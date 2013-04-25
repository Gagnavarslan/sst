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


import os
import re
import sys
import unittest
from cStringIO import StringIO

import testtools

from sst import (
    htmlrunner,
    tests
)


def _make_test_suite():
    """create a suite of tests so we have something to load and run."""
    class TruthyTestCase(unittest.TestCase):

        def test_true(self):
            pass

        def test_false(self):
            pass

    suite = unittest.TestSuite()
    suite.addTest(TruthyTestCase('test_true'))
    suite.addTest(TruthyTestCase('test_false'))
    return suite


class TestHtmlRunner(testtools.TestCase):

    def setUp(self):
        super(TestHtmlRunner, self).setUp()
        tests.set_cwd_to_tmp(self)
        # capture test output so we don't pollute the test runs
        self.out = StringIO()
        self.patch(sys, 'stdout', self.out)

    def test_html_output(self):
        suite = _make_test_suite()
        self.assertEqual(suite.countTestCases(), 2)

        report_filename = 'report.html'

        # create a runner and run the tests
        fp = file(report_filename, 'wb')
        runner = htmlrunner.HTMLTestRunner(
            stream=fp,
            title='My Unit Test',
            description='Test Description',
            verbosity=0
        )
        runner.run(suite)
        # Close file handle so output flushes before asserting content.
        fp.close()

        self.assertIn(report_filename, os.listdir(self.test_base_dir))
        with open(report_filename) as f:
            content = f.read()
        self.assertGreater(len(content), 0)
        regex = re.compile(r'.*<html?.*</html?', re.DOTALL)
        self.assertRegexpMatches(content, regex)
