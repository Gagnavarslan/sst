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


from cStringIO import StringIO
import os
import sys

import testtools

from testtools import matchers

from sst import (
    cases,
    tests,
)


class SSTStringTestCase(cases.SSTScriptTestCase):

    xserver_headless = True

    def __init__(self, code='pass'):
        super(SSTStringTestCase, self).__init__('ignored_dir', 'ignored_name')
        self.script_code = code

    def setUp(self):
        # We don't need to compile the script because we have already define
        # the code to execute.
        self._compile_script = lambda: None
        self.code = compile(self.script_code + '\n', '<string>', 'exec')
        super(SSTStringTestCase, self).setUp()


class TestContext(testtools.TestCase):

    def test_test_case_without_context(self):
        # Use the default context value.
        test = SSTStringTestCase('ignored')
        test.script_code = 'assert True'
        result = testtools.TestResult()
        test.run(result)
        self.assertTrue(result.wasSuccessful())


class TestScreenShotsAndPageDump(testtools.TestCase):

    def setUp(self):
        super(TestScreenShotsAndPageDump, self).setUp()
        tests.set_cwd_to_tmp(self)
        # capture test output so we don't pollute the test runs
        self.out = StringIO()
        self.patch(sys, 'stdout', self.out)

    def run_failing_test(self, test):
        result = testtools.TestResult()
        test.run(result)
        self.assertEqual(0, len(result.errors))
        self.assertEqual(1, len(result.failures))

    def test_screenshot_and_page_dump_enabled(self):
        test = SSTStringTestCase('ignored')
        test.script_code = 'assert False'
        test.screenshots_on = True
        test.results_directory = 'results'
        self.run_failing_test(test)
        # We get a screenshot and a pagesource
        self.assertTrue(os.path.exists('results'))
        files = sorted(os.listdir('results'))
        self.assertEqual(2, len(files))

        def byte_size(f):
            return os.path.getsize(os.path.join(test.results_directory, f))

        self.assertGreater(byte_size(files[0]), 0)
        self.assertGreater(byte_size(files[1]), 0)
        self.assertThat(files[0], matchers.StartsWith('pagesource-'))
        self.assertThat(files[1], matchers.StartsWith('screenshot-'))

    def test_screenshot_and_page_dump_disabled(self):
        test = SSTStringTestCase('ignored')
        test.script_code = 'assert False'
        test.screenshots_on = False
        test.results_directory = 'results'
        self.run_failing_test(test)
        # No screenshot required, no files, not even a directory
        self.assertFalse(os.path.exists('results'))
