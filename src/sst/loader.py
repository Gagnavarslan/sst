#
#   Copyright (c) 2011-2013 Canonical Ltd.
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
import os
import re
import unittest
import unittest.loader

from sst import case


class DirLoader(object):

    def __init__(self, test_loader):
        """Load tests from a directory."""
        super(DirLoader, self).__init__()
        self.test_loader = test_loader

    def discover(self, cur, top=None):
        if top is None:
            top = cur
        paths = os.listdir(cur)
        tests = self.test_loader.suiteClass()
        for path in paths:
            # We don't care about the base name as we use only the full path
            path = os.path.join(top, path)
            tests = self.discover_path(path, top)
            if tests is not None:
                tests.addTests(tests)
        return tests

    def discover_path(self, path, top):
        loader = None
        if os.path.isfile(path):
            loader = self.test_loader.fileLoaderClass(self.test_loader)
        elif os.path.isdir(path):
            loader = self.test_loader.dirLoaderClass(self.test_loader)
        if loader:
            return loader.discover(path, top)
        return None


class PackageLoader(object):

    def discover(self, cur, top=None):
        if top is None:
            top = cur
        try:
            # FIXME: We should probably excludes '{cur}/__init__.py' from
            # the list of files to handle -- vila 2013-04-29
            package = self.test_loader.importFromPath(
                os.path.join(top, cur))
        except ImportError:
            # Explicitly raise the full exception with its backtrace. This
            # could easily be overwritten by daughter classes to handle
            # them differently (swallowing included ;)
            raise
        # Can we delegate to the package ?
        discover = getattr(package, 'discover', None)
        if discover is not None:
            # Since the user defined it, the package knows better
            return discover(self, cur)
        # Can we use the load_tests protocol ?
        load_tests = getattr(package, 'load_tests', None)
        if load_tests is not None:
            # FIXME: This swallows exceptions raise the by the user defined
            # 'load_test'. We may want to give awy to expose them instead (with
            # or without stopping the test loading) -- vila 2013-04-27
            return self.test_loader.loadTestsFromModule(package)
        # Anything else with that ?
        # Nothing for now, thanks

        # Let's delegate to super
        return super(PackageLoader, self).discover(cur)


def matches_regexp(regexp):
    include_re = re.compile(regexp)

    def matches(path):
        return bool(include_re.match(path))
    return matches


class FileLoader(object):

    included_re = None
    excluded_re = None

    def __init__(self, test_loader, includes=None, excludes=None):
        """Load tests from a file."""
        super(FileLoader, self).__init__()
        self.test_loader = test_loader
        if includes is not None:
            self.includes = includes
        if excludes is not None:
            self.excludes = excludes

    def discover(self, path, cur, top):
        """Return an empty test suite.

        This is mostly for documentation purposes, if a file contains material
        that can produce tests, a specific file loader should be defined to
        build tests from the file content.
        """
        # I know nothing about tests
        empty = self.test_loader.suiteClass()
        return empty

    def includes(self, path):
        return True

    def excludes(self, path):
        return False


class ModuleLoader(FileLoader):

    def __init__(self, test_loader, includes=None, excludes=None):
        if includes is None:
            # Default to python source files
            includes = matches_regexp('^.*\.py$')
        super(ModuleLoader, self).__init__(test_loader, includes, excludes)

    def discover(self, path, cur, top):
        empty = self.test_loader.suiteClass()
        if not self.includes(path):
            return empty
        if self.excludes(path):
            return empty
        module = self.test_loader.importFromPath(path)
        return self.test_loader.loadTestsFromModule(module)


class TestLoader(unittest.TestLoader):
    """Load test from an sst tree.

    This loader is able to load sst scripts and create test cases with the
    right sst specific attributes (browser, error handling, reporting).

    This also allows test case based modules to be loaded when appropriate.
    """

    dirLoaderClass = DirLoader
    fileLoaderClass = FileLoader

    def __init__(self, browser_factory=None,
                 screenshots_on=False, debug_post_mortem=False,
                 extended_report=False):
        super(TestLoader, self).__init__()
        self.browser_factory = browser_factory
        self.screenshots_on = screenshots_on
        self.debug_post_mortem = debug_post_mortem
        self.extended_report = extended_report

    def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        dir_loader = self.dirLoaderClass(self)
        return dir_loader.discover(start_dir)

    def importFromPath(self, path):
        mod_name = path.replace(os.path.sep, '.')
        if mod_name.endswith('.py'):
            mod_name = mod_name[:3]  # Remove the trailing '.py'
        module = __import__(mod_name)
        return module

    def loadTestsFromScript(self, dir_name, script_name):
        suite = self.suiteClass()
        # script specific test parametrization
        csv_path = os.path.join(dir_name, script_name.replace('.py', '.csv'))
        if os.path.isfile(csv_path):
            for row in case.get_data(csv_path):
                # row is a dictionary of variables that will magically appear
                # as globals in the script.
                test = self.loadTestFromScript(dir_name, script_name, row)
                suite.addTest(test)
        else:
            test = self.loadTestFromScript(dir_name, script_name)
            suite.addTest(test)
        return suite

    def loadTestFromScript(self, dir_name, script_name, context=None):
        test = case.SSTScriptTestCase(dir_name, script_name, context)

        # FIXME: We shouldn't have to set test attributes manually, something
        # smells wrong here. -- vila 2013-04-26
        test.browser_factory = self.browser_factory

        test.screenshots_on = self.screenshots_on
        test.debug_post_mortem = self.debug_post_mortem
        test.extended_report = self.extended_report

        return test
