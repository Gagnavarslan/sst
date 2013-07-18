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
    results,
    tests,
)


class TestResultOutput(testtools.TestCase):

    def assertOutput(self, expected, kind):
        test = tests.get_case(kind)
        out = StringIO()
        res = results.TextTestResult(out)

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


class TestVerboseResultOutput(testtools.TestCase):

    def assertOutput(self, template, kind):
        test = tests.get_case(kind)
        expected = tests.expand_template_for_test(template, test)
        out = StringIO()
        res = results.TextTestResult(out, verbosity=2)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        res._delta_to_float = zero
        test.run(res)
        self.assertEquals(expected, res.stream.getvalue())

    def test_pass(self):
        self.assertOutput('''\
{name} ({classname}) ... OK (0.000 secs)
''',
                          'pass')

    def test_fail(self):
        self.assertOutput('''\
{name} ({classname}) ... FAIL (0.000 secs)
''',
                          'fail')

    def test_error(self):
        self.assertOutput('''\
{name} ({classname}) ... ERROR (0.000 secs)
''',
                          'error')

    def test_skip(self):
        self.assertOutput('''\
{name} ({classname}) ... SKIP (0.000 secs)
''',
                          'skip')

    def test_skip_reason(self):
        self.assertOutput('''\
{name} ({classname}) ... SKIP Because (0.000 secs)
''',
                          'skip_reason')

    def test_expected_failure(self):
        self.assertOutput('''\
{name} ({classname}) ... XFAIL (0.000 secs)
''',
                          'expected_failure')

    def test_unexpected_success(self):
        self.assertOutput('''\
{name} ({classname}) ... NOTOK (0.000 secs)
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
        test = tests.get_case(kind)
        res.startTestRun()
        test.run(res)
        # due to the nature of JUnit XML output, nothing will be written to
        # the stream until stopTestRun() is called.
        res.stopTestRun()
        expected = tests.expand_template_for_test(template, test, kwargs)
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
  File "{filename}", line {traceback_line}, in {name}
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
  File "{filename}", line {traceback_line}, in {name}
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
        test = tests.get_case(kind)
        res, stream = self.run_with_subunit(test)
        expected = tests.expand_template_for_test(template, test, kwargs)
        self.assertEqual(expected, stream.getvalue())

    def test_pass(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
successful: {classname}.{name} [ multipart
]
''',
                                 'pass')

    def test_fail(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
failure: {classname}.{name} [ multipart
Content-Type: text/x-traceback;charset=utf8,language=python
traceback
{subunit_traceback_length}\r
Traceback (most recent call last):
  File "{filename}", line {traceback_line}, in {name}
    raise self.failureException
AssertionError
0\r
]
''',
                                 'fail',
                                 dict(traceback_fixed_length=116))

    def test_error(self):
        self.assertSubunitOutput('''\
test: {classname}.{name}
error: {classname}.{name} [ multipart
Content-Type: text/x-traceback;charset=utf8,language=python
traceback
{subunit_traceback_length}\r
Traceback (most recent call last):
  File "{filename}", line {traceback_line}, in {name}
    raise SyntaxError
SyntaxError: None
0\r
]
''',
                                 'error',
                                 dict(traceback_fixed_length=110))

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


class TestSubunitInputStreamTextResultOutput(TestResultOutput):
    """Test subunit input stream.

    More precisely, ensure our test result can properly handle a subunit input
    stream.
    """

    def assertOutput(self, expected, kind):
        test = tests.get_case(kind)
        # Get subunit output (what subprocess produce)
        stream = StringIO()
        res = subunit.TestProtocolClient(stream)
        test.run(res)
        # Inject it again (what controlling process consumes)
        receiver = subunit.ProtocolTestCase(StringIO(stream.getvalue()))
        out = StringIO()
        text_result = results.TextTestResult(out, verbosity=0)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        text_result._delta_to_float = zero
        receiver.run(text_result)
        self.assertEquals(expected, out.getvalue())


class TestSubunitInputStreamXmlOutput(TestXmlOutput):

    def assertOutput(self, template, kind, kwargs=None):
        """Assert the expected output from a run for a given test.

        :param template: A string where common strings have been replaced by a
            keyword so we don't run into pep8 warnings for long lines.

        :param kind: A string used to select the kind of test.

        :param kwargs: A dict with more keywords for the template. This allows
            some tests to add more keywords when they are test specific.
        """
        test = tests.get_case(kind)
        # Get subunit output (what subprocess produce)
        stream = StringIO()
        res = subunit.TestProtocolClient(stream)
        test.run(res)
        # Inject it again (what controlling process consumes)
        receiver = subunit.ProtocolTestCase(StringIO(stream.getvalue()))
        out = StringIO()
        res = junitxml.JUnitXmlResult(out)
        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        res._now = lambda: 0.0
        res._duration = lambda f: 0.0
        expected = tests.expand_template_for_test(template, test, kwargs)
        res.startTestRun()
        receiver.run(res)
        # due to the nature of JUnit XML output, nothing will be written to
        # the stream until stopTestRun() is called.
        res.stopTestRun()
        self.assertEquals(expected, out.getvalue())
