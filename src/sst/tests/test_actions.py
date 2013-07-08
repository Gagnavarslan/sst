#
#   Copyright (c) 2013 Canonical Ltd.
#
#   This file is part of: SST (selenium-simple-test)
#   https://launchpad.net/selenium-simple-test
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from cStringIO import StringIO
import logging
import random

import mock
import testtools
import time

from selenium.common import exceptions
from selenium.webdriver.remote import webelement
from sst import actions


class TestException(Exception):
    pass


class TestRetryOnException(testtools.TestCase):

    def setUp(self):
        super(TestRetryOnException, self).setUp()
        self.out = StringIO()
        # Capture output from retry_on_stale_element calls
        logger = logging.getLogger('SST')
        logger.addHandler(logging.StreamHandler(self.out))
        self.nb_calls = 0

    def raise_exception(self, exception=TestException, times=1):
        self.nb_calls += 1
        if self.nb_calls <= times:
            raise exception()
        return 'success'

    def assertRaisesOnlyOnce(self, expected, func, *args):
        # Calling the function succeeds
        self.assertEqual(expected, func(*args))
        # But under the hood it's been called twice
        self.assertEqual(2, self.nb_calls)
        # And we get some feedback about the exception
        self.assertIn(
            'Retrying after catching: ',
            self.out.getvalue())

    def test_retry_on_exception_sleeps_poll_time(self):
        @actions.retry_on_exception(TestException, retries=1)
        def protected_raiser():
            return self.raise_exception(times=1)

        poll_time = random.random()
        actions.set_wait_timeout(10, poll_time)
        with mock.patch('time.sleep') as mock_sleep:
            protected_raiser()

        mock_sleep.assert_called_once_with(poll_time)

    def test_retry_on_exception_fails_with_max_retries(self):
        max_retries = 1

        @actions.retry_on_exception(TestException, retries=max_retries)
        def protected_raiser():
            return self.raise_exception(times=max_retries + 1)

        self.assertRaises(TestException, protected_raiser)

    def test_retry_on_exception_fails_with_max_timeout(self):
        timeout = 0.5

        @actions.retry_on_exception(TestException)
        def protected_raiser():
            # It will have time to retry only once.
            time.sleep(timeout + 0.01)
            return self.raise_exception(times=2)

        actions.set_wait_timeout(timeout)
        self.assertRaises(TestException, protected_raiser)

    def test_retry_on_exception_only_once(self):
        """retry once on TestException."""
        @actions.retry_on_exception(TestException, retries=1)
        def protected_raiser():
            return self.raise_exception(times=1)

        self.assertRaisesOnlyOnce('success', protected_raiser)

    def test_wait_for_retries_on_stale_element(self):
        self.assertRaisesOnlyOnce(
            'success', actions.wait_for, self.raise_exception,
            exceptions.StaleElementReferenceException, 1)


class TestElementToString(testtools.TestCase):

    def _get_mock_element(self, identifier=None, text=None, value=None,
                          outer_html=None):
        def mock_get_attribute(attribute):
            values = {
                'id': identifier,
                'value': value,
                'outerHTML': outer_html
            }
            return values[attribute]
        element = mock.Mock(spec=webelement.WebElement, parent=None, id_=None)
        element.get_attribute.side_effect = mock_get_attribute
        type(element).text = mock.PropertyMock(return_value=text)
        return element

    def test_element_with_id(self):
        element = self._get_mock_element(identifier='Test id')
        self.assertEqual(actions._element_to_string(element), 'Test id')

    def test_element_without_id_with_text(self):
        element = self._get_mock_element(identifier=None, text='Test text')
        self.assertEqual(actions._element_to_string(element), 'Test text')

    def test_element_without_id_without_text_with_value(self):
        element = self._get_mock_element(
            identifier=None, text=None, value='Test value')
        self.assertEqual(actions._element_to_string(element), 'Test value')

    def test_element_without_id_without_text_without_value(self):
        element = self._get_mock_element(
            identifier=None, text=None, value=None, outer_html='<p></p>')
        self.assertEqual(
            actions._element_to_string(element), '<p></p>')


class TestBaseUrl(testtools.TestCase):

    def test_go_to(self):
        e = self.assertRaises(AssertionError, actions.go_to, '/')
        self.assertEqual('BASE_URL is not set, did you call set_base_url ?',
                         e.message)
