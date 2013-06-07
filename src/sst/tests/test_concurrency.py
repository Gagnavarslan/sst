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
import sys
import unittest

from junitxml import JUnitXmlResult

from testtools import (
    ConcurrentTestSuite,
    MultiTestResult,
    TestCase,
)

from sst import (
    browsers,
    concurrency,
    result,
    runtests,
    tests,
)


def _make_allpass_test_suite(num_tests):
    """ Generate a TestSuite with a number of identical TestCases.

    This is used for generating test data."""

    # Every method generated will have this body
    def test_method(self):
        self.assertTrue(True)

    # Create a dict of test methods, sequentially named
    d = {}
    for i in range(num_tests):
        d['test_method%i' % i] = test_method

    # Generate a Class with the created methods
    SampleTestCase = type('SampleTestCase', (TestCase,), d)

    # Make a sequence of test_cases from the test methods
    test_cases = [
        SampleTestCase('test_method%i' % i)
        for i in range(num_tests)
    ]
    return unittest.TestSuite(test_cases)


class ConcurrencyForkedTestCase(TestCase):

    def setUp(self):
        super(ConcurrencyForkedTestCase, self).setUp()
        tests.set_cwd_to_tmp(self)

    def test_concurrent_forked(self):
        num_tests = 8
        concurrency_num = 4

        console_out = StringIO()
        xml_out = StringIO()
        txt_result = result.TextTestResult(console_out, verbosity=0)
        xml_result = JUnitXmlResult(xml_out)
        res = MultiTestResult(txt_result, xml_result)

        original_suite = _make_allpass_test_suite(num_tests)
        suite = ConcurrentTestSuite(
            original_suite,
            concurrency.fork_for_tests(concurrency_num)
        )
        res.startTestRun()
        suite.run(res)
        res.stopTestRun()

        # Check the result
        self.assertTrue(res.wasSuccessful())
        self.assertEqual(res.errors, [])
        self.assertEqual(res.testsRun, num_tests)

        # Check the xml output
        xml_lines = xml_out.getvalue().splitlines()
        # xml file has a line for each case + header + footer
        self.assertEqual(len(xml_lines), num_tests + 2)


class ConcurrencyRunTestCase(tests.ImportingLocalFilesTest):

    def setUp(self):
        super(ConcurrencyRunTestCase, self).setUp()

    def test_runtests_concurrent_allpass(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
from sst import loader
discover = loader.discoverRegularTests

file: t/test_conc1.py
import unittest
class Test1(unittest.TestCase):
    def test_pass_1(self):
        self.assertTrue(True)

file: t/test_conc2.py
import unittest
class Test2(unittest.TestCase):
    def test_pass_2(self):
        self.assertTrue(True)
''')

        out = StringIO()
        failures = runtests.runtests(
            ['^t'], 'no results directory used', out,
            concurrency_num=2,
            browser_factory=browsers.FirefoxFactory(),
        )

        output = out.getvalue()
        lines = output.splitlines()
        self.assertEqual('Tests running...', lines[0])
        self.assertIn('Ran 2 tests', output)
        self.assertIn('OK', output)
        self.assertNotIn('FAIL', output)

    def test_runtests_concurrent_withfails(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
from sst import loader
discover = loader.discoverRegularTests

file: t/test_pass.py
import unittest
class TestPass(unittest.TestCase):
    def test_me(self):
        self.assertTrue(True)

file: t/test_fail1.py
import unittest
class TestFail1(unittest.TestCase):
    def test_fail_1(self):
        self.assertTrue(False)

file: t/test_fail2.py
import unittest
class TestFail2(unittest.TestCase):
    def test_fail_2(self):
        self.assertTrue(False)
''')

        out = StringIO()
        failures = runtests.runtests(
            ['^t'], 'no results directory used', out,
            concurrency_num=2,
            browser_factory=browsers.FirefoxFactory(),
        )
        output = out.getvalue()
        lines = output.splitlines()
        self.assertEqual('Tests running...', lines[0])
        self.assertIn('Ran 3 tests', output)
        self.assertIn('OK', output)
        self.assertEqual(output.count('Traceback (most recent call last):'), 2)
        self.assertIn('FAILED (failures=2)', output)
