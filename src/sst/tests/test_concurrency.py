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
import signal
import unittest

import testtools

from sst import (
    browsers,
    concurrency,
    results,
    runtests,
    tests,
)


class TestConcurrentSuite(testtools.TestCase):

    def run_test_concurrently(self, test, success):
        res = results.TextTestResult(StringIO(), verbosity=0)
        suite = unittest.TestSuite([test])
        # Run tests across 2 processes
        concurrent_suite = testtools.ConcurrentTestSuite(
            suite,
            concurrency.fork_for_tests(2)
        )
        res.startTestRun()
        concurrent_suite.run(res)
        res.stopTestRun()
        self.assertEqual(success, res.wasSuccessful())
        self.assertEqual(1, res.testsRun)
        return res

    def test_pass(self):
        res = self.run_test_concurrently(tests.get_case('pass'), True)
        self.assertEqual(0, len(res.errors))
        self.assertEqual(0, len(res.failures))

    def test_fail(self):
        res = self.run_test_concurrently(tests.get_case('fail'), False)
        self.assertEqual(0, len(res.errors))
        self.assertEqual(1, len(res.failures))

    def test_error(self):
        res = self.run_test_concurrently(tests.get_case('error'), False)
        self.assertEqual(1, len(res.errors))
        self.assertEqual(0, len(res.failures))

    def test_skip(self):
        res = self.run_test_concurrently(tests.get_case('skip'), True)
        self.assertEqual(0, len(res.errors))
        self.assertEqual(0, len(res.failures))
        reasons = res.skip_reasons
        self.assertEqual(1, len(reasons.keys()))
        reason, skipped = reasons.items()[0]
        self.assertEqual('', reason)
        self.assertEqual(1, len(skipped))
        self.assertEqual('sst.tests.Test.test_skip', skipped[0].id())

    def test_skip_reason(self):
        res = self.run_test_concurrently(tests.get_case('skip_reason'), True)
        self.assertEqual(0, len(res.errors))
        self.assertEqual(0, len(res.failures))
        reasons = res.skip_reasons
        self.assertEqual(1, len(reasons.keys()))
        reason, skipped = reasons.items()[0]
        self.assertEqual('Because', reason)
        self.assertEqual(1, len(skipped))
        self.assertEqual('sst.tests.Test.test_skip_reason', skipped[0].id())

    def test_expected_failure(self):
        res = self.run_test_concurrently(tests.get_case('expected_failure'),
                                         True)
        self.assertEqual(0, len(res.errors))
        self.assertEqual(0, len(res.failures))
        self.assertEqual(1, len(res.expectedFailures))

    def test_unexpected_success(self):
        res = self.run_test_concurrently(tests.get_case('unexpected_success'),
                                         False)
        self.assertEqual(0, len(res.errors))
        self.assertEqual(0, len(res.failures))
        self.assertEqual(1, len(res.unexpectedSuccesses))

    def test_killed(self):
        class Killed(unittest.TestCase):
            def test_killed(self):
                pid = os.getpid()
                os.kill(pid, signal.SIGKILL)

        res = self.run_test_concurrently(Killed('test_killed'), False)
        self.assertEqual(1, len(res.errors))
        self.assertEqual(0, len(res.failures))


class TestConcurrentRunTests(tests.ImportingLocalFilesTest):
    """Smoke integration tests at runtests level."""

    def test_pass(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
from sst import loaders
discover = loaders.discoverRegularTests

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
        runtests.runtests(
            ['^t'], 'no results directory used', out,
            concurrency_num=2,
            browser_factory=browsers.FirefoxFactory(),
        )

        output = out.getvalue()
        self.assertIn('Ran 2 tests', output)
        self.assertIn('OK', output)
        self.assertNotIn('FAIL', output)

    def test_fail(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
from sst import loaders
discover = loaders.discoverRegularTests

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
        runtests.runtests(
            ['^t'], 'no results directory used', out,
            concurrency_num=2,
            browser_factory=browsers.FirefoxFactory(),
        )
        output = out.getvalue()
        self.assertIn('Ran 2 tests', output)
        self.assertEqual(output.count('Traceback (most recent call last):'), 2)
        self.assertIn('FAILED (failures=2)', output)


class PartitionTestCase(testtools.TestCase):

    def setUp(self):
        super(PartitionTestCase, self).setUp()
        self.suite = unittest.TestSuite()
        self.suite.addTests([tests.get_case('pass') for i in range(8)])

    def test_partition_even_groups(self):
        parted_tests = concurrency.partition_tests(self.suite, 4)
        self.assertEqual(4, len(parted_tests))
        self.assertEqual(2, len(parted_tests[0]))
        self.assertEqual(2, len(parted_tests[1]))
        self.assertEqual(2, len(parted_tests[2]))
        self.assertEqual(2, len(parted_tests[3]))

    def test_partition_one_in_each(self):
        parted_tests = concurrency.partition_tests(self.suite, 8)
        self.assertEqual(8, len(parted_tests))
        self.assertEqual(1, len(parted_tests[0]))

    def test_partition_all_in_one(self):
        parted_tests = concurrency.partition_tests(self.suite, 1)
        self.assertEqual(1, len(parted_tests))
        self.assertEqual(8, len(parted_tests[0]))

    def test_partition_uneven(self):
        parted_tests = concurrency.partition_tests(self.suite, 3)
        self.assertEqual(3, len(parted_tests))
        self.assertEqual(3, len(parted_tests[0]))
        self.assertEqual(3, len(parted_tests[1]))
        self.assertEqual(2, len(parted_tests[2]))
