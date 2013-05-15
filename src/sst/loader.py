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


def matches_for_regexp(regexp):
    match_re = re.compile(regexp)

    def matches(path):
        return bool(match_re.match(path))
    return matches


def matches_for_glob(pattern):
    match_re = fnmatch.translate(pattern)
    return matches_for_regexp(match_re)


class NameMatcher(object):

    def __init__(self, includes=None, excludes=None):
        if includes is not None:
            self.includes = includes
        if excludes is not None:
            self.excludes = excludes

    def includes(self, path):
        return True

    def excludes(self, path):
        return False

    def matches(self, name):
        return self.includes(name) and not self.excludes(name)


class FileLoader(object):
    """Load tests from a file.

    This is an abstract class allowing daughter classes to enforce constraints
    including the ability to load tests from files that cannot be imported.
    """

    def __init__(self, test_loader, matcher=None):
        """Load tests from a file."""
        super(FileLoader, self).__init__()
        if matcher is None:
            self.matches = lambda name: True
        else:
            self.matches = matcher.matches
        self.test_loader = test_loader

    def discover(self, directory, name):
        """Return None to represent an empty test suite.

        This is mostly for documentation purposes, if a file contains material
        that can produce tests, a specific file loader should be defined to
        build tests from the file content.
        """
        return None


class ModuleLoader(FileLoader):
    """Load tests from a python module.

    This handles base name matching and loading tests defined in an importable
    python module.
    """

    def __init__(self, test_loader, matcher=None):
        if matcher is None:
            # Default to python source files, excluding private ones
            matcher = NameMatcher(includes=matches_for_regexp('.*\.py$'),
                                  excludes=matches_for_regexp('^_'))
        super(ModuleLoader, self).__init__(test_loader, matcher=matcher)

    def discover(self, directory, name):
        if not self.matches(name):
            return None
        module = self.test_loader.importFromPath(os.path.join(directory, name))
        return self.test_loader.loadTestsFromModule(module)


class ScriptLoader(FileLoader):
    """Load tests from an sst script.

    This handles base name matching and loading tests defined in an sst script.
    """

    def __init__(self, test_loader, matcher=None):
        if matcher is None:
            # Default to python source files, excluding private ones
            matcher = NameMatcher(includes=matches_for_regexp('.*\.py$'),
                                  excludes=matches_for_regexp('^_'))
        super(ScriptLoader, self).__init__(test_loader, matcher=matcher)

    def discover(self, directory, name):
        if not self.matches(name):
            return None
        return self.test_loader.loadTestsFromScript(directory, name)


class DirLoader(object):
    """Load tests from a tree.

    This is an abstract class allowing daughter classes to enforce constraints
    including the ability to load tests from files and directories that cannot
    be imported.
    """

    def __init__(self, test_loader, matcher=None):
        """Load tests from a directory."""
        super(DirLoader, self).__init__()
        if matcher is None:
            # Accept everything
            self.matches = lambda name: True
        else:
            self.matches = matcher.matches
        self.test_loader = test_loader

    def discover(self, directory, name):
        if not self.matches(name):
            return None
        path = os.path.join(directory, name)
        names = os.listdir(path)
        names = self.test_loader.sortNames(names)
        return self.discover_names(path, names)

    def discover_names(self, directory, names):
        suite = self.test_loader.suiteClass()
        for name in names:
            tests = self.discover_path(directory, name)
            if tests is not None:
                suite.addTests(tests)
        return suite

    def discover_path(self, directory, name):
        loader = None
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            loader = self.test_loader.fileLoaderClass(self.test_loader)
        elif os.path.isdir(path):
            loader = self.test_loader.dirLoaderClass(self.test_loader)
        if loader is not None:
            return loader.discover(directory, name)
        return None


class ScriptDirLoader(DirLoader):
    """Load tests for a tree containing scripts.

    Scripts can be organized in a tree where directories are not python
    packages. Since scripts are not imported, they don't require the
    directories containing them to be packages.
    """

    def __init__(self, test_loader, matcher=None):
        if matcher is None:
            # Excludes the 'shared' directory and the "private" directories
            regexp = '^shared$|^_'
            matcher = NameMatcher(excludes=matches_for_regexp(regexp))
        super(ScriptDirLoader, self).__init__(test_loader, matcher=matcher)

    def discover_path(self, directory, name):
        # MISSINGTEST: The behavior is unclear when a module cannot be imported
        # because sys.path is incomplete. This makes it hard for the user to
        # understand it should update sys.path -- vila 2013-05-05
        path = os.path.join(directory, name)
        if (os.path.isdir(path) and os.path.isfile(
                os.path.join(path, '__init__.py'))):
            # Hold on, we need to respect users wishes here (if it has some)
            loader = PackageLoader(self.test_loader)
            try:
                return loader.discover(directory, name)
            except ImportError:
                # FIXME: Nah, didn't work, should we report it to the user ?
                # (yes see MISSINGTEST above) How ? (By re-raising with a
                # proper message: if there is an __init__.py file here, it
                # should be importable, that's what we should explain to the
                # user) vila 2013-05-04
                pass
        return super(ScriptDirLoader, self).discover_path(directory, name)


class PackageLoader(DirLoader):
    """Load tests for a package.

    A package provides a way for the user to specify how tests are loaded.
    """

    def discover(self, directory, name):
        if not self.matches(name):
            return None
        path = os.path.join(directory, name)
        try:
            package = self.test_loader.importFromPath(path)
        except ImportError:
            # Explicitly raise the full exception with its backtrace. This
            # could be overwritten by daughter classes to handle them
            # differently (swallowing included ;)
            raise
        # Can we delegate to the package ?
        discover = getattr(package, 'discover', None)
        if discover is not None:
            # Since the user defined it, the package knows better
            return discover(self.test_loader, package,
                            os.path.join(directory, name))
        # Can we use the load_tests protocol ?
        load_tests = getattr(package, 'load_tests', None)
        if load_tests is not None:
            # FIXME: This swallows exceptions raised the by the user defined
            # 'load_test'. We may want to give a way to expose them instead
            # (with or without stopping the test loading) -- vila 2013-04-27
            return self.test_loader.loadTestsFromModule(package)
        # Anything else with that ?
        # Nothing for now, thanks

        names = os.listdir(path)
        names.remove('__init__.py')
        names = self.test_loader.sortNames(names)
        return self.discover_names(path, names)


@contextlib.contextmanager
def Loaders(test_loader, file_loader_class, dir_loader_class):
    """A context manager for loading tests from a tree.

    This is mainly used when walking a tree a requiring a different set of
    loaders for a subtree.
    """
    if file_loader_class is None:
        file_loader_class = test_loader.fileLoaderClass
    if dir_loader_class is None:
        dir_loader_class = test_loader.dirLoaderClass
    orig = (test_loader.fileLoaderClass, test_loader.dirLoaderClass)
    try:
        test_loader.fileLoaderClass = file_loader_class
        test_loader.dirLoaderClass = dir_loader_class
        # 'test_loader' will now use the specified file/dir loader classes
        yield
    finally:
        (test_loader.fileLoaderClass, test_loader.dirLoaderClass) = orig


class TestLoader(unittest.TestLoader):
    """Load tests from an sst tree.

    This loader is able to load sst scripts and create test cases with the
    right sst specific attributes (browser, error handling, reporting).

    This also allows test case based modules to be loaded when appropriate.

    This also provides ways for packages to define the test loading as they see
    fit.

    Sorting happens on base names inside a directory while walking the tree and
    on test classes and test method names when loading a module. Those sortings
    combined provide a test suite where test ids are sorted.
    """

    dirLoaderClass = PackageLoader
    fileLoaderClass = ModuleLoader

    def __init__(self, browser_factory=None,
                 screenshots_on=False, debug_post_mortem=False,
                 extended_report=False):
        super(TestLoader, self).__init__()
        self.browser_factory = browser_factory
        self.screenshots_on = screenshots_on
        self.debug_post_mortem = debug_post_mortem
        self.extended_report = extended_report

    def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        if top_level_dir:
            # For backward compatibility we insert top_level_dir in
            # sys.path. More complex import rules are left to the caller to
            # setup properly
            sys.path.insert(0, top_level_dir)

        class ModuleLoaderFromPattern(ModuleLoader):

            def __init__(self, test_loader):
                matcher = NameMatcher(includes=matches_for_glob(pattern))
                super(ModuleLoaderFromPattern, self).__init__(
                    test_loader, matcher=matcher)

        return self.discoverTests(start_dir,
                                  file_loader_class=ModuleLoaderFromPattern)

    def discoverTests(self, start_dir, file_loader_class=None,
                      dir_loader_class=None):
        with Loaders(self, file_loader_class, dir_loader_class):
            dir_loader = self.dirLoaderClass(self)
            return dir_loader.discover(*os.path.split(start_dir))

    def discoverTestsFromPackage(self, package, path, file_loader_class=None,
                                 dir_loader_class=None):
        suite = self.suiteClass()
        suite.addTests(self.loadTestsFromModule(package))
        names = os.listdir(path)
        names.remove('__init__.py')
        names = self.sortNames(names)
        with Loaders(self, file_loader_class, dir_loader_class):
            dir_loader = self.dirLoaderClass(self)
            suite.addTests(dir_loader.discover_names(path, names))
        return suite

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

    def loadTestsFromScript(self, dir_name, script_name):
        suite = self.suiteClass()
        path = os.path.join(dir_name, script_name)
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
        test.browser_factory = self.browser_factory

        test.screenshots_on = self.screenshots_on
        test.debug_post_mortem = self.debug_post_mortem
        test.extended_report = self.extended_report

        return test


def discoverTestScripts(test_loader, package, directory):
    """``discover`` helper to load sst scripts.

    This can be used in a __init__.py file while walking a regular tests tree.
    """
    return test_loader.discoverTestsFromPackage(
        package, directory,
        file_loader_class=ScriptLoader, dir_loader_class=ScriptDirLoader)


def discoverRegularTests(test_loader, package, directory):
    """``discover`` helper to load regular python files defining tests.

    This can be used in a __init__.py file while walking an sst tests tree.
    """
    return test_loader.discoverTestsFromPackage(
        package, directory,
        file_loader_class=ModuleLoader, dir_loader_class=PackageLoader)


def discoverNoTests(test_loader, *args, **kwargs):
    """Returns an empty test suite.

    This can be used in a __init__.py file to prune the test loading for a
    given subtree.
    """
    return test_loader.suiteClass()
