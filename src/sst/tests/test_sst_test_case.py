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


import cStringIO

import mock
import testtools

from sst import tests


class TestHandleExceptions(testtools.TestCase):

    def setUp(self):
        super(TestHandleExceptions, self).setUp()
        tests.set_cwd_to_tmp(self)
        self.result = testtools.TestResult()

    def get_handle_exceptions_test(self, with_screenshots=False,
                                   with_debug_post_mortem=False,
                                   with_extended_report=False):
        class ForHandleExceptionsTests(tests.SSTBrowserLessTestCase):

            screenshots_on = with_screenshots
            debug_post_mortem = with_debug_post_mortem
            extended_report = with_extended_report

            def test_it(self):
                """An always failing test."""
                self.assertTrue(False)

        return ForHandleExceptionsTests('test_it')

    @mock.patch('sst.actions.take_screenshot')
    @mock.patch('sst.actions.save_page_source')
    def test_screenshot_and_page_dump_on_failure_enabled(
            self, mock_page_dump, mock_screenshot):
        test = self.get_handle_exceptions_test(with_screenshots=True)
        test.run()
        mock_screenshot.assert_called_once_with(
            'screenshot-{0}.png'.format(test.id()))
        mock_page_dump.assert_called_once_with(
            'pagesource-{0}.html'.format(test.id()))

    def test_screenshot_and_page_dump_on_failure_disabled(self):
        test = self.get_handle_exceptions_test(with_screenshots=False)
        with mock.patch.object(test, 'take_screenshot_and_page_dump'):
            test.run()
            self.assertFalse(test.take_screenshot_and_page_dump.called)

    @mock.patch('pdb.post_mortem')
    @mock.patch('sys.stderr', new_callable=cStringIO.StringIO)
    def test_debug_post_mortem_enabled(self, mock_stderr, mock_post_mortem):
        test = self.get_handle_exceptions_test(with_debug_post_mortem=True)
        test.run()
        self.assertTrue(mock_stderr.getvalue().endswith,
                        'AssertionError: False is not true')
        # The traceback passed as a parameter to post_mortem depends on the
        # execution. Here we are just testing that it was called.
        mock_post_mortem.assert_called_with(mock.ANY)

    def test_debug_post_mortem_disabled(self):
        test = self.get_handle_exceptions_test(with_debug_post_mortem=False)
        with mock.patch.object(test, 'print_exception_and_enter_post_mortem'):
            test.run()
            self.assertFalse(test.print_exception_and_enter_post_mortem.called)

    def test_report_extensively_enabled(self):
        test = self.get_handle_exceptions_test(with_extended_report=True)
        result = testtools.TextTestResult(cStringIO.StringIO())
        result.startTestRun()
        test.run(result)
        result.stopTestRun()
        self.assertIn('Current url: {{{unavailable}}}',
                      result.stream.getvalue())
        self.assertIn(
            'Original exception: {{{AssertionError : False is not true}}}',
            result.stream.getvalue())
        self.assertIn('Page source: {{{unavailable}}}',
                      result.stream.getvalue())

    def test_report_extensively_disabled(self):
        test = self.get_handle_exceptions_test(with_extended_report=False)
        with mock.patch.object(test, 'report_extensively'):
            test.run()
            self.assertFalse(test.report_extensively.called)


class TestSkipping(testtools.TestCase):

    def test_is_skipped(self):

        class WillSkip(tests.SSTBrowserLessTestCase):

            def test_it(self):
                self.skip('test reason')

        test = WillSkip('test_it')
        result = testtools.TestResult()
        test.run(result)
        self.assertIn('test reason', result.skip_reasons)
