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
import sys

from sst import (
    runtests,
    tests,
)


class TestRunTestsFilteringByTestId(tests.ImportingLocalFilesTest):

    def setUp(self):
        super(TestRunTestsFilteringByTestId, self).setUp()
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
file: t/bar.py
Don't look at me !
file: t/too.py
Don't look at me !
''')

    def run_tests(self, *args, **kwargs):
        # FIXME: runtests use print, it should accept a stream instead. We also
        # should be able to better focus the test filtering but that requires
        # refactoring runtests. -- vila 2013-05-07
        self.out = StringIO()
        self.patch(sys, 'stdout', self.out)
        runtests.runtests(*args, test_dir='t', collect_only=True, **kwargs)
        lines = self.out.getvalue().splitlines()
        self.assertEqual('', lines[0])
        # We don't care about the number of tests, that will be checked later
        # by the caller
        self.assertTrue(lines[1].endswith('test cases loaded'))
        self.assertEqual('', lines[2])
        self.assertEqual('-' * 62, lines[3])
        self.assertEqual('Collect-Only Enabled, Not Running Tests...',
                         lines[4])
        self.assertEqual('', lines[5])
        self.assertEqual('Tests Collected:', lines[6])
        self.assertEqual('----------------', lines[7])
        return lines[8:]

    def test_all(self):
        self.assertEqual(['t.bar', 't.test_foo', 't.too'],
                         self.run_tests(None))

    def test_single_include(self):
        self.assertEqual(['t.bar'],
                         self.run_tests(['t.b']))

    def test_multiple_includes(self):
        self.assertEqual(['t.bar', 't.too'],
                         self.run_tests(['t.b', 't.to']))

    def test_single_exclude(self):
        self.assertEqual(['t.bar'],
                         self.run_tests(None, excludes=['t.t']))

    def test_multiple_excludes(self):
        self.assertEqual(['t.test_foo'],
                         self.run_tests(None, excludes=['t.to', 't.b']))

    def test_mixed(self):
        self.assertEqual(['t.test_foo'],
                         self.run_tests(['t.t'], excludes=['to']))


class SSTRunExitCodeTestCase(tests.ImportingLocalFilesTest):

    def setUp(self):
        super(SSTRunExitCodeTestCase, self).setUp()
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
from sst import loader
discover = loader.discoverRegularTests

file: t/test_all_pass.py
import unittest
class TestAllPass(unittest.TestCase):
    def test_all_pass(self):
        self.assertTrue(True)

file: t/test_one_fail.py
import unittest
class TestOneFail(unittest.TestCase):
    def test_one_fail(self):
        self.assertTrue(False)

file: t/test_multi_fail.py
import unittest
class TestMultiFail(unittest.TestCase):
    def test_fail_1(self):
        self.assertTrue(False)
    def test_fail_2(self):
        self.assertTrue(False)
''')

    def run_tests(self, args):
        self.out = StringIO()
        self.patch(sys, 'stdout', self.out)

        failures = runtests.runtests(args)

        exit_code = 0
        if failures:
            exit_code = 1
        return exit_code

    def test_exitcode_pass(self):
        exit_code = self.run_tests(['test_all_pass$'])
        self.assertEqual(exit_code, 0)

    def test_exitcode_fail(self):
        exit_code = self.run_tests(['test_one_fail$'])
        self.assertEqual(exit_code, 1)

    def test_exitcode_multi_fail(self):
        exit_code = self.run_tests(['test_fail_.*'])
        self.assertEqual(exit_code, 1)
