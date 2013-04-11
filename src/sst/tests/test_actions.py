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

import mock
import testtools

from sst import actions


class TestRetryOnStale(testtools.TestCase):

    def setUp(self):
        super(TestRetryOnStale, self).setUp()
        self.out = StringIO()
        # Capture output from retry_on_stale_element calls
        logger = logging.getLogger('SST')
        logger.addHandler(logging.StreamHandler(self.out))
        self.nb_calls = 0

    def raise_stale_element(self):
        self.nb_calls += 1
        if self.nb_calls == 1:
            raise actions.StaleElementReferenceException('whatever')
        return 'success'

    def assertRaisesOnlyOnce(self, expected, func, *args):
        # Calling the function succeeds
        self.assertEqual(expected, func(*args))
        # But under the hood it's been called twice
        self.assertEqual(2, self.nb_calls)
        # And we get some feedback about the exception
        self.assertIn(
            'Retrying after catching: StaleElementReferenceException()',
            self.out.getvalue())

    def test_retry_on_stale_only_once(self):
        """retry once on StaleElementReferenceException."""
        @actions.retry_on_stale_element
        def protected_raiser():
            return self.raise_stale_element()

        self.assertRaisesOnlyOnce('success', protected_raiser)

    def test_wait_for_retries(self):
        self.assertRaisesOnlyOnce(None, actions.wait_for,
                                  self.raise_stale_element)


class TestElementToString(testtools.TestCase):

    def test_element_with_id(self):
        element = self._get_element_with_id(element_id='Test id')
        self.assertEqual('Test id', actions._element_to_string(element))

    def _get_element_with_id(self, element_id):
        element = mock.Mock()
        def mock_get_attribute(attribute):
            if attribute == 'id':
                return element_id
        element.get_attribute.side_effect = mock_get_attribute
        return element

    def test_element_without_id_with_text(self):
        element = self._get_element_without_id_with_text(text='Test text')
        self.assertEqual('Test text', actions._element_to_string(element))

    def _get_element_without_id_with_text(self, text):
        element = mock.Mock()
        element.get_attribute.return_value = None
        element.text = text
        return element

    def test_element_without_id_without_text(self):
        element = self._get_element_without_id_without_text(tag='p')
        self.assertEqual(
            '<p></p>', actions._element_to_string(element))

    def _get_element_without_id_without_text(self, tag):
        element = mock.Mock()
        def mock_get_attribute(attribute):
            values = {
                'id': None,
                'value': None,
                'outerHTML': '<{0}></{0}>'.format(tag)
            }
            return values[attribute]
        element.get_attribute.side_effect = mock_get_attribute
        element.text = None
        return element
