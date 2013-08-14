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
#


import testtools

from sst import (
    cases,
    config,
    tests,
)


class TestSSTScriptTestCase(testtools.TestCase):

    def setUp(self):
        super(TestSSTScriptTestCase, self).setUp()
        self.test = cases.SSTScriptTestCase('dir', 'foo.py')

    def test_id(self):
        """The test id mentions the python class path and the test name."""
        # FIXME: This is a minimal test to cover http://pad.lv/1087606, it
        # would be better to check a results.xml file but we don't have the
        # test infrastructure for that (yet) -- vila 2012-12-07
        self.assertEqual('dir.foo', self.test.id())


class TestSSTTestCase(testtools.TestCase):

    def setUp(self):
        super(TestSSTTestCase, self).setUp()
        tests.set_cwd_to_tmp(self)
        self.test = tests.SSTBrowserLessTestCase('run')
        self.result = testtools.TestResult()
        self.test.run(self.result)

    def test_results(self):
        result = self.result
        self.assertEqual(result.testsRun, 1)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
        self.assertEqual(result.skipped, [])

    def test_attributes(self):
        test = self.test
        self.assertEqual(test._testMethodName, 'run')
        self.assertIsNone(test.base_url)
        self.assertFalse(test.screenshots_on)
        self.assertEqual(test.wait_poll, 0.1)
        self.assertEqual(test.wait_timeout, 10)
        self.assertEqual(test.id(), 'sst.tests.SSTBrowserLessTestCase.run')

    def test_config(self):
        self.assertIsNone(config._current_context)
        self.assertEqual(config.browser_type, 'firefox')
        self.assertEqual(config.cache, {})
        self.assertEqual(config.flags, [])
        self.assertIs(None, config.results_directory)
