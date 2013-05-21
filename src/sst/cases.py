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
import os
import pdb
import testtools
import testtools.content


from sst import (
    actions,
    browsers,
    config,
    context,
    xvfbdisplay,
)
import traceback


logger = logging.getLogger('SST')


class SSTTestCase(testtools.TestCase):
    """A test case that can use the sst framework."""

    xvfb = None
    xserver_headless = False

    browser_factory = browsers.FirefoxFactory()

    javascript_disabled = False
    assume_trusted_cert_issuer = False

    wait_timeout = 10
    wait_poll = 0.1
    base_url = None

    results_directory = os.path.abspath('results')
    screenshots_on = False
    debug_post_mortem = False
    extended_report = False

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
            self.xvfb = xvfbdisplay.use_xvfb_server(self)
        config.results_directory = self.results_directory
        actions._make_results_dir()
        self.start_browser()
        self.addCleanup(self.stop_browser)
        if self.screenshots_on:
            self.addOnException(self.take_screenshot_and_page_dump)
        if self.debug_post_mortem:
            self.addOnException(
                self.print_exception_and_enter_post_mortem)
        if self.extended_report:
            self.addOnException(self.report_extensively)

    def shortDescription(self):
        # testools wrongly defines this as returning self.id(). Since we're not
        # using the short description (aka the first line of the test
        # docstring) (who is ? should we ?), we revert to the default behavior
        # so runners and results don't get mad.
        return None

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

    def __init__(self, script_dir, script_name, context_row=None):
        super(SSTScriptTestCase, self).__init__('run_test_script')
        self.script_dir = script_dir
        self.script_name = script_name
        self.script_path = os.path.join(self.script_dir, self.script_name)

        # pythonify the script path into a python path
        test_id = self.script_path.replace('.py', '')
        if test_id.startswith('./'):
            test_id = test_id[2:]
        self.id = lambda: '%s' % (test_id.replace(os.sep, '.'))
        if context_row is None:
            context_row = {}
        self.context = context_row

    def __str__(self):
        # Since we use run_test_script to encapsulate the call to the
        # compiled code, we need to override __str__ to get a proper name
        # reported.
        return "%s" % (self.id(),)

    def setUp(self):
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
        previous_context = context.store_context()
        self.addCleanup(context.restore_context, previous_context)
        context.populate_context(self.context, self.script_path,
                                 self.browser.name, self.javascript_disabled)

    def _compile_script(self):
        self.script_path = os.path.join(self.script_dir, self.script_name)
        with open(self.script_path) as f:
            source = f.read() + '\n'
        self.code = compile(source, self.script_path, 'exec')

    def run_test_script(self, result=None):
        # Run the test catching exceptions sstnam style
        try:
            exec self.code in self.context
        except actions.EndTest:
            pass


def get_data(csv_path):
    """
    Return a list of data dicts for parameterized testing.

    The first row (headers) match data_map key names. rows beneath are filled
    with data values.
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
