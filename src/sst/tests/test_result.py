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
import subunit
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
            raise self.failureException

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


def format_expected(template, test, kwargs=None):
    """Expand common references in template.

    Tests that check runs output can be simplified if they use templates
    instead of litteral expected strings. There are plenty of examples below.

    :param template: A string where common strings have been replaced by a
        keyword so 1) tests are easier to read, 2) we don't run into pep8
        warnings for long lines.

    :param test: The test case under scrutiny.

    :param kwargs: A dict with more keywords for the template. This allows
        some tests to add more keywords when they are test specific.
    """
    if kwargs is None:
        kwargs = dict()
    # Getting the file name right is tricky, depending on whether the module
    # was just recompiled or not __file__ can be either .py or .pyc but when it
    # appears in an exception, the .py is always used.
    filename = __file__.replace('.pyc', '.py').replace('.pyo', '.py')
    # To allow easier reading for template, we format some known values
    kwargs.update(dict(classname='%s.%s' % (test.__class__.__module__,
                                            test.__class__.__name__),
                       name=test._testMethodName,
                       filename=filename))
    return template.format(**kwargs)


class TestConsoleOutput(testtools.TestCase):

    def assertOutput(self, expected, kind):
        test = get_case(kind)
        out = StringIO()
        res = result.TextTestResult(out)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        res._delta_to_float = zero
        test.run(res)
        self.assertEquals(expected, res.stream.getvalue())

    def test_pass(self):
        self.assertOutput('.', 'pass')

    def test_fail(self):
        self.assertOutput('F', 'fail')

    def test_error(self):
        self.assertOutput('E', 'error')

    def test_skip(self):
        self.assertOutput('s', 'skip')

    def test_skip_reason(self):
        self.assertOutput('s', 'skip_reason')

    def test_expected_failure(self):
        self.assertOutput('x', 'expected_failure')

    def test_unexpected_success(self):
        self.assertOutput('u', 'unexpected_success')


class TestVerboseConsoleOutput(testtools.TestCase):

    def assertOutput(self, expected, kind):
        test = get_case(kind)
        out = StringIO()
        res = result.TextTestResult(out, verbosity=2)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        res._delta_to_float = zero
        test.run(res)
        self.assertEquals(expected, res.stream.getvalue())

    def test_pass(self):
        self.assertOutput('''\
test_pass (sst.tests.test_result.Test) ... OK (0.000 secs)
''',
                          'pass')

    def test_fail(self):
        self.assertOutput('''\
test_fail (sst.tests.test_result.Test) ... FAIL (0.000 secs)
''',
                          'fail')

    def test_error(self):
        self.assertOutput('''\
test_error (sst.tests.test_result.Test) ... ERROR (0.000 secs)
''',
                          'error')

    def test_skip(self):
        self.assertOutput('''\
test_skip (sst.tests.test_result.Test) ... SKIP (0.000 secs)
''',
                          'skip')

    def test_skip_reason(self):
        self.assertOutput('''\
test_skip_reason (sst.tests.test_result.Test) ... SKIP Because (0.000 secs)
''',
                          'skip_reason')

    def test_expected_failure(self):
        self.assertOutput('''\
test_expected_failure (sst.tests.test_result.Test) ... XFAIL (0.000 secs)
''',
                          'expected_failure')

    def test_unexpected_success(self):
        self.assertOutput('''\
test_unexpected_success (sst.tests.test_result.Test) ... NOTOK (0.000 secs)
''',
                          'unexpected_success')


class TestXmlOutput(testtools.TestCase):

    def assertOutput(self, template, kind, kwargs=None):
        """Assert the expected output from a run for a given test.

        :param template: A string where common strings have been replaced by a
            keyword so we don't run into pep8 warnings for long lines.

        :param kind: A string used to select the kind of test.

        :param kwargs: A dict with more keywords for the template. This allows
            some tests to add more keywords when they are test specific.
        """
        out = StringIO()
        res = junitxml.JUnitXmlResult(out)
        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        res._now = lambda: 0.0
        res._duration = lambda f: 0.0
        test = get_case(kind)
        expected = format_expected(template, test, kwargs)
        test.run(res)
        # due to the nature of JUnit XML output, nothing will be written to
        # the stream until stopTestRun() is called.
        res.stopTestRun()
        self.assertEquals(expected, res._stream.getvalue())

    def test_pass(self):
        expected = '''\
<testsuite errors="0" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000"/>
</testsuite>
'''
        self.assertOutput(expected, 'pass')

    def test_fail(self):
        more = dict(exc_type='testtools.testresult.real._StringException')
        expected = '''\
<testsuite errors="0" failures="1" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<failure type="{exc_type}">_StringException: Traceback (most recent call last):
  File "{filename}", line 42, in {name}
    raise self.failureException
AssertionError

</failure>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'fail', more)

    def test_error(self):
        more = dict(exc_type='testtools.testresult.real._StringException')
        expected = '''\
<testsuite errors="1" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<error type="{exc_type}">_StringException: Traceback (most recent call last):
  File "{filename}", line 45, in {name}
    raise SyntaxError
SyntaxError: None

</error>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'error', more)

    def test_skip(self):
        expected = '''\
<testsuite errors="0" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<skipped></skipped>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'skip')

    def test_skip_reason(self):
        expected = '''\
<testsuite errors="0" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<skipped>Because</skipped>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'skip_reason')

    def test_expected_failure(self):
        expected = '''\
<testsuite errors="0" failures="0" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000"/>
</testsuite>
'''
        self.assertOutput(expected, 'expected_failure')

    def test_unexpected_success(self):
        expected = '''\
<testsuite errors="0" failures="1" name="" tests="1" time="0.000">
<testcase classname="{classname}" name="{name}" time="0.000">
<failure type="unittest.case._UnexpectedSuccess"/>
</testcase>
</testsuite>
'''
        self.assertOutput(expected, 'unexpected_success')


class TestSubunitOutput(testtools.TestCase):
    """Test subunit output stream."""

    def run_with_subunit(self, test):
        """Run a suite returning the subunit stream."""
        stream = StringIO()
        res = subunit.TestProtocolClient(stream)
        test.run(res)
        return res, stream

    def assertSubunitOutput(self, template, kind, kwargs=None):
        """Assert the expected output from a subunit run for a given test.

        :param template: A string where common strings have been replaced by a
            keyword so we don't run into pep8 warnings for long lines.

        :param kind: A string used to select the kind of test.

        :param kwargs: A dict with more keywords for the template. This allows
            some tests to add more keywords when they are test specific.
        """
        if kwargs is None:
            kwargs = dict()
        test = get_case(kind)
        expected = format_expected(template, test, kwargs)
        res, stream = self.run_with_subunit(test)
        self.assertEqual(expected, stream.getvalue())

    def test_pass(self):
        self.assertSubunitOutput('''\
test: sst.tests.test_result.Test.test_pass
successful: sst.tests.test_result.Test.test_pass [ multipart
]
''',
                                 'pass')

    def test_fail(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
failure: {classname}.{name} [ multipart
Content-Type: text/x-traceback;charset=utf8,language=python
traceback
C8\r
Traceback (most recent call last):
  File "{filename}", line 42, in {name}
    raise self.failureException
AssertionError
0\r
]
''',
                                 'fail')

    def test_error(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
error: {classname}.{name} [ multipart
Content-Type: text/x-traceback;charset=utf8,language=python
traceback
C2\r
Traceback (most recent call last):
  File "{filename}", line 45, in {name}
    raise SyntaxError
SyntaxError: None
0\r
]
''',
                                 'error')

    def test_skip(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
skip: {classname}.{name} [ multipart
Content-Type: text/plain;charset=utf8
reason
0\r
]
''',
                                 'skip')

    def test_skip_reason(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
skip: {classname}.{name} [ multipart
Content-Type: text/plain;charset=utf8
reason
7\r
Because0\r
]
''',
                                 'skip_reason')

    def test_expected_failure(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
xfail: {classname}.{name} [ multipart
Content-Type: text/plain;charset=utf8
reason
D\r
1 should be 00\r
Content-Type: text/x-traceback;charset=utf8,language=python
traceback
16\r
MismatchError: 1 != 0
0\r
]
''',
                                 'expected_failure')

    def test_unexpected_success(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
uxsuccess: {classname}.{name} [ multipart
Content-Type: text/plain;charset=utf8
reason
A\r
1 is not 10\r
]
''',
                                 'unexpected_success')


class TestSubunitInputStream(testtools.TestCase):
    """Test subunit input stream."""

    def assertOutput(self, expected, kind):
        test = get_case(kind)
        # Run with subunit output
        stream = StringIO()
        res = subunit.TestProtocolClient(stream)
        test.run(res)
        # Run with subunit input
        receiver = subunit.ProtocolTestCase(StringIO(stream.getvalue()))
        out = StringIO()
        text_result = result.TextTestResult(out, verbosity=0)
        receiver.run(text_result)
        self.assertEquals(expected, out.getvalue())

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
