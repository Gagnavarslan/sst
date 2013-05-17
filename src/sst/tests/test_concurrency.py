import sys
import time
import threading
import unittest

import junitxml

from testtools import (
    ConcurrentTestSuite,
    iterate_tests,
    MultiTestResult,
    TestCase,
    ThreadsafeForwardingResult,
    )

import sst.result



def _make_test_suite(num_tests=10):
    
    def test_method(self):
        time.sleep(2.0)
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


class ConcurrentTestCase(TestCase):

    def split_suite(self, suite):
        return list(iterate_tests(suite))

    def test_concurrent_all_at_once_text_result(self):
        num_tests = 50
        original_suite = _make_test_suite(num_tests=50)
        result = sst.result.TextTestResult(sys.stdout, verbosity=0)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)

    def test_concurrent_all_at_once_xml_result(self):
        num_tests = 50
        original_suite = _make_test_suite(num_tests=50)
        xml_stream = file('results.xml', 'wb')
        result = junitxml.JUnitXmlResult(xml_stream)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        result.stopTestRun()
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)

    def test_concurrent_all_at_once_multi_result(self):
        num_tests = 50
        original_suite = _make_test_suite(num_tests=50)
        txt_result = sst.result.TextTestResult(sys.stdout, verbosity=1)
        xml_stream = file('results.xml', 'wb')
        xml_result = junitxml.JUnitXmlResult(xml_stream)
        result = MultiTestResult(txt_result, xml_result)
        suite = ConcurrentTestSuite(original_suite, self.split_suite)
        suite.run(result)
        result.stopTestRun()
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.testsRun, num_tests)
       