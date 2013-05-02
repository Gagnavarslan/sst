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

import ast
import logging
import fnmatch
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
    case,
    browsers,
    config,
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


def runtests(test_names, test_dir='.', collect_only=False,
             browser_factory=None,
             report_format='console',
             shared_directory=None, screenshots_on=False, failfast=False,
             debug=False,
             extended=False):

    if test_dir == 'selftests':
        # XXXX horrible hardcoding
        # selftests should be a command instead
        package_dir = os.path.dirname(__file__)
        test_dir = os.path.join(package_dir, 'selftests')

    if not os.path.isdir(test_dir):
        msg = 'Specified directory %r does not exist' % test_dir
        print msg
        sys.exit(1)

    if browser_factory is None:
        # TODO: We could raise an error instead as providing a default value
        # makes little sense here -- vila 2013-04-11
        browser_factory = browsers.FirefoxFactory()

    shared_directory = find_shared_directory(test_dir, shared_directory)
    config.shared_directory = shared_directory
    sys.path.append(shared_directory)

    config.results_directory = _get_full_path('results')

    test_names = set(test_names)

    suites = get_suites(test_names, test_dir, shared_directory, collect_only,
                        browser_factory,
                        screenshots_on, debug,
                        extended=extended,
                        )

    alltests = unittest.TestSuite(suites)

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
        for t in sorted(testtools.testsuite.iterate_tests(alltests)):
            print t.id()
        sys.exit(0)

    actions._make_results_dir()
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


def _get_full_path(relpath):
    return os.path.abspath(relpath)


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

    So I plan to remove the support for searching shared upwards in favor of
    allowing running a test subset and go with a sane layout and import
    behavior. No test fail if this feature is removed so it's not supported
    anyway. -- vila 2013-04-26
    """
    if shared_directory is not None:
        return _get_full_path(shared_directory)

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

    return _get_full_path(shared_directory)


def get_suites(test_names, test_dir, shared_dir, collect_only,
               browser_factory,
               screenshots_on, debug,
               extended=False
               ):
    return [
        get_suite(
            test_names, root, collect_only,
            browser_factory,
            screenshots_on, debug,
            extended=extended,
        )
        for root, _, _ in os.walk(test_dir, followlinks=True)
        if os.path.abspath(root) != shared_dir and
        not os.path.abspath(root).startswith(shared_dir + os.path.sep)
        and not os.path.split(root)[1].startswith('_')
    ]


def find_cases(test_names, test_dir):
    found = set()
    dir_list = os.listdir(test_dir)
    filtered_dir_list = set()
    if not test_names:
        test_names = ['*', ]
    for name_pattern in test_names:
        if not name_pattern.endswith('.py'):
            name_pattern += '.py'
        matches = fnmatch.filter(dir_list, name_pattern)
        if matches:
            for match in matches:
                if os.path.isfile(os.path.join(test_dir, match)):
                    filtered_dir_list.add(match)
    for entry in filtered_dir_list:
        # conditions for ignoring files
        if not entry.endswith('.py'):
            continue
        if entry.startswith('_'):
            continue
        found.add(entry)

    return found


def get_suite(test_names, test_dir, collect_only,
              browser_factory,
              screenshots_on, debug,
              extended=False):

    suite = unittest.TestSuite()

    for test_case in find_cases(test_names, test_dir):
        csv_path = os.path.join(test_dir, test_case.replace('.py', '.csv'))
        if os.path.isfile(csv_path):
            # reading the csv file now
            for row in case.get_data(csv_path):
                # row is a dictionary of variables
                suite.addTest(
                    get_case(test_dir, test_case, browser_factory,
                             screenshots_on,
                             row,
                             debug=debug, extended=extended))
        else:
            suite.addTest(
                get_case(test_dir, test_case, browser_factory, screenshots_on,
                         debug=debug, extended=extended))

    return suite


def _has_classes(test_dir, entry):
    """Scan Python source file and check for a class definition."""
    # FIXME: This is not enough, a script can very well define a class that
    # doesn't inherit from unittest.TestCase -- vila 2012-04-26
    with open(os.path.join(test_dir, entry)) as f:
        source = f.read() + '\n'
    found_classes = []

    def visit_class_def(node):
        found_classes.append(True)

    node_visitor = ast.NodeVisitor()
    node_visitor.visit_ClassDef = visit_class_def
    node_visitor.visit(ast.parse(source))
    return bool(found_classes)


def get_case(test_dir, entry, browser_factory, screenshots_on,
             context=None, debug=False, extended=False):
    # our naming convention for tests requires that script-based tests must
    # not begin with "test_*."  SSTTestCase class-based or other
    # unittest.TestCase based source files must begin with "test_*".
    # we also scan the source file to see if it has class definitions,
    # since script base cases normally don't, but TestCase class-based
    # tests always will.
    if entry.startswith('test_') and _has_classes(test_dir, entry):
        # load just the individual file's tests
        this_test = unittest.defaultTestLoader.discover(
            test_dir, pattern=entry, top_level_dir=test_dir)
    else:  # this is for script-based test
        this_test = case.SSTScriptTestCase(test_dir, entry, context)

        this_test.browser_factory = browser_factory

        this_test.screenshots_on = screenshots_on
        this_test.debug_post_mortem = debug
        this_test.extended_report = extended

    return this_test
