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
import unittest
from cStringIO import StringIO

import junitxml
import testtools

from sst import (
    tests,
    runtests,
)


def _make_pass_test_suite():
    class InnerPassTestCase(unittest.TestCase):
        def test_inner_pass(self):
            self.assertTrue(True)
    suite = unittest.TestSuite()
    suite.addTest(InnerPassTestCase('test_inner_pass'))
    return suite


def _make_fail_test_suite():
    class InnerFailTestCase(unittest.TestCase):
        def test_inner_fail(self):
            self.assertTrue(False)
    suite = unittest.TestSuite()
    suite.addTest(InnerFailTestCase('test_inner_fail'))
    return suite


def _make_error_test_suite():
    class InnerErrorTestCase(unittest.TestCase):
        def test_inner_error(self):
            raise
    suite = unittest.TestSuite()
    suite.addTest(InnerErrorTestCase('test_inner_error'))
    return suite


def _make_skip_test_suite():
    class InnerSkipTestCase(unittest.TestCase):
        @testtools.skip('skip me')
        def test_inner_skip(self):
            pass
    suite = unittest.TestSuite()
    suite.addTest(InnerSkipTestCase('test_inner_skip'))
    return suite


class ConsoleOutputTestCase(testtools.TestCase):

    def setUp(self):
        super(ConsoleOutputTestCase, self).setUp()
        tests.set_cwd_to_tmp(self)
        self.out = StringIO()
        self.text_result = runtests.TextTestResult(self.out)

    def execute_test(self, suite, regex):
        suite.run(self.text_result)
        self.console_output = self.out.getvalue()
        self.assertRegexpMatches(self.console_output, regex)

    def test_text_output_pass(self):
        suite = _make_pass_test_suite()
        regex = \
            r'test_inner_pass ' \
            r'\(sst.tests.test_results_output.InnerPassTestCase\) ...' \
            r'\nOK \([0-9]*.[0-9]{3} secs\)\n\n'
        self.execute_test(suite, regex)

    def test_text_output_fail(self):
        suite = _make_fail_test_suite()
        regex = \
            r'test_inner_fail ' \
            r'\(sst.tests.test_results_output.InnerFailTestCase\) ...' \
            r'\nFAIL\n\n'
        self.execute_test(suite, regex)

    def test_text_output_error(self):
        suite = _make_error_test_suite()
        regex = \
            r'test_inner_error ' \
            r'\(sst.tests.test_results_output.InnerErrorTestCase\) ...' \
            r'\nERROR\n\n'
        self.execute_test(suite, regex)

    def test_text_output_skip(self):
        suite = _make_skip_test_suite()
        regex = \
            r'test_inner_skip ' \
            r'\(sst.tests.test_results_output.InnerSkipTestCase\) ...' \
            r'\nSkipped \'skip me\'\n\n'
        self.execute_test(suite, regex)


class XmlOutputTestCase(testtools.TestCase):

    def setUp(self):
        super(XmlOutputTestCase, self).setUp()
        tests.set_cwd_to_tmp(self)
        self.results_file = 'results.xml'
        self.xml_stream = file(self.results_file, 'wb')
        self.xml_result = junitxml.JUnitXmlResult(self.xml_stream)
        self.addCleanup(os.remove, 'results.xml')

    def execute_test(self, suite, regex):
        suite.run(self.xml_result)
        self.xml_result.stopTestRun()
        self.xml_stream.close()
        self.assertIn(self.results_file, os.listdir(self.test_base_dir))
        with open(self.results_file) as f:
            content = f.read()
        self.assertGreater(len(content), 0)

    def test_xml_output_pass(self):
        suite = _make_pass_test_suite()
        regex = \
            r'<testsuite errors="0" failures="0" name="" tests="1" ' \
            r'time=".*">\n' \
            r'<testcase ' \
            r'classname="sst.tests.test_results_output.InnerPassTestCase" ' \
            r'name="test_inner_pass" time="[0-9]*.[0-9]{3}"'
        self.execute_test(suite, regex)

    def test_xml_output_fail(self):
        suite = _make_fail_test_suite()
        regex = \
            r'<testsuite errors="0" failures="1" name="" tests="1" ' \
            r'time=".*">\n' \
            r'<testcase ' \
            r'classname="sst.tests.test_results_output.InnerFailTestCase" ' \
            r'name="test_inner_fail" time="[0-9]*.[0-9]{3}"'
        self.execute_test(suite, regex)

    def test_xml_output_error(self):
        suite = _make_error_test_suite()
        regex = \
            r'<testsuite errors="1" failures="0" name="" tests="1" ' \
            r'time=".*">\n' \
            r'<testcase ' \
            r'classname="sst.tests.test_results_output.InnerErrorTestCase" ' \
            r'name="test_inner_error" time="[0-9]*.[0-9]{3}"'
        self.execute_test(suite, regex)

    def test_xml_output_skip(self):
        suite = _make_skip_test_suite()
        regex = \
            r'<testsuite errors="0" failures="0" name="" tests="1" ' \
            r'time=".*">\n<testcase classname="sst.tests.' \
            r'test_results_output.InnerSkipTestCase" ' \
            r'name="test_inner_skip" time="[0-9]*.[0-9]{3}"' \
            r'>\n<skipped>skip me</skipped>\n</testcase>\n</testsuite>'
        self.execute_test(suite, regex)
