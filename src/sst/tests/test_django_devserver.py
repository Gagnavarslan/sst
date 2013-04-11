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


import testtools

from sst.scripts import run
from sst.tests import check_devserver_port_used
from sst import DEVSERVER_PORT


class TestDjangoDevServer(testtools.TestCase):

    def test_django_start(self):
        self.addCleanup(run.kill_django, DEVSERVER_PORT)
        proc = run.run_django(DEVSERVER_PORT)
        self.assertIsNotNone(proc)


    def test_django_devserver_port_used(self):
        used = check_devserver_port_used(DEVSERVER_PORT)
        self.assertFalse(used)
        
        self.addCleanup(run.kill_django, DEVSERVER_PORT)
        run.run_django(DEVSERVER_PORT)
        
        used = check_devserver_port_used(DEVSERVER_PORT)
        self.assertTrue(used)
