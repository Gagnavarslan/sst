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

- protect_imports will remove the loaded modules from sys.modules and restore
  sys.path.

Because the tests themselves shares this module name space, care must be taken
by tests to not use module names already used in the module. Most of tests
below therefore use 't' as the main directory because:
- we use python not lisp so using 't' is ok ;)
- it's short,
- it's unlikely to be imported by the module.

"""
import sys
import testtools
import unittest

from sst import (
    case,
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


def protect_imports(test):
    """Protect sys.modules and sys.path for the test duration.

    This is useful to test imports which modifies sys.modules or requires
    modifying sys.path.
    """
    # Protect sys.modules and sys.path to be able to test imports
    test.patch(sys, 'path', list(sys.path))
    orig_modules = sys.modules.copy()

    def cleanup_modules():
        # Remove all added modules
        added = [m for m in sys.modules.keys() if m not in orig_modules]
        if added:
            for m in added:
                del sys.modules[m]
        # Restore deleted or modified modules
        sys.modules.update(orig_modules)
    test.addCleanup(cleanup_modules)


class TestProtectImports(testtools.TestCase):

    def setUp(self):
        super(TestProtectImports, self).setUp()
        protect_imports(self)

    def run_successful_test(self, test):
        result = testtools.TestResult()
        test.run(result)
        self.assertTrue(result.wasSuccessful())

    def test_add_module(self):
        self.assertIs(None, sys.modules.get('foo', None))

        class Test(testtools.TestCase):

            def test_it(self):
                protect_imports(self)
                sys.modules['foo'] = 'bar'

        self.run_successful_test(Test('test_it'))
        self.assertIs(None, sys.modules.get('foo', None))

    def test_remove_module(self):
        self.assertIs(None, sys.modules.get('I_dont_exist', None))
        sys.modules['I_dont_exist'] = 'bar'

        class Test(testtools.TestCase):

            def test_it(self):
                protect_imports(self)
                self.assertEqual('bar', sys.modules['I_dont_exist'])
                del sys.modules['I_dont_exist']
        self.run_successful_test(Test('test_it'))
        self.assertEqual('bar', sys.modules['I_dont_exist'])

    def test_modify_module(self):
        self.assertIs(None, sys.modules.get('I_dont_exist', None))
        sys.modules['I_dont_exist'] = 'bar'

        class Test(testtools.TestCase):

            def test_it(self):
                protect_imports(self)
                self.assertEqual('bar', sys.modules['I_dont_exist'])
                sys.modules['I_dont_exist'] = 'qux'
        self.run_successful_test(Test('test_it'))
        self.assertEqual('bar', sys.modules['I_dont_exist'])

    def test_sys_path_restored(self):
        tests.set_cwd_to_tmp(self)
        inserted = self.test_base_dir
        self.assertFalse(inserted in sys.path)

        class Test(testtools.TestCase):

            def test_it(self):
                protect_imports(self)
                sys.path.insert(0, inserted)
        self.run_successful_test(Test('test_it'))
        self.assertFalse(inserted in sys.path)


class ImportingLocalFilesTest(testtools.TestCase):
    """Class for tests requiring import of locally generated files.

    This setup the tests working dir in a newly created temp dir and restore
    sys.modules and sys.path at the end of the test.
    """
    def setUp(self):
        super(ImportingLocalFilesTest, self).setUp()
        tests.set_cwd_to_tmp(self)
        protect_imports(self)
        sys.path.insert(0, self.test_base_dir)


class TestModuleLoader(ImportingLocalFilesTest):

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


class TestDirLoaderDiscoverPath(ImportingLocalFilesTest):

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


class TestPackageLoader(ImportingLocalFilesTest):

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
            f.write("'foo'^'bar'\n")
            f.write('1^baz\n')
            f.write('2^qux\n')
        suite = loader.TestLoader().loadTestsFromScript('.', 'foo.py')
        self.assertEqual(2, suite.countTestCases())

    def test_load_non_existing_script(self):
        suite = loader.TestLoader().loadTestsFromScript('.', 'foo.py')
        self.assertEqual(0, suite.countTestCases())


class TestScriptLoader(ImportingLocalFilesTest):

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


class TesScriptDirLoader(ImportingLocalFilesTest):

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


class TestTestLoader(ImportingLocalFilesTest):

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
import os
from sst import loader as sloader


def discover(loader, directory, name):
    return loader.discoverTestsFromPackage(__package__,
        os.path.join(directory, name),
        file_loader_class=sloader.ScriptLoader,
        dir_loader_class=sloader.ScriptDirLoader)

file: t/scripts/script.py
raise AssertionError('Loading only, executing fails')
''')
        test_loader = loader.TestLoader()
        suite = test_loader.discoverTests('t')
        self.assertEqual(2, suite.countTestCases())
        # Check which kind of tests have been discovered or we may miss regular
        # test cases seen as scripts.
        iter_tests = iter(suite)
        script_test_case = iter_tests.next()
        self.assertIs(case.SSTScriptTestCase, script_test_case.__class__)
        self.assertEqual('t/scripts/script.py', script_test_case.script_path)
        inner_suite = iter_tests.next()
        self.assertIs(unittest.TestSuite, inner_suite.__class__)
        iter_inner_suite = iter(inner_suite)
        test_case = iter_inner_suite.next()
        self.assertEqual(sys.modules['t.foo'].Test, test_case.__class__)
        self.assertEqual('t.foo.Test.test_me', test_case.id())

    def test_regular_below_scripts(self):
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
dir: t/regular
file: t/regular/__init__.py
import os
from sst import loader as sloader


def discover(loader, directory, name):
    return loader.discoverTestsFromPackage(__package__,
        os.path.join(directory, name),
        file_loader_class=sloader.ModuleLoader,
        dir_loader_class=sloader.PackageLoader)
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
        self.assertEqual(2, suite.countTestCases())
        # Check which kind of tests have been discovered or we may miss regular
        # test cases seen as scripts.
        iter_tests = iter(suite)
        script_test_case = iter_tests.next()
        self.assertIs(case.SSTScriptTestCase, script_test_case.__class__)
        self.assertEqual('t/script.py', script_test_case.script_path)
        inner_suite = iter_tests.next()
        self.assertIs(unittest.TestSuite, inner_suite.__class__)
        iter_inner_suite = iter(inner_suite)
        test_case = iter_inner_suite.next()
        self.assertIs(sys.modules['t.regular.foo'].Test, test_case.__class__)
        self.assertEqual('t.regular.foo.Test.test_me', test_case.id())


class TestTestLoaderPattern(ImportingLocalFilesTest):

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
        protect_imports(self)

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
