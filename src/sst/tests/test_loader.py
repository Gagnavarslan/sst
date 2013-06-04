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
"""Test for sst test loader.

Many tests below create a temporary file hierarchy including python code and/or
sst scripts. Loading tests imply importing python modules in a way that tests
can observe via sys.modules while preserving isolation.

The isolation is provided via two means:

- the file hierarchies are created in a temporary directory added to sys.path
  so test can just import from their current directory,

- tests.protect_imports will remove the loaded modules from sys.modules and
  restore sys.path.

Because the tests themselves share this module name space, care must be taken
by tests to not use module names already used in the module. Most of tests
below therefore use 't' as the main directory because:
- we use python not lisp so using 't' is ok ;)
- it's short,
- it's unlikely to be imported by the module.

"""
import testtools

from sst import (
    loader,
    tests,
)


class TestNameMatcher(testtools.TestCase):

    def test_defaults(self):
        nm = loader.NameMatcher()
        self.assertFalse(nm.matches(''))
        self.assertFalse(nm.matches('foo'))

    def test_simple_include(self):
        nm = loader.NameMatcher(includes=['foo'])
        self.assertTrue(nm.matches('foo'))
        self.assertTrue(nm.matches('XXXfooXXX'))

    def test_multiple_includes(self):
        nm = loader.NameMatcher(includes=['foo', '^bar'])
        self.assertTrue(nm.matches('foo'))
        self.assertTrue(nm.matches('bar'))
        self.assertTrue(nm.matches('barfoo'))
        self.assertTrue(nm.matches('foobar'))
        self.assertFalse(nm.matches('bazbar'))

    def test_simple_excludes(self):
        nm = loader.NameMatcher(includes=['.*'], excludes=['foo'])
        self.assertTrue(nm.matches('bar'))
        self.assertFalse(nm.matches('foo'))
        self.assertFalse(nm.matches('foobar'))

    def test_multiple_excludes(self):
        nm = loader.NameMatcher(includes=['.*'], excludes=['foo$', '^bar'])
        self.assertTrue(nm.matches('baz'))
        self.assertTrue(nm.matches('footix'))
        self.assertFalse(nm.matches('foo'))
        self.assertFalse(nm.matches('barista'))


class TestTestLoader(tests.ImportingLocalFilesTest):

    def make_test_loader(self):
        return loader.TestLoader()

    def test_ignored_file(self):
        with open('empty.py', 'w') as f:
            f.write('')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('.')
        self.assertEqual(0, suite.countTestCases())

    def test_invalid_file(self):
        with open('test_foo.py', 'w') as f:
            f.write("I'm no python code")
        test_loader = self.make_test_loader()
        self.assertRaises(SyntaxError, test_loader.discoverTestsFromTree, '.')

    def test_invalid_file_in_a_dir(self):
        tests.write_tree_from_desc('''dir: t
file: t/test_foo.py
I'm not even python code
''')
        # Since 'foo' can't be imported, discoverTestsFromTree should not be
        # invoked, ensure we still get some meaningful error message.
        test_loader = self.make_test_loader()
        e = self.assertRaises(ImportError,
                              test_loader.discoverTestsFromTree, 't')
        self.assertEqual('No module named t.test_foo', e.message)

    def test_symlink_is_ignored(self):
        tests.write_tree_from_desc('''dir: t
file: t/foo
tagada
link: t/foo t/test_bar.py
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('.')
        # Despite a matching name, symlink is ignored
        self.assertEqual(0, suite.countTestCases())

    def test_broken_symlink_is_ignored(self):
        tests.write_tree_from_desc('''dir: t
link: t/test_bar.py t/test_qux.py
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('.')
        self.assertEqual(0, suite.countTestCases())

    def test_file_in_a_dir(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
dir: t/dir
file: t/dir/test_foo.py
import unittest

class Test(unittest.TestCase):

    def test_it(self):
        self.assertTrue(True)
''')
        test_loader = self.make_test_loader()
        e = self.assertRaises(ImportError,
                              test_loader.discoverTestsFromTree, 't/dir')
        # 't' is a package but 'dir' is not, hence, 'dir.test_foo' is not
        # either, blame python for the approximate message ;-/
        self.assertEqual('No module named dir.test_foo', e.message)

    def test_simple_file_in_a_package(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('t')
        self.assertEqual(1, suite.countTestCases())

    # FIXME: Not strictly a TestLoader test, may be more appropriate as
    # demonstrating how to discover different kind of tests -- vila 2013-06-04
    def test_scripts_below_regular(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
dir: t/scripts
file: t/scripts/__init__.py
from sst import loader

discover = loader.discoverTestScripts
file: t/scripts/script.py
raise AssertionError('Loading only, executing fails')
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('t')
        self.assertEqual(2, suite.countTestCases())
        # Check which kind of tests have been discovered or we may miss regular
        # test cases seen as scripts.
        self.assertEqual(['t.scripts.script',
                         't.test_foo.Test.test_me'],
                         [t.id() for t in testtools.iterate_tests(suite)])


class TestTestLoaderPattern(tests.ImportingLocalFilesTest):

    def make_test_loader(self):
        return loader.TestLoader()

    def test_default_pattern(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo.py
Don't look at me !
file: t/test_foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discover('t')
        self.assertEqual(1, suite.countTestCases())

    def test_pattern(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo_foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
file: t/test_foo.py
Don't look at me !
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discover('t', pattern='foo*.py')
        self.assertEqual(1, suite.countTestCases())


class TestTestLoaderTopLevelDir(testtools.TestCase):

    def setUp(self):
        super(TestTestLoaderTopLevelDir, self).setUp()
        # We build trees rooted in test_base_dir from which we will import
        tests.set_cwd_to_tmp(self)
        tests.protect_imports(self)

    def make_test_loader(self):
        return loader.TestLoader()

    def _create_foo_in_tests(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
''')

    def test_simple_file_in_a_dir(self):
        self._create_foo_in_tests()
        test_loader = self.make_test_loader()
        suite = test_loader.discover('t', '*.py', self.test_base_dir)
        self.assertEqual(1, suite.countTestCases())

    def test_simple_file_in_a_dir_no_sys_path(self):
        self._create_foo_in_tests()
        test_loader = self.make_test_loader()
        e = self.assertRaises(ImportError,
                              test_loader.discover, 't', '*.py')
        self.assertEqual(e.message, 'No module named t')


class TestSSTestLoader(tests.ImportingLocalFilesTest):

    def make_test_loader(self):
        return loader.SSTestLoader()

    def test_simple_script(self):
        # A simple do nothing script with no imports
        tests.write_tree_from_desc('''file: foo.py
pass
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('.')
        self.assertEqual(1, suite.countTestCases())

    def test_simple_script_with_csv(self):
        tests.write_tree_from_desc('''file: foo.py
pass
file: foo.csv
'foo'^'bar'
1^baz
2^qux
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('.')
        self.assertEqual(2, suite.countTestCases())

    def test_simple_script_in_a_dir(self):
        tests.write_tree_from_desc('''dir: t
# no t/__init__.py required, we don't need to import the scripts
file: t/script.py
raise AssertionError('Loading only, executing fails')
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('t')
        self.assertEqual(1, suite.countTestCases())

    def test_ignore_privates(self):
        tests.write_tree_from_desc('''dir: t
file: t/_private.py
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('t')
        self.assertEqual(0, suite.countTestCases())

    def test_regular_below_scripts(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
dir: t/regular
file: t/regular/__init__.py
from sst import loader
import unittest

discover = loader.discoverRegularTests

class Test(unittest.TestCase):

    def test_in_init(self):
      self.assertTrue(True)
file: t/regular/test_foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
file: t/script.py
raise AssertionError('Loading only, executing fails')
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('t')
        # Check which kind of tests have been discovered or we may miss regular
        # test cases seen as scripts.
        self.assertEqual(['t.regular.Test.test_in_init',
                          't.regular.test_foo.Test.test_me',
                          't.script'],
                         [t.id() for t in testtools.iterate_tests(suite)])

    def test_regular_and_scripts_mixed(self):
        def regular(dir_name, name, suffix=None):
            if suffix is None:
                suffix = ''
            return '''
file: {dir_name}/{name}{suffix}
from sst import cases

class Test_{name}(cases.SSTTestCase):
    def test_{name}(self):
        pass
'''.format(**locals())

        tests.write_tree_from_desc('''dir: tests
file: tests/__init__.py
from sst import loader

discover = loader.discoverRegularTests
''')
        tests.write_tree_from_desc(regular('tests', 'test_real', '.py'))
        tests.write_tree_from_desc(regular('tests', 'test_real1', '.py'))
        tests.write_tree_from_desc(regular('tests', 'test_real2', '.py'))
        # Leading '_' => ignored
        tests.write_tree_from_desc(regular('tests', '_hidden', '.py'))
        # Not a python file => ignored
        tests.write_tree_from_desc(regular('tests', 'not-python'))
        # Some empty files
        tests.write_tree_from_desc('''
file: script1.py
file: script2.py
file: not_a_test
file: test_not_a_test.potato
_hidden_too.py
''')
        test_loader = self.make_test_loader()
        suite = test_loader.discoverTestsFromTree('.')
        self.assertEqual(['script1',
                          'script2',
                          'tests.test_real.Test_test_real.test_test_real',
                          'tests.test_real1.Test_test_real1.test_test_real1',
                          'tests.test_real2.Test_test_real2.test_test_real2'],
                         [t.id() for t in testtools.iterate_tests(suite)])
