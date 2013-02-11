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
