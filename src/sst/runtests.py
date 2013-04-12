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
import datetime
import fnmatch
import HTMLTestRunner
import junitxmlrunner
import os
import pdb
import sys
import traceback

from unittest2 import (
    defaultTestLoader,
    TestSuite,
    TextTestRunner,
)

from selenium import webdriver
import testtools
import testtools.content

from sst import (
    actions,
    bmobproxy,
    config,
    context,
    xvfbdisplay,
)
from .actions import (
    EndTest
)


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

    test_dir = _get_full_path(test_dir)
    if not os.path.isdir(test_dir):
        msg = 'Specified directory %r does not exist' % test_dir
        print msg
        sys.exit(1)

    if browser_factory is None:
        # TODO: We could raise an error instead as providing a default value
        # makes little sense here -- vila 2013-04-11
        browser_factory = FirefoxFactory(False, None)

    shared_directory = find_shared_directory(test_dir, shared_directory)
    config.shared_directory = shared_directory
    sys.path.append(shared_directory)

    config.results_directory = _get_full_path('results')

    config.browsermob_enabled = browser_factory.browsermob_process is not None

    test_names = set(test_names)

    suites = get_suites(test_names, test_dir, shared_directory, collect_only,
                        browser_factory,
                        screenshots_on, failfast, debug,
                        extended=extended,
                        )

    alltests = TestSuite(suites)

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

    if report_format == 'xml':
        _make_results_dir()
        fp = file(os.path.join(config.results_directory, 'results.xml'), 'wb')
        # XXX failfast not supported in XMLTestRunner
        runner = junitxmlrunner.XMLTestRunner(output=fp, verbosity=2)

    elif report_format == 'html':
        _make_results_dir()
        fp = file(os.path.join(config.results_directory, 'results.html'), 'wb')
        runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp, title='SST Test Report', verbosity=2, failfast=failfast
        )

    else:
        runner = TextTestRunner(verbosity=2, failfast=failfast)

    try:
        runner.run(alltests)
    except KeyboardInterrupt:
        print >> sys.stderr, 'Test run interrupted'
    finally:
        # XXX should warn on cases that were specified but not found
        pass


def _get_full_path(path):
    return os.path.normpath(
        os.path.abspath(
            os.path.join(os.getcwd(), path)
        )
    )


def _make_results_dir():
    try:
        os.makedirs(config.results_directory)
    except OSError:
        pass  # already exists


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
                relpath = os.path.split(relpath)[0]

    return _get_full_path(shared_directory)


def get_suites(test_names, test_dir, shared_dir, collect_only,
               browser_factory,
               screenshots_on, failfast, debug,
               extended=False
               ):
    return [
        get_suite(
            test_names, root, collect_only,
            browser_factory,
            screenshots_on, failfast, debug,
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
        test_names = ['*',]
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
              screenshots_on, failfast, debug,
              extended=False):

    suite = TestSuite()

    for case in find_cases(test_names, test_dir):
        csv_path = os.path.join(test_dir, case.replace('.py', '.csv'))
        if os.path.isfile(csv_path):
            # reading the csv file now
            for row in get_data(csv_path):
                # row is a dictionary of variables
                suite.addTest(
                    get_case(
                        test_dir, case, browser_factory, screenshots_on, row,
                        failfast=failfast, debug=debug, extended=extended
                    )
                )
        else:
            suite.addTest(
                get_case(
                    test_dir, case, browser_factory, screenshots_on,
                    failfast=failfast, debug=debug, extended=extended
                )
            )

    return suite


def use_xvfb_server(test, xvfb=None):
    """Setup an xvfb server for a given test.

    :param xvfb: An Xvfb object to use. If none is supplied, default values are
        used to build it.

    :returns: The xvfb server used so tests can use the built one.
    """
    if xvfb is None:
        xvfb = xvfbdisplay.Xvfb()
    xvfb.start()
    test.addCleanup(xvfb.stop)
    return xvfb


def _make_useable_har_name(stem=''):
    now = datetime.now()
    timestamped_base = 'har-%s' % now.strftime('%Y-%m-%d_%H-%M-%S-%f')
    if stem:
        slug_name = ''.join(x for x in stem if x.isalnum())
        out_name = '%s-%s.har' % (timestamped_base, slug_name)
    else:
        out_name = '%s.har' % timestamped_base
        file_name = os.path.join(config.results_directory, out_name)
    return file_name


class BrowserFactory(object):
    """Handle browser creation for tests.

    One instance is used for a given test run 
    """

    webdriver_class = None
    browsermob_proxy = None

    def __init__(self, javascript_disabled, browsermob_process):
        super(BrowserFactory, self).__init__()
        self.javascript_disabled = javascript_disabled
        self.browsermob_process = browsermob_process

    def setup_for_test(self, test):
        """Setup the browser for the given test.

        Some browsers accept more options that are test (and browser) specific.

        Daughter classes should redefines this method to capture them.
        """
        pass

    def browser(self):
        """Create a browser based on previously collected options.

        Daughter classes should override this method if they need to provide
        more context.
        """
        return self.webdriver_class()

    def start_http_capture(self, captured_url=''):
        if self.browsermob_proxy is not None:
            self.captured_url = captured_url
            logger.debug('Capturing http traffic...')
            self.browsermob_proxy.new_har()

    def stop_http_capture(self):
        if self.browsermob_proxy is not None:
            logger.debug('Saving HAR output')
            actions._make_results_dir()
            self.browsermob_proxy.save_har(
                _make_useable_har_name(self.captured_url))


# FIXME: Missing tests -- vila 2013-04-11
class RemoteBrowserFactory(BrowserFactory):

    webdriver_class = webdriver.Remote

    def __init__(self, capabilities, remote_url):
        super(RemoteBrowserFactory, self).__init__()
        self.capabilities = capabilities
        self.remote_url = remote_url

    def browser(self):
        return self.webdriver_class(self.capabilities, self.remote_url)


# FIXME: Missing tests -- vila 2013-04-11
class ChromeFactory(BrowserFactory):

    webdriver_class = webdriver.Chrome


# FIXME: Missing tests -- vila 2013-04-11
class IeFactory(BrowserFactory):

    webdriver_class = webdriver.Ie


# FIXME: Missing tests -- vila 2013-04-11
class PhantomJSFactory(BrowserFactory):

    webdriver_class = webdriver.PhantomJS


# FIXME: Missing tests -- vila 2013-04-11
class OperaFactory(BrowserFactory):

    webdriver_class = webdriver.Opera


class FirefoxFactory(BrowserFactory):

    webdriver_class = webdriver.Firefox

    def setup_for_test(self, test):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('intl.accept_languages', 'en')
        if self.browsermob_process is not None:
            # FIXME: The proxy url shouldn't be hardcoded -- vila 2013-04-10
            self.browsermob_proxy = bmobproxy.BrowserMobProxy('localhost', 8080)
            selenium_proxy = webdriver.Proxy(
                {'httpProxy': self.browsermob_proxy.url})
            profile.set_proxy(selenium_proxy)
        if test.assume_trusted_cert_issuer:
            profile.set_preference('webdriver_assume_untrusted_issuer', False)
            profile.set_preference(
                'capability.policy.default.Window.QueryInterface', 'allAccess')
            profile.set_preference(
                'capability.policy.default.Window.frameElement.get',
                'allAccess')
        if test.javascript_disabled or self.javascript_disabled:
            profile.set_preference('javascript.enabled', False)
        self.profile = profile

    def browser(self):
        return self.webdriver_class(self.profile)


# FIXME: Missing tests -- vila 2013-04-11
browser_factories = {
    'Chrome': ChromeFactory,
    'Firefox': FirefoxFactory,
    'Ie': IeFactory,
    'Opera': OperaFactory,
    'PhantomJS': PhantomJSFactory,
}


class SSTTestCase(testtools.TestCase):
    """A test case that can use the sst framework."""

    xvfb = None
    xserver_headless = False

    browser_factory = FirefoxFactory(False, None)

    javascript_disabled = False
    assume_trusted_cert_issuer = False

    wait_timeout = 10
    wait_poll = 0.1
    base_url = None

    results_directory = _get_full_path('results')
    screenshots_on = False
    debug_post_mortem = False
    extended_report = False

    def shortDescription(self):
        return None

    def setUp(self):
        super(SSTTestCase, self).setUp()
        if self.base_url is not None:
            actions.set_base_url(self.base_url)
        actions._set_wait_timeout(self.wait_timeout, self.wait_poll)
        # Ensures sst.actions will find me
        actions._test = self
        if self.xserver_headless and self.xvfb is None:
            # If we need to run headless and no xvfb is already running, start
            # a new one for the current test, scheduling the shutdown for the
            # end of the test.
            self.xvfb = use_xvfb_server(self)
        config.results_directory = self.results_directory
        _make_results_dir()
        self.start_browser()
        self.addCleanup(self.stop_browser)
        if self.screenshots_on:
            self.addOnException(self.take_screenshot_and_page_dump)
        if self.debug_post_mortem:
            self.addOnException(
                self.print_exception_and_enter_post_mortem)
        if self.extended_report:
            self.addOnException(self.report_extensively)

    def start_browser(self):
        logger.debug('\nStarting browser')
        self.browser_factory.setup_for_test(self)
        self.browser = self.browser_factory.browser()
        logger.debug('Browser started: %s' % (self.browser.name))

    def stop_browser(self):
        logger.debug('Stopping browser')
        self.browser.quit()

    def take_screenshot_and_page_dump(self, exc_info):
        try:
            filename = 'screenshot-{0}.png'.format(self.id())
            actions.take_screenshot(filename)
        except Exception:
            # FIXME: Needs to be reported somehow ? -- vila 2012-10-16
            pass
        try:
            # also dump page source
            filename = 'pagesource-{0}.html'.format(self.id())
            actions.save_page_source(filename)
        except Exception:
            # FIXME: Needs to be reported somehow ? -- vila 2012-10-16
            pass

    def print_exception_and_enter_post_mortem(self, exc_info):
        exc_class, exc, tb = exc_info
        traceback.print_exception(exc_class, exc, tb)
        pdb.post_mortem(tb)

    def report_extensively(self, exc_info):
        exc_class, exc, tb = exc_info
        original_message = str(exc)
        try:
            current_url = actions.get_current_url()
        except Exception:
            current_url = 'unavailable'
        try:
            page_source = actions.get_page_source()
        except Exception:
            page_source = 'unavailable'
        self.addDetail(
            'Original exception',
            testtools.content.text_content('{0} : {1}'.format(
                exc.__class__.__name__, original_message)))
        self.addDetail('Current url',
                       testtools.content.text_content(current_url))
        self.addDetail('Page source',
                       testtools.content.text_content(page_source))


class SSTScriptTestCase(SSTTestCase):
    """Test case used internally by sst-run and sst-remote."""

    script_dir = '.'
    script_name = None

    def __init__(self, testMethod, context_row=None):
        super(SSTScriptTestCase, self).__init__('run_test_script')
        self.id = lambda: '%s.%s.%s' % (self.__class__.__module__,
                                        self.__class__.__name__, testMethod)
        if context_row is None:
            context_row = {}
        self.context = context_row

    def __str__(self):
        # Since we use run_test_script to encapsulate the call to the
        # compiled code, we need to override __str__ to get a proper name
        # reported.
        return "%s (%s.%s)" % (self.id(), self.__class__.__module__,
                               self.__class__.__name__)

    def shortDescription(self):
        # The description should be first line of the test method's docstring.
        # Since we have no real test method here, we override it to always
        # return none.
        return None

    def setUp(self):
        self.script_path = os.path.join(self.script_dir, self.script_name)
        sys.path.append(self.script_dir)
        self.addCleanup(sys.path.remove, self.script_dir)
        self._compile_script()
        # The script may override some settings. The default value for
        # JAVASCRIPT_DISABLED and ASSUME_TRUSTED_CERT_ISSUER are False, so if
        # the user mentions them in his script, it's to turn them on. Also,
        # getting our hands on the values used in the script is too hackish ;)
        if 'JAVASCRIPT_DISABLED' in self.code.co_names:
            self.javascript_disabled = True
        if 'ASSUME_TRUSTED_CERT_ISSUER' in self.code.co_names:
            self.assume_trusted_cert_issuer = True
        super(SSTScriptTestCase, self).setUp()
        # Start with default values
        actions.reset_base_url()
        actions._set_wait_timeout(10, 0.1)
        # Possibly inject parametrization from associated .csv file
        context.populate_context(self.context, self.script_path,
                                 self.browser.name, self.javascript_disabled)

    def _compile_script(self):
        with open(self.script_path) as f:
            source = f.read() + '\n'
        self.code = compile(source, self.script_path, 'exec')

    def run_test_script(self, result=None):
        # Run the test catching exceptions sstnam style
        try:
            exec self.code in self.context
        except EndTest:
            pass


def _has_classes(test_dir, entry):
    """Scan Python source file and check for a class definition."""
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
             context=None, failfast=False, debug=False, extended=False):
    # our naming convention for tests requires that script-based tests must
    # not begin with "test_*."  SSTTestCase class-based or other
    # unittest.TestCase based source files must begin with "test_*".
    # we also scan the source file to see if it has class definitions,
    # since script base cases normally don't, but TestCase class-based
    # tests always will.
    if entry.startswith('test_') and _has_classes(test_dir, entry):
        # load just the individual file's tests
        this_test = defaultTestLoader.discover(test_dir, pattern=entry)
    else:  # this is for script-based test
        name = entry[:-3]
        test_name = 'test_%s' % name
        this_test = SSTScriptTestCase(test_name, context)
        this_test.script_dir = test_dir
        this_test.script_name = entry
        this_test.browser_factory = browser_factory

        this_test.screenshots_on = screenshots_on
        this_test.debug_post_mortem = debug
        this_test.extended_report = extended

    return this_test


def get_data(csv_path):
    """
    Return a list of data dicts for parameterized testing.

      the first row (headers) match data_map key names.
      rows beneath are filled with data values.
    """
    rows = []
    print '  Reading data from %r...' % os.path.split(csv_path)[-1],
    row_num = 0
    with open(csv_path) as f:
        headers = f.readline().rstrip().split('^')
        headers = [header.replace('"', '') for header in headers]
        headers = [header.replace("'", '') for header in headers]
        for line in f:
            row = {}
            row_num += 1
            row['_row_num'] = row_num
            fields = line.rstrip().split('^')
            for header, field in zip(headers, fields):
                try:
                    value = ast.literal_eval(field)
                except ValueError:
                    value = field
                    if value.lower() == 'false':
                        value = False
                    if value.lower() == 'true':
                        value = True
                row[header] = value
            rows.append(row)
    print 'found %s rows' % len(rows)
    return rows
