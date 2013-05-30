#!/usr/bin/env python
#
#   Copyright (c) 2011-2012 Canonical Ltd.
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

from sst import (
    browsers,
    command,
    runtests,
)


def main():
    cmd_opts, args = command.get_opts_run()

    print '--------------------------------------------------------------'
    print 'starting SST...'

    cleaner = command.Cleaner(sys.stdout)

    if cmd_opts.xserver_headless:
        from sst.xvfbdisplay import Xvfb
        print '\nstarting virtual display...'
        display = Xvfb(width=1024, height=768)
        display.start()
        cleaner.add('stopping virtual display...\n', display.stop)

    with cleaner:
        command.clear_old_results()
        factory = browsers.browser_factories.get(cmd_opts.browser_type)
        failures = runtests.runtests(
            args,
            test_dir=cmd_opts.dir_name,
            collect_only=cmd_opts.collect_only,
            report_format=cmd_opts.report_format,
            browser_factory=factory(cmd_opts.javascript_disabled),
            shared_directory=cmd_opts.shared_directory,
            screenshots_on=cmd_opts.screenshots_on,
            failfast=cmd_opts.failfast,
            debug=cmd_opts.debug,
            extended=cmd_opts.extended_tracebacks,
            excludes=cmd_opts.excludes
        )

    return failures


if __name__ == '__main__':
    failures = main()
    if failures:
        sys.exit(1)
