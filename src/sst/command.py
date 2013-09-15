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

from __future__ import print_function

import errno
import logging
import optparse
import os
import sys
import shutil
import traceback

import sst
from sst import (
    actions,
    browsers,
    config,
)


usage = """Usage: %prog [options] [regexps]

* Calling sst-run with test regular expression(s) as argument(s) will run
  the tests whose test name(s) match the regular expression(s).

* You may optionally create data file(s) for data-driven testing.  Create a
  '^' delimited txt data file with the same name as the test script, plus
  the '.csv' extension.  This will run a test script using each row in the
  data file (1st row of data file is variable name mapping)
"""


def reset_directory(path):
    try:
        shutil.rmtree(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    os.makedirs(path)


def get_common_options():
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', dest='dir_name',
                      default='.',
                      help='directory of test case files')
    parser.add_option('-r', dest='report_format',
                      default='console',
                      help='report type: xml')
    parser.add_option('-b', dest='browser_type',
                      default='Firefox',
                      help=('select webdriver (Firefox, Chrome, '
                            'PhantomJS, etc)'))
    parser.add_option('-m', dest='shared_directory',
                      default=None,
                      help='directory for shared modules')
    parser.add_option('-q', dest='quiet', action='store_true',
                      default=False,
                      help='output less debugging info during test run')
    parser.add_option('-V', dest='print_version', action='store_true',
                      default=False,
                      help='print version info and exit')
    parser.add_option('-s', dest='screenshots_on', action='store_true',
                      default=False,
                      help='save screenshots on failures')
    parser.add_option('--failfast',
                      action='store_true', default=False,
                      help='stop test execution after first failure')
    parser.add_option('--debug',
                      action='store_true', default=False,
                      help='drop into debugger on test fail or error')
    parser.add_option('--with-flags', dest='with_flags',
                      help='comma separated list of flags to run '
                      'tests with')
    parser.add_option('--disable-flag-skips', dest='disable_flags',
                      action='store_true', default=False,
                      help='run all tests, disable skipping tests due '
                      'to flags')
    parser.add_option('--extended-tracebacks', dest='extended_tracebacks',
                      action='store_true', default=False,
                      help='add extra information (page source) to failure'
                      ' reports')
    parser.add_option('--collect-only', dest='collect_only',
                      action='store_true', default=False,
                      help='collect/print cases without running tests')
    parser.add_option('-e', '--exclude', dest='excludes',
                      action='append',
                      help='all tests matching this regex will not be run')
    return parser


def get_run_options():
    parser = get_common_options()
    parser.add_option('-x', dest='xserver_headless',
                      default=False, action='store_true',
                      help='run browser in headless xserver (Xvfb)')
    parser.add_option('-c', '--concurrency', dest='concurrency',
                      default=1, type='int',
                      help='concurrency (number of procs)')
    return parser


def get_remote_options():
    parser = get_common_options()
    parser.add_option('-p', dest='browser_platform',
                      default='ANY',
                      help=('desired platform (XP, VISTA, LINUX, etc), '
                            'when using a remote Selenium RC'))
    parser.add_option('-v', dest='browser_version',
                      default='',
                      help=('desired browser version, when using a '
                            'remote Selenium'))
    parser.add_option('-n', dest='session_name',
                      default=None,
                      help=('identifier for this test run session, '
                            'when using a remote Selenium RC'))
    parser.add_option('-u', dest='webdriver_remote_url',
                      default=None,
                      help=('url to WebDriver endpoint '
                            '(eg: http://host:port/wd/hub), '
                            'when using a remote Selenium RC'))
    return parser


def get_opts_run(args=None):
    return get_opts(get_run_options, args)


def get_opts_remote(args=None):
    return get_opts(get_remote_options, args)


def get_opts(get_options, args=None):
    parser = get_options()
    (cmd_opts, args) = parser.parse_args(args)

    if cmd_opts.print_version:
        print('SST version: %s' % sst.__version__)
        sys.exit()

    if cmd_opts.browser_type not in browsers.browser_factories:
        print('Error: %s should be one of %s' %
              cmd_opts.browser_type, browsers.browser_factories.keys())
        sys.exit(1)

    logging.basicConfig(format='    %(levelname)s:%(name)s:%(message)s')
    logger = logging.getLogger('SST')
    if cmd_opts.quiet:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.DEBUG)
    # FIXME: We shouldn't be modifying anything in the 'actions' module, this
    # violates isolation and will make it hard to test. -- vila 2013-04-10
    if cmd_opts.disable_flags:
        actions._check_flags = False

    with_flags = cmd_opts.with_flags
    config.flags = [flag.lower() for flag in
                    ([] if not with_flags else with_flags.split(','))]
    return (cmd_opts, args)


class Cleaner(object):
    """Store cleanup callables in a stack.

    This allows deferring cleanups until a processing end while setting up an
    environment.
    """

    def __init__(self, stream=None):
        self.stream = stream
        self.cleanups = []

    def add(self, msg, func, *args, **kwargs):
        """Add a cleanup callable.

        :param msg: A message to write into the stream when the callable is
            called.

        :param func: The callable.

        :param args: An optional list of arguments to pass to func.

        :param kwargs: An optional dict of arguments to pass to func.
        """
        self.cleanups.insert(0, (msg, func, args, kwargs))

    def _write(self, msg):
        if self.stream is not None:
            self.stream.write(msg)

    def cleanup_now(self):
        """Run cleanups last added first.

        If exceptions occur, they are written to the stream but not propagated.
        """
        for msg, func, args, kwargs in self.cleanups:
            self._write(msg)
            try:
                func(*args, **kwargs)
            except Exception:
                # Note that since we catch Exception, KeyboardInterrupt is not
                # caught which is intended. If things go really wrong, the user
                # should stay in control
                self._write(traceback.format_exc())
        # We're done
        self.cleanups = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.cleanup_now()
        return False
