#
# work in progress
# - concurrency strategies for parallel test case runner
#
#
# to run:
#  $ ./selftest.py src/sst/tests/ -p test_concurrency.py
#

import sys
import unittest
from cStringIO import StringIO

import junitxml

from testtools import (
    ConcurrentTestSuite,
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
        import time
        from selenium import webdriver
        driver = webdriver.Firefox()
        time.sleep(5.0)
        driver.quit()
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

    def test_concurrent_forked(self):
        num_tests = 8

        console_out = StringIO()
        xml_out = StringIO()
        txt_result = sst.result.TextTestResult(console_out, verbosity=0)
        xml_result = junitxml.JUnitXmlResult(xml_out)
        result = MultiTestResult(txt_result, xml_result)

        original_suite = _make_test_suite(num_tests)
        suite = ConcurrentTestSuite(
            original_suite,
            sst.concurrency.fork_for_tests
        )
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
