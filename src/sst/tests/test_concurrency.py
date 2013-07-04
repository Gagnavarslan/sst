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
    loader,
    result,
    runtests,
    tests,
)


class ConcurrencyTestCase(tests.ImportingLocalFilesTest):

    def run_tests_concurrently(self, suite):
        txt_result = result.TextTestResult(StringIO(), verbosity=0)
        # Run tests across 2 processes
        concurrent_suite = ConcurrentTestSuite(
            suite,
            concurrency.fork_for_tests(2)
        )
        txt_result.startTestRun()
        concurrent_suite.run(txt_result)
        txt_result.stopTestRun()
        return txt_result

    def test_forked_all_pass(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_pass.py
import unittest
class BothPass(unittest.TestCase):
    def test_pass_1(self):
        self.assertTrue(True)
    def test_pass_2(self):
        self.assertTrue(True)
''')
        suite = loader.TestLoader().discover('t', pattern='test_pass.py')
        result = self.run_tests_concurrently(suite)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.testsRun, suite.countTestCases())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
        self.assertEqual(result.skipped, [])

    def test_forked_with_error(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_error.py
import unittest
class OneError(unittest.TestCase):
    def test_error(self):
        raise Exception('ouch')
    def test_pass(self):
        self.assertTrue(True)
''')
        suite = loader.TestLoader().discover('t', pattern='test_error.py')
        result = self.run_tests_concurrently(suite)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.testsRun, suite.countTestCases())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(len(result.skipped), 0)

    def test_forked_with_fail(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_fail.py
import unittest
class OneFail(unittest.TestCase):
    def test_fail(self):
        self.assertTrue(False)
    def test_pass(self):
        self.assertTrue(True)
''')
        suite = loader.TestLoader().discover('t', pattern='test_fail.py')
        result = self.run_tests_concurrently(suite)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.testsRun, suite.countTestCases())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(len(result.skipped), 0)

    def test_forked_with_skip(self):
        class Skip(unittest.TestCase):
            def test_skip(self):
                self.skipTest('Because')
        suite = unittest.TestSuite()
        suite.addTest(Skip('test_skip'))
        result = self.run_tests_concurrently(suite)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.testsRun, suite.countTestCases())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        reasons = result.skip_reasons
        self.assertEqual(1, len(reasons.keys()))
        reason, tests = reasons.items()[0]
        # subunit adds a spurious \n
        self.assertEqual('Because\n', reason)
        self.assertEqual(1, len(tests))
        self.assertEqual('sst.tests.test_concurrency.Skip.test_skip',
                         tests[0].id())

    def test_forked_with_dead_subprocess(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_kill.py
import os
import signal
import unittest
class OneKilled(unittest.TestCase):
    def test_killed(self):
        pid = os.getpid()
        os.kill(pid, signal.SIGKILL)
    def test_pass(self):
        self.assertTrue(True)
''')
        suite = loader.TestLoader().discover('t', pattern='test_kill.py')
        result = self.run_tests_concurrently(suite)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.testsRun, suite.countTestCases())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(len(result.skipped), 0)


def _make_allpass_test_suite(num_tests):
    """Generate a TestSuite with a number of identical TestCases.

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


class PartitionTestCase(tests.ImportingLocalFilesTest):

    def setUp(self):
        super(PartitionTestCase, self).setUp()
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_partitions.py
import unittest
class SampleTestCase(unittest.TestCase):
    def test_pass_1(self):
        self.assertTrue(True)
    def test_pass_2(self):
        self.assertTrue(True)
    def test_pass_3(self):
        self.assertTrue(True)
    def test_pass_4(self):
        self.assertTrue(True)
    def test_pass_5(self):
        self.assertTrue(True)
    def test_pass_6(self):
        self.assertTrue(True)
    def test_pass_7(self):
        self.assertTrue(True)
    def test_pass_8(self):
        self.assertTrue(True)
''')

    def test_partition_even_groups(self):
        suite = loader.TestLoader().discover('t')
        parted_tests = concurrency.partition_tests(suite, 4)
        self.assertEqual(len(parted_tests), 4)
        self.assertEqual(len(parted_tests[0]), 2)
        self.assertEqual(len(parted_tests[1]), 2)

    def test_partition_one_in_each(self):
        suite = loader.TestLoader().discover('t')
        parted_tests = concurrency.partition_tests(suite, 8)
        self.assertEqual(len(parted_tests), 8)
        self.assertEqual(len(parted_tests[0]), 1)

    def test_partition_all_in_one(self):
        suite = loader.TestLoader().discover('t')
        parted_tests = concurrency.partition_tests(suite, 1)
        self.assertEqual(len(parted_tests), 1)
        self.assertEqual(len(parted_tests[0]), 8)
