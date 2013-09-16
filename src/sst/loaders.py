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

import contextlib
import fnmatch
import functools
import os
import re
import sys
import unittest
import unittest.loader

from sst import cases


class NameMatcher(object):
    """Defines rules to select names.

    The rules are defined by two lists of regular expressions:
    - includes: matching succeeds if one of the regular expression match.
    - excludes: matching fails if one of the regular expression match.

    Matching fails if no rules are given.
    """

    def __init__(self, includes=None, excludes=None):
        self.includes = []
        if includes is not None:
            for inc in includes:
                self.includes.append(re.compile(inc))
        self.excludes = []
        if excludes is not None:
            for exc in excludes:
                self.excludes.append(re.compile(exc))

    def matches(self, name):
        for exc in self.excludes:
            if exc.search(name):
                return False
        for inc in self.includes:
            if inc.search(name):
                return True
        # Not explicitely included
        return False


@contextlib.contextmanager
def NameMatchers(test_loader, file_matcher=None, dir_matcher=None):
    """A context manager for loading tests from a tree.

    This is mainly used when walking a tree and requiring a different set of
    name matchers for a subtree.
    """
    if file_matcher is None:
        file_matcher = test_loader.file_matcher
    if dir_matcher is None:
        dir_matcher = test_loader.dir_matcher
    orig = (test_loader.file_matcher, test_loader.dir_matcher)
    try:
        test_loader.file_matcher = file_matcher
        test_loader.dir_matcher = dir_matcher
        # 'test_loader' will now use the specified file/dir matchers
        yield test_loader
    finally:
        (test_loader.file_matcher, test_loader.dir_matcher) = orig


class TestLoader(unittest.TestLoader):
    """Load tests from an arbitrary tree.

    This also provides ways for packages to define the test discovery and
    loading as they see fit.

    Sorting happens on base names inside a directory while walking the tree and
    on test classes and test method names when loading a module. Those sortings
    combined provide a test suite where test ids are sorted.
    """

    file_matcher = NameMatcher(includes=[r'^test.*\.py$'])
    dir_matcher = NameMatcher(includes=[r'.*'])

    def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        if top_level_dir:
            # For backward compatibility we insert top_level_dir in
            # sys.path. More complex import rules are left to the caller to
            # setup properly
            sys.path.insert(0, top_level_dir)

        translated = NameMatcher(includes=['^' + fnmatch.translate(pattern)])
        with NameMatchers(self, file_matcher=translated) as tl:
            return tl.discoverTestsFromTree(start_dir)

    def discoverTestsFromTree(self, dir_path, package=None):
        suite = self.suiteClass()
        names = os.listdir(dir_path)
        if package is None:
            if os.path.isfile(os.path.join(dir_path, '__init__.py')):
                package = self.importFromPath(dir_path)
                names.remove('__init__.py')
        if package is not None:
            # Can we delegate to the package ?
            discover = getattr(package, 'discover', None)
            if discover is not None:
                # Since the user defined it, the package knows better
                suite.addTests(discover(self, package, dir_path, names))
                return suite
            load_tests = getattr(package, 'load_tests', None)
            if load_tests is not None:
                # let unittest handle the 'load_tests' protocol
                suite.addTests(self.loadTestsFromModule(package))
                return suite
            # If tests are defined in the package, load them
            suite.addTests(self.loadTestsFromModule(package))
        suite.addTests(self.discoverTestsFromNames(dir_path, names))
        return suite

    def discoverTestsFromNames(self, dir_path, names):
        # Walk the tree to discover the tests
        suite = self.suiteClass()
        for name in self.sortNames(names):
            path = os.path.join(dir_path, name)
            if os.path.isfile(path) and self.file_matcher.matches(name):
                suite.addTests(self.discoverTestsFromFile(path))
            elif os.path.isdir(path) and self.dir_matcher.matches(name):
                suite.addTests(self.discoverTestsFromTree(path))
        return suite

    def discoverTestsFromFile(self, path):
        module = self.importFromPath(path)
        return self.loadTestsFromModule(module)

    def sortNames(self, names):
        """Return 'names' sorted as defined by sortTestMethodsUsing.

        It's a little abuse of sort*TestMethods*Using as we're sorting file
        names (or even module python paths) but it allows providing a
        consistent order for the whole suite.
        """
        return sorted(names,
                      key=functools.cmp_to_key(self.sortTestMethodsUsing))

    def importFromPath(self, path):
        path = os.path.normpath(path)
        if path.endswith('.py'):
            path = path[:-3]  # Remove the trailing '.py'
        mod_name = path.replace(os.path.sep, '.')
        __import__(mod_name)
        return sys.modules[mod_name]


class SSTestLoader(TestLoader):
    """Load tests from an sst tree.

    This loader is able to load sst scripts and create test cases with the
    right sst specific attributes (browser, error handling, reporting).

    This also allows test case based modules to be loaded when appropriate.

    The main differences with unittest test loader are around different rules
    for file names that can contain tests and importing rules (a script *should
    not* be imported at load time).

    Scripts can be organized in a tree where directories are not python
    packages. Since scripts are not imported, they don't require the
    directories containing them to be packages. Although as soon a test suite
    becomes complex enough to be organized as a tree, it generally requires the
    packages to be importable.
    """

    file_matcher = NameMatcher(includes=[r'.*\.py$'], excludes=[r'^_'])
    dir_matcher = NameMatcher(includes=[r'.*'], excludes=[r'^_', '^shared$'])

    def __init__(self, results_directory=None, browser_factory=None,
                 screenshots_on=False, debug_post_mortem=False,
                 extended_report=False):
        super(SSTestLoader, self).__init__()
        self.results_directory = results_directory
        self.browser_factory = browser_factory
        self.screenshots_on = screenshots_on
        self.debug_post_mortem = debug_post_mortem
        self.extended_report = extended_report

    def discoverTestsFromFile(self, path):
        return self.loadTestsFromScript(path)

    def loadTestsFromScript(self, path):
        suite = self.suiteClass()
        dir_name, script_name = os.path.split(path)
        if not os.path.isfile(path):
            return suite
        # script specific test parametrization
        csv_path = path.replace('.py', '.csv')
        if os.path.isfile(csv_path):
            for row in cases.get_data(csv_path):
                # row is a dictionary of variables that will magically appear
                # as globals in the script.
                test = self.loadTestFromScript(dir_name, script_name, row)
                suite.addTest(test)
        else:
            test = self.loadTestFromScript(dir_name, script_name)
            suite.addTest(test)
        return suite

    def loadTestFromScript(self, dir_name, script_name, context=None):
        test = cases.SSTScriptTestCase(dir_name, script_name, context)

        # FIXME: We shouldn't have to set test attributes manually, something
        # smells wrong here. -- vila 2013-04-26
        test.results_directory = self.results_directory
        test.browser_factory = self.browser_factory

        test.screenshots_on = self.screenshots_on
        test.debug_post_mortem = self.debug_post_mortem
        test.extended_report = self.extended_report

        return test


def discoverTestScripts(test_loader, package, directory, names):
    """``discover`` helper to load sst scripts.

    This can be used in a __init__.py file while walking a regular tests tree.
    """
    return SSTestLoader().discoverTestsFromNames(directory, names)


def discoverRegularTests(test_loader, package, directory, names):
    """``discover`` helper to load regular python files defining tests.

    This can be used in a __init__.py file while walking an sst tests tree.
    """
    return TestLoader().discoverTestsFromNames(directory, names)


def discoverNoTests(test_loader, package, directory, names):
    """Returns an empty test suite.

    This can be used in a __init__.py file to prune the test loading for a
    given subtree.
    """
    return test_loader.suiteClass()
