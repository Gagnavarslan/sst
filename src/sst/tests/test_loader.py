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


class TestMatchesForRegexp(testtools.TestCase):

    def test_matches(self):
        matches = loader.matches_for_regexp('foo.*')
        # All assertions should succeed, if one of them fails, we have a bigger
        # problem than having one test for each assertion
        self.assertTrue(matches('foo'))
        self.assertFalse(matches('bar'))
        self.assertTrue(matches('foobar'))
        self.assertFalse(matches('barfoo'))


class TestMatchesForGlob(testtools.TestCase):

    def test_matches(self):
        matches = loader.matches_for_glob('foo*')
        # All assertions should succeed, if one of them fails, we have a bigger
        # problem than having one test for each assertion
        self.assertTrue(matches('foo'))
        self.assertFalse(matches('fo'))
        self.assertFalse(matches('bar'))
        self.assertTrue(matches('foobar'))
        self.assertFalse(matches('barfoo'))


class TestNameMatcher(testtools.TestCase):

    def test_default_includes(self):
        name_matcher = loader.NameMatcher()
        self.assertTrue(name_matcher.includes('foo'))
        self.assertTrue(name_matcher.matches('foo'))

    def test_default_exclude(self):
        name_matcher = loader.NameMatcher()
        self.assertFalse(name_matcher.excludes('foo'))
        self.assertTrue(name_matcher.matches('foo'))

    def test_provided_includes(self):
        name_matcher = loader.NameMatcher(
            includes=loader.matches_for_regexp('^.*foo$'))
        self.assertTrue(name_matcher.includes('foo'))
        self.assertTrue(name_matcher.includes('barfoo'))
        self.assertFalse(name_matcher.includes('bar'))
        self.assertFalse(name_matcher.includes('foobar'))

    def test_provided_excludes(self):
        name_matcher = loader.NameMatcher(
            excludes=loader.matches_for_regexp('^bar.*foo$'))
        self.assertTrue(name_matcher.excludes('barfoo'))
        self.assertFalse(name_matcher.excludes('foo'))


class TestFileLoader(testtools.TestCase):

    def get_test_loader(self):
        return loader.TestLoader()

    def test_discover_nothing(self):
        tests.set_cwd_to_tmp(self)
        with open('foo', 'w') as f:
            f.write('bar\n')
        file_loader = loader.FileLoader(self.get_test_loader())
        suite = file_loader.discover('.', 'foo')
        self.assertIs(None, suite)


class TestModuleLoader(tests.ImportingLocalFilesTest):

    def get_test_loader(self):
        return loader.TestLoader()

    def test_default_includes(self):
        mod_loader = loader.ModuleLoader(self.get_test_loader())
        self.assertTrue(mod_loader.matches('foo.py'))
        # But we won't try to import a random file
        self.assertFalse(mod_loader.matches('foopy'))

    def test_discover_empty_file(self):
        with open('foo.py', 'w') as f:
            f.write('')
        mod_loader = loader.ModuleLoader(self.get_test_loader())
        suite = mod_loader.discover('.', 'foo.py')
        self.assertEqual(0, suite.countTestCases())

    def test_discover_invalid_file(self):
        with open('foo.py', 'w') as f:
            f.write("I'm no python code")
        mod_loader = loader.ModuleLoader(self.get_test_loader())
        self.assertRaises(SyntaxError, mod_loader.discover, '.', 'foo.py')

    def test_discover_valid_file(self):
        with open('foo.py', 'w') as f:
            f.write('''
import unittest

class Test(unittest.TestCase):

    def test_it(self):
        self.assertTrue(True)
''')
        mod_loader = loader.ModuleLoader(self.get_test_loader())
        suite = mod_loader.discover('.', 'foo.py')
        self.assertEqual(1, suite.countTestCases())


class TestDirLoaderDiscoverPath(tests.ImportingLocalFilesTest):

    def get_test_loader(self):
        test_loader = loader.TestLoader()
        # We don't use the default PackageLoader for unit testing DirLoader
        # behavior. But we still leave ModuleLoader for the file loader.
        test_loader.dirLoaderClass = loader.DirLoader
        return test_loader

    def test_discover_path_for_file_without_package(self):
        tests.write_tree_from_desc('''dir: t
file: t/foo.py
I'm not even python code
''')
        # Since 'foo' can't be imported, discover_path should not be invoked,
        # ensure we still get some meaningful error message.
        dir_loader = loader.DirLoader(self.get_test_loader())
        e = self.assertRaises(ImportError,
                              dir_loader.discover_path, 't', 'foo.py')
        self.assertEqual('No module named t.foo', e.message)

    def test_discover_path_for_valid_file(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo.py
import unittest

class Test(unittest.TestCase):

    def test_it(self):
        self.assertTrue(True)
''')
        dir_loader = loader.DirLoader(self.get_test_loader())
        suite = dir_loader.discover_path('t', 'foo.py')
        self.assertEqual(1, suite.countTestCases())

    def test_discover_path_for_dir(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
dir: t/dir
file: t/dir/foo.py
import unittest

class Test(unittest.TestCase):

    def test_it(self):
        self.assertTrue(True)
''')
        dir_loader = loader.DirLoader(self.get_test_loader())
        e = self.assertRaises(ImportError,
                              dir_loader.discover_path, 't', 'dir')
        # 't' is a module but 'dir' is not, hence, 'dir.foo' is not either,
        # blame python for the approximate message ;-/
        self.assertEqual('No module named dir.foo', e.message)

    def test_discover_path_for_not_matching_symlink(self):
        tests.write_tree_from_desc('''dir: t
file: t/foo
tagada
link: t/foo t/bar.py
''')
        dir_loader = loader.DirLoader(self.get_test_loader())
        suite = dir_loader.discover_path('t', 'bar.py')
        self.assertIs(None, suite)

    def test_discover_path_for_broken_symlink(self):
        tests.write_tree_from_desc('''dir: t
file: t/foo
tagada
link: bar t/qux
''')
        dir_loader = loader.DirLoader(self.get_test_loader())
        suite = dir_loader.discover_path('t', 'qux')
        self.assertIs(None, suite)

    def test_discover_simple_file_in_dir(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo.py
import unittest

class Test(unittest.TestCase):

    def test_it(self):
        self.assertTrue(True)
''')
        dir_loader = loader.DirLoader(self.get_test_loader())
        suite = dir_loader.discover('.', 't')
        # Despite using DirLoader, python triggers the 't' import so we are
        # able to import foo.py and all is well
        self.assertEqual(1, suite.countTestCases())


class TestPackageLoader(tests.ImportingLocalFilesTest):

    def get_test_loader(self):
        test_loader = loader.TestLoader()
        return test_loader

    def test_discover_package_with_invalid_file(self):
        tests.write_tree_from_desc('''dir: dir
file: dir/__init__.py
file: dir/foo.py
I'm not even python code
''')
        pkg_loader = loader.PackageLoader(self.get_test_loader())
        e = self.assertRaises(SyntaxError, pkg_loader.discover, '.', 'dir')
        self.assertEqual('EOL while scanning string literal', e.args[0])

    def test_discover_simple_file_in_dir(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo.py
import unittest

class Test(unittest.TestCase):

    def test_it(self):
        self.assertTrue(True)
''')
        dir_loader = loader.DirLoader(self.get_test_loader())
        suite = dir_loader.discover('.', 't')
        self.assertEqual(1, suite.countTestCases())


class TestLoadScript(testtools.TestCase):

    def setUp(self):
        super(TestLoadScript, self).setUp()
        tests.set_cwd_to_tmp(self)

    def create_script(self, path, content):
        with open(path, 'w') as f:
            f.write(content)

    def test_load_simple_script(self):
        # A simple do nothing script with no imports
        self.create_script('foo.py', 'pass')
        suite = loader.TestLoader().loadTestsFromScript('.', 'foo.py')
        self.assertEqual(1, suite.countTestCases())

    def test_load_simple_script_with_csv(self):
        self.create_script('foo.py', "pass")
        with open('foo.csv', 'w') as f:
            f.write('''\
'foo'^'bar'
1^baz
2^qux
''')
        suite = loader.TestLoader().loadTestsFromScript('.', 'foo.py')
        self.assertEqual(2, suite.countTestCases())

    def test_load_non_existing_script(self):
        suite = loader.TestLoader().loadTestsFromScript('.', 'foo.py')
        self.assertEqual(0, suite.countTestCases())


class TestScriptLoader(tests.ImportingLocalFilesTest):

    def get_test_loader(self):
        return loader.TestLoader()

    def test_simple_script(self):
        tests.write_tree_from_desc('''dir: t
# no t/__init__.py required, we don't need to import the scripts
file: t/foo.py
from sst.actions import *

raise AssertionError('Loading only, executing fails')
''')
        script_loader = loader.ScriptLoader(self.get_test_loader())
        suite = script_loader.discover('t', 'foo.py')
        self.assertEqual(1, suite.countTestCases())

    def test_ignore_privates(self):
        tests.write_tree_from_desc('''dir: t
file: t/_private.py
''')
        script_loader = loader.ScriptLoader(self.get_test_loader())
        suite = script_loader.discover('t', '_private.py')
        self.assertIs(None, suite)


class TesScriptDirLoader(tests.ImportingLocalFilesTest):

    def test_shared(self):
        tests.write_tree_from_desc('''dir: t
# no t/__init__.py required, we don't need to import the scripts
file: t/foo.py
from sst.actions import *

raise AssertionError('Loading only, executing fails')
dir: t/shared
file: t/shared/amodule.py
Don't look at me !
''')
        script_dir_loader = loader.ScriptDirLoader(loader.TestLoader())
        suite = script_dir_loader.discover('t', 'shared')
        self.assertIs(None, suite)

    def test_regular(self):
        tests.write_tree_from_desc('''dir: t
# no t/__init__.py required, we don't need to import the scripts
dir: t/subdir
file: t/subdir/foo.py
raise AssertionError('Loading only, executing fails')
dir: t/shared
file: t/shared/amodule.py
Don't look at me !
''')
        test_loader = loader.TestLoader()
        suite = test_loader.discoverTests(
            '.', file_loader_class=loader.ScriptLoader,
            dir_loader_class=loader.ScriptDirLoader)
        self.assertEqual(1, suite.countTestCases())


class TestTestLoader(tests.ImportingLocalFilesTest):

    def test_simple_file_in_a_dir(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
''')
        test_loader = loader.TestLoader()
        suite = test_loader.discoverTests('t')
        self.assertEqual(1, suite.countTestCases())

    def test_broken_file_in_a_dir(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo.py
I'm not even python code
''')
        test_loader = loader.TestLoader()
        e = self.assertRaises(SyntaxError, test_loader.discoverTests, 't')
        self.assertEqual('EOL while scanning string literal', e.args[0])

    def test_scripts_below_regular(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/foo.py
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
        test_loader = loader.TestLoader()
        suite = test_loader.discoverTests('t')
        self.assertEqual(2, suite.countTestCases())
        # Check which kind of tests have been discovered or we may miss regular
        # test cases seen as scripts.
        self.assertEqual(['t.foo.Test.test_me',
                          't.scripts.script'],
                         [t.id() for t in testtools.iterate_tests(suite)])

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
file: t/regular/foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
file: t/script.py
raise AssertionError('Loading only, executing fails')
''')
        test_loader = loader.TestLoader()
        suite = test_loader.discoverTests(
            't',
            file_loader_class=loader.ScriptLoader,
            dir_loader_class=loader.ScriptDirLoader)
        # Check which kind of tests have been discovered or we may miss regular
        # test cases seen as scripts.
        self.assertEqual(['t.regular.Test.test_in_init',
                          't.regular.foo.Test.test_me',
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
# '.p' is intentional, not a typoed '.py'
file: test_not_a_test.p
_hidden_too.py
''')
        test_loader = loader.TestLoader()
        suite = test_loader.discoverTests(
            '.',
            file_loader_class=loader.ScriptLoader,
            dir_loader_class=loader.ScriptDirLoader)
        self.assertEqual(['script1',
                          'script2',
                          'tests.test_real.Test_test_real.test_test_real',
                          'tests.test_real1.Test_test_real1.test_test_real1',
                          'tests.test_real2.Test_test_real2.test_test_real2'],
                         [t.id() for t in testtools.iterate_tests(suite)])


class TestTestLoaderPattern(tests.ImportingLocalFilesTest):

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
        test_loader = loader.TestLoader()
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
        test_loader = loader.TestLoader()
        suite = test_loader.discover('t', pattern='foo*.py')
        self.assertEqual(1, suite.countTestCases())


class TestTestLoaderTopLevelDir(testtools.TestCase):

    def setUp(self):
        super(TestTestLoaderTopLevelDir, self).setUp()
        # We build trees rooted in test_base_dir from which we will import
        tests.set_cwd_to_tmp(self)
        tests.protect_imports(self)

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
        test_loader = loader.TestLoader()
        suite = test_loader.discover('t', '*.py', self.test_base_dir)
        self.assertEqual(1, suite.countTestCases())

    def test_simple_file_in_a_dir_no_sys_path(self):
        self._create_foo_in_tests()
        test_loader = loader.TestLoader()
        e = self.assertRaises(ImportError,
                              test_loader.discover, 't', '*.py')
        self.assertEqual(e.message, 'No module named t')
