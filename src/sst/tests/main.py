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


import sys
import time
import unittest

import testtools
import junitxml

from sst import result


class TestRunner(object):
    """Test Runner that writes XML output and reports status.

    """
    resultclass = testtools.testresult.MultiTestResult

    def __init__(self, xml_stream, verbosity, txt_stream=None):
        if txt_stream is None:
            txt_stream = sys.stderr
        self.verbosity = verbosity
        self._txt_stream = txt_stream
        self._xml_stream = xml_stream

    def _make_result(self):
        xml_result = junitxml.JUnitXmlResult(self._xml_stream)
        txt_result = result.TextTestResult(self._txt_stream,
                                           None, self.verbosity)
        return self.resultclass(xml_result, txt_result)

    def run(self, test):
        result = self._make_result()
        result.startTestRun()
        test.run(result)
        result.stopTestRun()
        return result


class TestProgram(testtools.run.TestProgram):

    def __init__(self, module, argv, stdout=None,
                 testRunner=None, exit=True, xml=True):
        if testRunner is None:
            testRunner = unittest.TextTestRunner(verbosity=2)

        if xml:
            xml_stream = file('unitresults.xml', 'wb')
            testRunner = TestRunner(xml_stream, verbosity=2)

        super(TestProgram, self).__init__(module, argv=argv, stdout=stdout,
                                          testRunner=testRunner, exit=exit)
