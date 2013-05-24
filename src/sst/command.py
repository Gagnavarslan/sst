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

import __main__
import logging
import os
import sys
import shutil
import optparse


import sst
from sst import (
    actions,
    browsers,
    config,
    runtests,
)


usage = """Usage: %prog [testname] [options]

- Calling %prog with testname(s) as arguments will just run
those tests. The testnames should not include '.py' at
the end of the filename.
"""


def clear_old_results():
    try:
        shutil.rmtree('./results/')
    except OSError:
        pass


def get_common_options():
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', dest='dir_name',
                      default='.',
                      help='directory of test case files')
    parser.add_option('-r', dest='report_format',
                      default='console',
                      help='valid report types: xml)')
    parser.add_option('-b', dest='browser_type',
                      default='Firefox',
                      help=('select webdriver (Firefox, Chrome, '
                            'PhantomJS, etc)'))
    parser.add_option('-j', dest='javascript_disabled',
                      default=False, action='store_true',
                      help='disable javascript in browser')
    parser.add_option('-m', dest='shared_modules',
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
                      'reports')
    parser.add_option('--collect-only', dest='collect_only',
                      action='store_true', default=False,
                      help='collect/print cases without running tests')
    parser.add_option(
        '-e', '--exclude', dest='excludes',
        action='append',
        help='all tests matching this regular expression will not be run')
    return parser


def get_run_options():
    parser = get_common_options()
    parser.add_option('--test',
                      dest='run_tests', action='store_true',
                      default=False,
                      help='run selftests (acceptance tests using django)')
    parser.add_option('-x', dest='xserver_headless',
                      default=False, action='store_true',
                      help='run browser in headless xserver (Xvfb)')
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
        print 'SST version: %s' % sst.__version__
        sys.exit()

    run_tests = getattr(cmd_opts, 'run_tests', False)
    if cmd_opts.dir_name == '.' and not args and not run_tests:
        print ('Error: you must supply a test case regular expression'
               ' or specifiy a directory.')
        prog = os.path.split(__main__.__file__)[-1]
        print 'run "%s -h" or "%s --help" to see run options.' % (prog, prog)
        sys.exit(1)

    if cmd_opts.browser_type not in browsers.browser_factories:
        print ("Error: %s should be one of %s"
               % (cmd_opts.browser_type, runtests.browser_factories.keys()))
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
