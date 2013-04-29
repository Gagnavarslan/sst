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
import testtools

from sst import (
    loader,
    tests,
)


class TestMatchesRegexp(testtools.TestCase):

    def test_matches(self):
        matches = loader.matches_regexp('foo.*')
        self.assertTrue(matches('foo'))
        self.assertFalse(matches('bar'))
        self.assertTrue(matches('foobar'))
        self.assertFalse(matches('barfoo'))


class TestFileLoader(testtools.TestCase):

    def get_test_loader(self):
        return loader.TestLoader()

    def test_discover_nothing(self):
        tests.set_cwd_to_tmp(self)
        with open('foo', 'w') as f:
            f.write('bar\n')
        file_loader = loader.FileLoader(self.get_test_loader())
        suite = file_loader.discover('foo', '.', '.')
        self.assertEqual(0, suite.countTestCases())

    def test_default_includes(self):
        file_loader = loader.FileLoader(self.get_test_loader())
        self.assertTrue(file_loader.includes('foo'))

    def test_default_exclude(self):
        file_loader = loader.FileLoader(self.get_test_loader())
        self.assertFalse(file_loader.excludes('foo'))

    def test_provided_includes(self):
        file_loader = loader.FileLoader(
            self.get_test_loader(),
            includes=loader.matches_regexp('^.*foo$'))
        self.assertTrue(file_loader.includes('foo'))
        self.assertTrue(file_loader.includes('barfoo'))
        self.assertFalse(file_loader.includes('bar'))
        self.assertFalse(file_loader.includes('foobar'))

    def test_provided_excludes(self):
        file_loader = loader.FileLoader(
            self.get_test_loader(),
            excludes=loader.matches_regexp('^bar.*foo$'))
        self.assertTrue(file_loader.excludes('barfoo'))
        self.assertFalse(file_loader.excludes('foo'))


# FIXME: Missing tests for protect_imports, add a module, delete a module,
# modify? a module -- vila 2013-04-29
def protect_imports(test):
    # Protect sys.modules and sys.path to be able to test imports
    test.patch(sys, 'path', list(sys.path))
    orig_modules = sys.modules.copy()
    def cleanup_modules():
        # Remove all added modules
        added = [ m for m in sys.modules.keys() if m not in orig_modules ]
        if added:
            for m in added:
                del sys.modules[m]
        # Restore deleted or modified modules
        sys.modules.update(orig_modules)
    test.addCleanup(cleanup_modules)


class TestModuleLoader(testtools.TestCase):

    def setUp(self):
        super(TestModuleLoader, self).setUp()
        tests.set_cwd_to_tmp(self)
        protect_imports(self)
        sys.path.insert(0, self.test_base_dir)

    def get_test_loader(self):
        return loader.TestLoader()

    def test_default_includes(self):
        mod_loader = loader.ModuleLoader(self.get_test_loader())
        self.assertTrue(mod_loader.includes('foo.py'))
        self.assertTrue(mod_loader.includes('package/foo.py'))
        # We don't try to catch all non importable names, that's import job
        self.assertTrue(mod_loader.includes('package.py/foo.py'))
        # But we won't try to import a random file
        self.assertFalse(mod_loader.includes('foopy'))

    def test_discover_empty_file(self):
        with open('foo.py', 'w') as f:
            f.write('')
        mod_loader = loader.ModuleLoader(self.get_test_loader())
        suite = mod_loader.discover('foo.py', '.', '.')
        self.assertEqual(0, suite.countTestCases())

    def test_discover_invalid_file(self):
        with open('foo.py', 'w') as f:
            f.write("I'm no python code")
        mod_loader = loader.ModuleLoader(self.get_test_loader())
        self.assertRaises(SyntaxError, mod_loader.discover, 'foo.py', '.', '.')


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
