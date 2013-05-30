#
# work in progress
# - concurrency strategies for parallel test case runner
#
#
# to run:
#  $ nosetests -v -m test_concurrent*
#

import Queue
import sys
import threading
import unittest
from cStringIO import StringIO

import junitxml

from testtools import (
    ConcurrentTestSuite,
    iterate_tests,
    MultiTestResult,
    TestCase,
)

import sst.concurrency
import sst.result
import sst.tests


def _make_test_suite(num_tests):
    """ generate a TestSuite with some number of identical TestCases.

    This is used for generating test data."""

    # Every method generated will have this body
    def test_method(self):
        #from selenium import webdriver
        #driver = webdriver.Firefox()
        #driver.quit()
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


class ConcurrencyTestCase(TestCase):

    def setUp(self):
        super(ConcurrencyTestCase, self).setUp()
        sst.tests.set_cwd_to_tmp(self)
        self.addCleanup(self.restore_stdout)

    def restore_stdout(self):
        sys.stdout = sys.__stdout__

    def split_suite(self, suite):
        return list(iterate_tests(suite))

    def group_cases(self, tests, group_size):
        suite_groups = []
        for i in xrange(0, len(list(tests)), group_size):
            suite_groups.append(unittest.TestSuite(tests[i:i + group_size]))
        return suite_groups

    def test_concurrent_all_at_once_text_result(self):
        num_tests = 4
        original_suite = _make_test_suite(num_tests)
        out = StringIO()
        result = sst.result.TextTestResult(out, verbosity=0)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)

    def test_concurrent_all_at_once_xml_result(self):
        num_tests = 4
        original_suite = _make_test_suite(num_tests)
        out = StringIO()
        result = junitxml.JUnitXmlResult(out)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        result.stopTestRun()
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)
        xml_lines = out.getvalue().splitlines()
        # xml file has a line for each case + header + footer
        self.assertEqual(len(xml_lines), num_tests + 2)

    def test_concurrent_all_at_once_multi_result(self):
        num_tests = 8
        original_suite = _make_test_suite(num_tests)
        txt_result = sst.result.TextTestResult(sys.stdout, verbosity=0)
        out = StringIO()
        xml_result = junitxml.JUnitXmlResult(out)
        result = MultiTestResult(txt_result, xml_result)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        result.stopTestRun()
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)
        xml_lines = out.getvalue().splitlines()
        # xml file has a line for each case + header + footer
        self.assertEqual(len(xml_lines), num_tests + 2)

    def test_concurrent_even_groups_text_result(self):
        num_tests = 8
        group_size = 2  # number of tests in each sub_suite
        original_suite = _make_test_suite(num_tests)
        sub_suites = self.group_cases(
            self.split_suite(original_suite),
            group_size,
        )
        result = sst.result.TextTestResult(sys.stdout, verbosity=0)
        for sub_suite in sub_suites:
            suite = ConcurrentTestSuite(sub_suite, self.split_suite)
            suite.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)

    def test_concurrent_even_groups_multi_result(self):
        num_tests = 8
        group_size = 2  # Number of tests in each sub_suite

        original_suite = _make_test_suite(num_tests)
        sub_suites = self.group_cases(
            self.split_suite(original_suite),
            group_size,
        )
        txt_result = sst.result.TextTestResult(sys.stdout, verbosity=0)
        out = StringIO()
        xml_result = junitxml.JUnitXmlResult(out)
        result = MultiTestResult(txt_result, xml_result)
        for sub_suite in sub_suites:
            suite = ConcurrentTestSuite(sub_suite, self.split_suite)
            suite.run(result)
        result.stopTestRun()
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)
        xml_lines = out.getvalue().splitlines()
        # xml file has a line for each case + header + footer
        self.assertEqual(len(xml_lines), num_tests + 2)

    def test_concurrent_one_case_per_threaded_worker(self):

        def runner_worker(task_queue):
            """Get from input queue, and run each test, until empty."""
            while True:
                try:
                    single_case_suite, result = task_queue.get(False)
                    # Run the test
                    single_case_suite.run(result)
                except Queue.Empty:
                    break

        num_tests = 16
        num_workers = 4  # number of worker threads to spawn

        # Genereate a unittest suite to run
        original_suite = _make_test_suite(num_tests)

        # Create results and streams.
        txt_result = sst.result.TextTestResult(sys.stdout, verbosity=0)
        out = StringIO()
        xml_result = junitxml.JUnitXmlResult(out)
        result = MultiTestResult(txt_result, xml_result)

        # Split the suite into sub suites with one TestCase in each
        split_suites = self.split_suite(original_suite)

        suites = [ConcurrentTestSuite(s, lambda s: s) for s in split_suites]

        # Create queue for feeding test suites to workers
        task_queue = Queue.Queue()

        # Queue up tasks
        for single_case_suite in suites:
            task_queue.put((single_case_suite, result))

        # Start workers
        threads = []
        for _ in xrange(num_workers):
            t = threading.Thread(target=runner_worker, args=(task_queue,))
            t.start()
            threads.append(t)

        # Wait on workers
        for t in threads:
            t.join()

        # Stop populating results
        result.stopTestRun()

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)
        xml_lines = out.getvalue().splitlines()
        # xml file has a line for each case + header + footer
        self.assertEqual(len(xml_lines), num_tests + 2)

    def test_concurrent_even_groups_multi_result_forked(self):
        num_tests = 8

        console_out = StringIO()
        xml_out = StringIO()
        txt_result = sst.result.TextTestResult(console_out, verbosity=2)
        xml_result = junitxml.JUnitXmlResult(xml_out)
        result = MultiTestResult(txt_result, xml_result)

        original_suite = _make_test_suite(num_tests)
        suite = ConcurrentTestSuite(
            original_suite,
            sst.concurrency.fork_for_tests
        )
        #result.startTestRun()
        suite.run(result)
        result.stopTestRun()

        # Check the result
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)

        # Check the xml output
        xml_lines = xml_out.getvalue().splitlines()
        # xml file has a line for each case + header + footer
        self.assertEqual(len(xml_lines), num_tests + 2)
