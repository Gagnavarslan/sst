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

import os
import shutil
import socket
import tempfile

from sst import runtests


class SSTBrowserLessTestCase(runtests.SSTTestCase):
    """A specialized test class for tests that don't need a browser."""

    # We don't use a browser here so disable its use to speed the tests
    # (i.e. the browser won't be started)
    def start_browser(self):
        pass

    def stop_browser(self):
        pass


def set_cwd_to_tmp(test):
    """Create a temp dir an cd into it for the test duration.

    This is generally called during a test setup.
    """
    test.test_base_dir = tempfile.mkdtemp(prefix='mytests-', suffix='.tmp')
    test.addCleanup(shutil.rmtree, test.test_base_dir, True)
    current_dir = os.getcwdu()
    test.addCleanup(os.chdir, current_dir)
    os.chdir(test.test_base_dir)


def check_devserver_port_used(port):
    """check if port is ok to use for django devserver"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # immediately reuse a local socket in TIME_WAIT state
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('127.0.0.1', int(port)))
        used = False
    except socket.error as e:
        used = True
    finally:
        sock.close()
    return used
