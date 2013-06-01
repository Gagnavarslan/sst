#
# to run:
#  $ ./selftest.py src/sst/tests/ -p test_concurrency.py
#

import sys
import unittest
from cStringIO import StringIO

from junitxml import JUnitXmlResult

from testtools import (
    ConcurrentTestSuite,
    MultiTestResult,
    TestCase,
)

from sst import (
    concurrency,
    result,
    tests,
)


def _make_test_suite(num_tests):
    """ generate a TestSuite with some number of identical TestCases.

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


class ConcurrencyTestCase(TestCase):

    def setUp(self):
        super(ConcurrencyTestCase, self).setUp()
        tests.set_cwd_to_tmp(self)

    def test_concurrent_forked(self):
        num_tests = 8
        concurrency_num = 4

        console_out = StringIO()
        xml_out = StringIO()
        txt_result = result.TextTestResult(console_out, verbosity=0)
        xml_result = JUnitXmlResult(xml_out)
        res = MultiTestResult(txt_result, xml_result)

        original_suite = _make_test_suite(num_tests)
        suite = ConcurrentTestSuite(
            original_suite,
            lambda suite: concurrency.fork_for_tests(suite, concurrency_num)
        )
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
