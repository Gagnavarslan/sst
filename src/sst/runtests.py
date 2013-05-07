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

import fnmatch
import logging
import htmlrunner
import junitxmlrunner
import os
import sys
import unittest
import unittest.loader


import testtools
import testtools.content

from sst import (
    actions,
    browsers,
    case,
    config,
    loader,
)

# Maintaining compatibility until we deprecate the followings
BrowserFactory = browsers.BrowserFactory
RemoteBrowserFactory = browsers.RemoteBrowserFactory
ChromeFactory = browsers.ChromeFactory
IeFactory = browsers.IeFactory
PhantomJSFactory = browsers.PhantomJSFactory
OperaFactory = browsers.OperaFactory
FirefoxFactory = browsers.FirefoxFactory
browser_factories = browsers.browser_factories
SSTTestCase = case.SSTTestCase
SSTScriptTestCase = case.SSTScriptTestCase


__all__ = ['runtests']

logger = logging.getLogger('SST')


# MISSINGTEST: 'shared' relationship with test_dir, auto-added to sys.path or
# not -- vila 2013-05-05
# MISSINGTEST: 'results' dir, created in current dir unconditionally conflicts
# with claim that 'shared' can be found somewhere up -- vila 2013-05-05
def runtests(test_names, test_dir='.', collect_only=False,
             browser_factory=None,
             report_format='console',
             shared_directory=None, screenshots_on=False, failfast=False,
             debug=False,
             extended=False,
             includes=None,
             excludes=None):

    config.results_directory = os.path.abspath('results')
    actions._make_results_dir()

    if test_dir == 'selftests':
        # XXXX horrible hardcoding
        # selftests should be a command instead
        package_dir = os.path.dirname(__file__)
        os.chdir(os.path.dirname(package_dir))
        test_dir = os.path.join('.', 'sst', 'selftests')
    else:
        if not os.path.isdir(test_dir):
            msg = 'Specified directory %r does not exist' % test_dir
            print msg
            sys.exit(1)
    shared_directory = find_shared_directory(test_dir, shared_directory)
    config.shared_directory = shared_directory
    sys.path.append(shared_directory)

    if browser_factory is None:
        # TODO: We could raise an error instead as providing a default value
        # makes little sense here -- vila 2013-04-11
        browser_factory = browsers.FirefoxFactory()

    test_loader = loader.TestLoader(browser_factory, screenshots_on,
                                    debug, extended)
    alltests = test_loader.suiteClass()
    alltests.addTests(
        test_loader.discoverTests(test_dir,
                                  file_loader_class=loader.ScriptLoader,
                                  dir_loader_class=loader.ScriptDirLoader))

    def filter_test_names(name):
        if not test_names:
            return True
        for pattern in test_names:
            if fnmatch.fnmatchcase(name, pattern):
                return True
        return False

    alltests = loader.filter_suite(filter_test_names, alltests)

    if includes:
        def starts_with_one_of(test):
            # A test is kept if its id matches one of the 'includes' prefixes
            tid = test.id()
            for inc in includes:
                if tid.startswith(inc):
                    return True
            return False
        alltests = loader.filter_suite(starts_with_one_of, alltests)
    if excludes:
        def starts_with_none_of(test):
            # A test is kept if its id matches none of the 'excludes' prefixes
            tid = test.id()
            for ex in excludes:
                if tid.startswith(ex):
                    return False
            return True
        alltests = loader.filter_suite(starts_with_none_of, alltests)

    print ''
    print '  %s test cases loaded\n' % alltests.countTestCases()
    print '--------------------------------------------------------------'

    if not alltests.countTestCases():
        print 'Error: Did not find any tests'
        sys.exit(1)

    if collect_only:
        print 'Collect-Only Enabled, Not Running Tests...\n'
        print 'Tests Collected:'
        print '-' * 16
        for t in testtools.testsuite.iterate_tests(alltests):
            print t.id()
        return

    if report_format == 'xml':
        fp = file(os.path.join(config.results_directory, 'results.xml'), 'wb')
        # XXX failfast not supported in XMLTestRunner
        runner = junitxmlrunner.XMLTestRunner(output=fp, verbosity=2)

    elif report_format == 'html':
        fp = file(os.path.join(config.results_directory, 'results.html'), 'wb')
        runner = htmlrunner.HTMLTestRunner(
            stream=fp, title='SST Test Report', verbosity=2, failfast=failfast
        )

    else:
        runner = unittest.TextTestRunner(verbosity=2, failfast=failfast)

    try:
        runner.run(alltests)
    except KeyboardInterrupt:
        print >> sys.stderr, 'Test run interrupted'
    finally:
        # XXX should warn on cases that were specified but not found
        pass


def find_shared_directory(test_dir, shared_directory):
    """This function is responsible for finding the shared directory.
    It implements the following rule:

    If a shared directory is explicitly specified then that is used.

    The test directory is checked first. If there is a shared directory
    there, then that is used.

    If the current directory is not "above" the test directory then the
    function bails.

    Otherwise it checks every directory from the test directory up to the
    current directory. If it finds one with a "shared" directory then it
    uses that as the shared directory and returns.

    The intention is that if you have 'tests/shared' and 'tests/foo' you
    run `sst-run -d tests/foo` and 'tests/shared' will still be used as
    the shared directory.

    IMHO the above is only needed because we don't allow:
    sst-run --start with tests.foo

    So I plan to remove the support for searching 'shared' upwards in favor of
    allowing running a test subset and go with a sane layout and import
    behavior. No test fail if this feature is removed so it's not supported
    anyway. -- vila 2013-04-26
    """
    if shared_directory is not None:
        return os.path.abspath(shared_directory)

    cwd = os.getcwd()
    default_shared = os.path.join(test_dir, 'shared')
    shared_directory = default_shared
    if not os.path.isdir(default_shared):
        relpath = os.path.relpath(test_dir, cwd)
        if not relpath.startswith('..') and not os.path.isabs(relpath):
            while relpath and relpath != os.curdir:
                this_shared = os.path.join(cwd, relpath, 'shared')
                if os.path.isdir(this_shared):
                    shared_directory = this_shared
                    break
                relpath = os.path.dirname(relpath)

    return os.path.abspath(shared_directory)
