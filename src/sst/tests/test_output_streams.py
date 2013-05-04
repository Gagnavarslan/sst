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
import re
import unittest
from cStringIO import StringIO

import junitxml
import testtools

import sst


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


class OutputTestCase(testtools.TestCase):

    def setUp(self):
        super(OutputTestCase, self).setUp()
        sst.tests.set_cwd_to_tmp(self)
        self.out = StringIO()

    def test_text_output_pass(self):
        suite = _make_pass_test_suite()
        text_result = sst.runtests.TextTestResult(self.out)
        suite.run(text_result)
        self.console_output = self.out.getvalue()
        regex_expected = \
            r'test_inner_pass ' + \
            r'\(sst.tests.test_output_streams.InnerPassTestCase\) ...' + \
            r'\nOK \([0-9]*.[0-9]{3} secs\)\n\n'
        self.assertRegexpMatches(self.console_output, regex_expected)

    def test_text_output_fail(self):
        suite = _make_fail_test_suite()
        text_result = sst.runtests.TextTestResult(self.out)
        suite.run(text_result)
        self.console_output = self.out.getvalue()
        regex_expected = \
            r'test_inner_fail ' + \
            '\(sst.tests.test_output_streams.InnerFailTestCase\) ...' + \
            r'\nFAIL\n\n'
        self.assertRegexpMatches(self.console_output, regex_expected)

    def test_text_output_error(self):
        suite = _make_error_test_suite()
        text_result = sst.runtests.TextTestResult(self.out)
        suite.run(text_result)
        self.console_output = self.out.getvalue()
        regex_expected = \
            r'test_inner_error ' + \
            '\(sst.tests.test_output_streams.InnerErrorTestCase\) ...' + \
            r'\nERROR\n\n'
        self.assertRegexpMatches(self.console_output, regex_expected)

    def test_xml_output_pass(self):
        suite = _make_pass_test_suite()
        results_file = 'results.xml'
        xml_stream = file(results_file, 'wb')
        xml_result = junitxml.JUnitXmlResult(xml_stream)
        suite.run(xml_result)
        xml_result.stopTestRun()
        xml_stream.close()
        self.assertIn(results_file, os.listdir(self.test_base_dir))
        with open(results_file) as f:
            content = f.read()
        self.assertGreater(len(content), 0)
        regex = r'<testsuite errors="0" failures="0" name="" tests="1" .*'
        self.assertRegexpMatches(content, regex)

    def test_xml_output_fail(self):
        suite = _make_fail_test_suite()
        results_file = 'results.xml'
        xml_stream = file(results_file, 'wb')
        xml_result = junitxml.JUnitXmlResult(xml_stream)
        suite.run(xml_result)
        xml_result.stopTestRun()
        xml_stream.close()
        self.assertIn(results_file, os.listdir(self.test_base_dir))
        with open(results_file) as f:
            content = f.read()
        self.assertGreater(len(content), 0)
        regex = r'<testsuite errors="0" failures="1" name="" tests="1" .*'
        self.assertRegexpMatches(content, regex)

    def test_xml_output_error(self):
        results_file = 'results.xml'
        xml_stream = file(results_file, 'wb')
        xml_result = junitxml.JUnitXmlResult(xml_stream)
        suite = _make_error_test_suite()
        suite.run(xml_result)
        xml_result.stopTestRun()
        xml_stream.close()
        self.assertIn(results_file, os.listdir(self.test_base_dir))
        with open(results_file) as f:
            content = f.read()
        self.assertGreater(len(content), 0)
        regex = r'<testsuite errors="1" failures="0" name="" tests="1" .*'
        self.assertRegexpMatches(content, regex)
