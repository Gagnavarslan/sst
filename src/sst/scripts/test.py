#!/usr/bin/env python
#
#   Copyright (c) 2011,2012,2013 Canonical Ltd.
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
import subprocess
import sys
import time
import urllib

import testtools

testtools.try_import('selenium')
testtools.try_import('django')

import sst
from sst import (
    browsers,
    command,
    runtests,
    tests,
)


package_dir = os.path.dirname(os.path.dirname(__file__))


def main():
    cmd_opts, args = command.get_opts_run()
    out = sys.stdout
    cleaner = command.Cleaner(out)

    run_django(sst.DEVSERVER_PORT)
    cleaner.add('killing django...\n', kill_django, sst.DEVSERVER_PORT)

    if cmd_opts.xserver_headless:
        from sst.xvfbdisplay import Xvfb
        out.write('starting virtual display...\n')
        display = Xvfb(width=1024, height=768)
        display.start()
        cleaner.add('stopping virtual display...\n', display.stop)

    with cleaner:
        results_directory = os.path.abspath('results')
        command.reset_directory(results_directory)
        os.chdir(os.path.dirname(package_dir))
        test_dir = os.path.join('.', 'sst',)
        shared_directory = os.path.join('.', 'sst', 'selftests', 'shared')
        factory = browsers.browser_factories.get(cmd_opts.browser_type)
        failures = runtests.runtests(
            args, results_directory, out,
            test_dir=test_dir,
            collect_only=cmd_opts.collect_only,
            report_format=cmd_opts.report_format,
            browser_factory=factory(),
            shared_directory=shared_directory,
            screenshots_on=cmd_opts.screenshots_on,
            concurrency_num=cmd_opts.concurrency,
            failfast=cmd_opts.failfast,
            debug=cmd_opts.debug,
            extended=cmd_opts.extended_tracebacks,
            excludes=cmd_opts.excludes
        )

    return failures


def run_django(port):
    """Start django server for running local self-tests."""
    if tests.check_devserver_port_used(port):
        raise RuntimeError('Port %s is in use.\n'
                           'Can not launch Django server for internal tests.'
                           % (port,))
    manage_file = os.path.abspath(
        os.path.join(package_dir, '../testproject/manage.py'))
    url = 'http://localhost:%s/' % port

    if not os.path.isfile(manage_file):
        raise RuntimeError(
            'Can not find the django testproject.\n'
            '%r does not exist\n'
            'you must run tests from the dev branch or package source.'
            % (manage_file,))

    proc = subprocess.Popen([manage_file, 'runserver', str(port)],
                            stderr=open(os.devnull, 'w'),
                            stdout=open(os.devnull, 'w')
                            )
    attempts = 30
    for count in range(attempts):
        try:
            resp = urllib.urlopen(url)
            if resp.code == 200:
                break
        except IOError:
            time.sleep(0.2)
            if count >= attempts - 1:  # timeout
                raise RuntimeError('Django server for acceptance '
                                   'tests is not running.')
    return proc


def kill_django(port):
    try:
        urllib.urlopen('http://localhost:%s/kill_django' % port)
    except IOError:
        pass


if __name__ == '__main__':
    failures = main()
    if failures:
        sys.exit(1)
