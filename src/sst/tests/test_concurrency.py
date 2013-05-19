#
# work in progress
# - concurrency strategies for parallel test case runner


import sys
import time
import threading
import unittest
from cStringIO import StringIO

import junitxml

from testtools import (
    ConcurrentTestSuite,
    iterate_tests,
    MultiTestResult,
    TestCase,
    ThreadsafeForwardingResult,
    )

import sst.result
import sst.tests


def _make_test_suite(num_tests):
    
    def test_method(self):
        time.sleep(0.5)
        self.assertTrue(True)

    d = {}
    for i in range(num_tests):
        d['test_method%i' % i] = test_method
    SampleTestCase = type('SampleTestCase', (TestCase,), d)
    test_cases = [
        SampleTestCase('test_method%i' % i)
        for i in range(num_tests)
    ]
    return unittest.TestSuite(test_cases)


class ConcurrencyTestCase(TestCase):

    def setUp(self):
        super(ConcurrencyTestCase, self).setUp()
        sst.tests.set_cwd_to_tmp(self)

    def split_suite(self, suite):
        return list(iterate_tests(suite))

    def group_cases(self, tests, group_size):
        suite_groups = []
        for i in xrange(0, len(list(tests)), group_size):
            suite_groups.append(unittest.TestSuite(tests[i:i+group_size]))
        return suite_groups
            
    def test_concurrent_all_at_once_text_result(self):
        num_tests = 50
        original_suite = _make_test_suite(num_tests)
        out = StringIO()
        result = sst.result.TextTestResult(out, verbosity=0)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)

    def test_concurrent_all_at_once_xml_result(self):
        num_tests = 50
        original_suite = _make_test_suite(num_tests)
        out = StringIO()
        result = junitxml.JUnitXmlResult(out)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        result.stopTestRun()
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)

    def test_concurrent_all_at_once_multi_result(self):
        num_tests = 50
        original_suite = _make_test_suite(num_tests)
        out = StringIO()
        txt_result = sst.result.TextTestResult(out, verbosity=1)
        xml_result = junitxml.JUnitXmlResult(out)
        result = MultiTestResult(txt_result, xml_result)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        result.stopTestRun()
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)

    def test_concurrent_even_groups_text_result(self):
        num_tests = 50
        group_size = 25  # number of tests in each sub_suite
        original_suite = _make_test_suite(num_tests)
        sub_suites = self.group_cases(list(iterate_tests(original_suite)), group_size)
        results = []
        for sub_suite in sub_suites:
            suite = ConcurrentTestSuite(sub_suite, self.split_suite)
            result = sst.result.TextTestResult(sys.stdout, verbosity=1)
            suite.run(result)
            results.append(result)
        for result in results:
            self.assertTrue(result.wasSuccessful())
            self.assertEqual(result.errors, [])
            self.assertEqual(result.testsRun, group_size)

    def test_concurrent_even_groups_multi_result(self):
        num_tests = 50
        group_size = 25  # number of tests in each sub_suite
        original_suite = _make_test_suite(num_tests)
        sub_suites = self.group_cases(list(iterate_tests(original_suite)), group_size)
        results = []
        for sub_suite in sub_suites:
            suite = ConcurrentTestSuite(sub_suite, self.split_suite)
            result = sst.result.TextTestResult(sys.stdout, verbosity=1)
            suite.run(result)
            results.append(result)
        for result in results:
            self.assertTrue(result.wasSuccessful())
            self.assertEqual(result.errors, [])
            self.assertEqual(result.testsRun, group_size)
