#
#   Copyright (c) 2011,2012,2013 Canonical Ltd.
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

from testtools import testresult


class TextTestResult(testresult.TextTestResult):
    """A TestResult which outputs activity to a text stream."""

    def __init__(self, stream, failfast=False, verbosity=1):
        super(TextTestResult, self).__init__(stream, failfast)
        self.verbose = verbosity > 1

    def startTest(self, test):
        if self.verbose:
            self.stream.write(str(test))
            self.stream.write(' ... ')
        self.start_time = self._now()
        super(TextTestResult, self).startTest(test)

    def stopTest(self, test):
        if self.verbose:
            elapsed_time = self._now() - self.start_time
            self.stream.write(' (%.3f secs)\n'
                              % self._delta_to_float(elapsed_time))
            self.stream.flush()
        super(TextTestResult, self).stopTest(test)

    def addExpectedFailure(self, test, err=None, details=None):
        if self.verbose:
            self.stream.write('XFAIL')
        else:
            self.stream.write('x')
        super(TextTestResult, self).addExpectedFailure(test, err, details)

    def addError(self, test, err=None, details=None):
        if self.verbose:
            self.stream.write('ERROR')
        else:
            self.stream.write('E')
        super(TextTestResult, self).addError(test, err, details)

    def addFailure(self, test, err=None, details=None):
        if self.verbose:
            self.stream.write('FAIL')
        else:
            self.stream.write('F')
        super(TextTestResult, self).addFailure(test, err, details)

    def addSkip(self, test, details=None):
        # FIXME: Something weird is going on with testtools, as we're supposed
        # to use a (self, test, reason, details) signature but this is never
        # called this way -- vila 2013-05-10
        reason = details.get('reason', '').as_text()
        if self.verbose:
            if not reason:
                reason_displayed = ''
            else:
                reason_displayed = ' ' + reason
            self.stream.write('SKIP%s' % reason_displayed)
        else:
            self.stream.write('s')
        super(TextTestResult, self).addSkip(test, reason, details)
        # testtools has its own handling of skipped tests in self.skip_reasons
        # If we wanted to *also* handle 'skipped' like unittest, we could add a
        # self.skipped.append((test, reason)) call.

    def addSuccess(self, test, details=None):
        if self.verbose:
            self.stream.write('OK')
        else:
            self.stream.write('.')
        super(TextTestResult, self).addSuccess(test, details)

    def addUnexpectedSuccess(self, test, details=None):
        if self.verbose:
            self.stream.write('NOTOK')
        else:
            self.stream.write('u')
        super(TextTestResult, self).addUnexpectedSuccess(test, details)
