import sys
import time
import threading
import unittest

import sst.result

from testtools import (
    ConcurrentTestSuite,
    iterate_tests,
    TestCase,
    ThreadsafeForwardingResult,
    )


def _make_test_suite():
    num_testcases = 40

    def test_method(self):
        time.sleep(2.0)
        self.assertTrue(True)

    d = {}
    for i in range(num_testcases):
        d['test_method%i' % i] = test_method
    SampleTestCase = type('SampleTestCase', (TestCase,), d)
    test_cases = [
        SampleTestCase('test_method%i' % i)
        for i in range(num_testcases)
    ]
    return unittest.TestSuite(test_cases)


class ConcurrentTestCase(TestCase):

    def split_suite(self, suite):
        return list(iterate_tests(suite))

    def test_concurrent(self):
        tests_batch = _make_test_suite()
        txt_result = sst.result.TextTestResult(sys.stdout, verbosity=2)
        result = ThreadsafeForwardingResult(
                                            txt_result,
                                            threading.Semaphore(value=1),
                                           )
        suite = ConcurrentTestSuite(tests_batch, self.split_suite)
        suite.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.errors, [])
