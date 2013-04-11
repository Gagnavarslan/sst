#!/usr/bin/env python
#
#   Copyright (c) 2011,2013 Canonical Ltd.
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


import testtools

testtools.try_import('selenium')

from sst import runtests
from sst.command import clear_old_results, get_opts_remote

def main():
    cmd_opts, args = get_opts_remote()

    clear_old_results()

    print '--------------------------------------------------------------'

    browser_factory = runtests.RemoteBrowserFactory(
        {
            "browserName": cmd_opts.browser_type.lower(),
            "platform": cmd_opts.browser_platform.upper(),
            "version": cmd_opts.browser_version,
            "javascriptEnabled": not cmd_opts.javascript_disabled,
            "name": cmd_opts.session_name},
        cmd_opts.webdriver_remote_url)
    runtests.runtests(
        args,
        test_dir=cmd_opts.dir_name,
        count_only=cmd_opts.count_only,
        report_format=cmd_opts.report_format,
        browser_factory=browser_factory,
        shared_directory=cmd_opts.shared_modules,
        screenshots_on=cmd_opts.screenshots_on,
        failfast=cmd_opts.failfast,
        debug=cmd_opts.debug,
        extended=cmd_opts.extended_tracebacks,
    )

    print '--------------------------------------------------------------'


if __name__ == '__main__':
    main()
