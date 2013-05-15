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


from cStringIO import StringIO

import junitxml
import testtools

from sst import (
    result,
    tests,
)


def get_case(kind):
    # Define the class in a function so test loading don't try to load it as a
    # regular test class.
    class Test(testtools.TestCase):

        def test_pass(self):
            pass

        def test_fail(self):
            self.assertTrue(False)

        def test_error(self):
            raise SyntaxError

        def test_skip(self):
            self.skipTest('')

        def test_skip_reason(self):
            self.skipTest('Because')

        def test_expected_failure(self):
            # We expect the test to fail and it does
            self.expectFailure("1 should be 0", self.assertEqual, 1, 0)

        def test_unexpected_success(self):
            # We expect the test to fail but it doesn't
            self.expectFailure("1 is not 1", self.assertEqual, 1, 1)

    test_method = 'test_%s' % (kind,)
    return Test(test_method)


class TestConsoleOutput(testtools.TestCase):

    def setUp(self):
        super(TestConsoleOutput, self).setUp()
        tests.set_cwd_to_tmp(self)

    def assertOutput(self, expected, kind):
        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        test = get_case(kind)
        out = StringIO()
        res = result.TextTestResult(out, timer=lambda: 0.0)
        test.run(res)
        self.assertEquals(expected, res.stream.getvalue())

    def test_pass_output(self):
        self.assertOutput('.', 'pass')

    def test_fail_output(self):
        self.assertOutput('F', 'fail')

    def test_error_output(self):
        self.assertOutput('E', 'error')

    def test_skip_output(self):
        self.assertOutput('s', 'skip')

    def test_skip_reason_output(self):
        self.assertOutput('s', 'skip_reason')

    def test_expected_failure_output(self):
        self.assertOutput('x', 'expected_failure')

    def test_unexpected_success_output(self):
        self.assertOutput('u', 'unexpected_success')


class TestVerboseConsoleOutput(testtools.TestCase):

    def setUp(self):
        super(TestVerboseConsoleOutput, self).setUp()
        tests.set_cwd_to_tmp(self)

    def assertOutput(self, expected, kind):
        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        test = get_case(kind)
        out = StringIO()
        res = result.TextTestResult(out, verbosity=2, timer=lambda: 0.0)
        test.run(res)
        self.assertEquals(expected, res.stream.getvalue())

    def test_pass_output(self):
        self.assertOutput('''\
test_pass (sst.tests.test_result.Test) ... OK (0.000 secs)
''',
                          'pass')

    def test_fail_output(self):
        self.assertOutput('''\
test_fail (sst.tests.test_result.Test) ... FAIL (0.000 secs)
''',
                          'fail')

    def test_error_output(self):
        self.assertOutput('''\
test_error (sst.tests.test_result.Test) ... ERROR (0.000 secs)
''',
                          'error')

    def test_skip_output(self):
        self.assertOutput('''\
test_skip (sst.tests.test_result.Test) ... SKIP (0.000 secs)
''',
                          'skip')

    def test_skip_reason_output(self):
        self.assertOutput('''\
test_skip_reason (sst.tests.test_result.Test) ... SKIP Because (0.000 secs)
''',
                          'skip_reason')

    def test_expected_failure_output(self):
        self.assertOutput('''\
test_expected_failure (sst.tests.test_result.Test) ... XFAIL (0.000 secs)
''',
                          'expected_failure')

    def test_unexpected_success_output(self):
        self.assertOutput('''\
test_unexpected_success (sst.tests.test_result.Test) ... NOTOK (0.000 secs)
''',
                          'unexpected_success')


class TestXmlOutput(testtools.TestCase):

    def setUp(self):
        super(TestXmlOutput, self).setUp()
        tests.set_cwd_to_tmp(self)

    def assertOutput(self, template, kind, kwargs=None):
        """Assert the expected output from a run for a given test.

        :param template: A string where common strings have been replaced by a
            keyword so we don't run into pep8 warnings for long lines.

        :param kind: A string used to select the kind of test.

        :param kwargs: A dict with more keywords for the template. This allows
            some tests to add more keywords when they are test specific.
        """
        if kwargs is None:
            kwargs = dict()
        out = StringIO()
        res = junitxml.JUnitXmlResult(out)
        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        res._now = lambda: 0.0
        res._duration = lambda f: 0.0
        test = get_case(kind)
        test.run(res)
        # due to the nature of JUnit XML output, nothing will be written to
        # the stream until stopTestRun() is called.
        res.stopTestRun()
        # To allow easier reading for template, we format some known values
        kwargs.update(dict(classname='%s.%s' % (test.__class__.__module__,
                                                test.__class__.__name__),
                           name=test._testMethodName))
        expected = template.format(**kwargs)
        self.assertEquals(expected, res._stream.getvalue())

    def test_pass_output(self):
        expected = '''\
<testsuite errors="0" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000"/>
</testsuite>
'''
        self.assertOutput(expected, 'pass')

    def test_fail_output(self):
        # Getting the file name right is tricky, depending on whether the
        # module was just recompiled or not __file__ can be either .py or .pyc
        # but when it appears in an exception, the .py is always used.
        filename = __file__.replace('.pyc', '.py').replace('.pyo', '.py')
        more = dict(exc_type='testtools.testresult.real._StringException',
                    filename=filename)
        expected = '''\
<testsuite errors="0" failures="1" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<failure type="{exc_type}">_StringException: Traceback (most recent call last):
  File "{filename}", line 41, in {name}
    self.assertTrue(False)
AssertionError: False is not true

</failure>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'fail', more)

    def test_error_output(self):
        # Getting the file name right is tricky, depending on whether the
        # module was just recompiled or not __file__ can be either .py or .pyc
        # but when it appears in an exception, the .py is always used.
        filename = __file__.replace('.pyc', '.py').replace('.pyo', '.py')
        more = dict(exc_type='testtools.testresult.real._StringException',
                    filename=filename)
        expected = '''\
<testsuite errors="1" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<error type="{exc_type}">_StringException: Traceback (most recent call last):
  File "{filename}", line 44, in {name}
    raise SyntaxError
SyntaxError: None

</error>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'error', more)

    def test_skip_output(self):
        expected = '''\
<testsuite errors="0" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<skipped></skipped>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'skip')

    def test_skip_reason_output(self):
        expected = '''\
<testsuite errors="0" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<skipped>Because</skipped>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'skip_reason')

    def test_expected_failure_output(self):
        expected = '''\
<testsuite errors="0" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000"/>
</testsuite>
'''
        self.assertOutput(expected, 'expected_failure')

    def test_unexpected_success_output(self):
        expected = '''\
<testsuite errors="0" failures="1" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<failure type="unittest.case._UnexpectedSuccess"/>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'unexpected_success')
