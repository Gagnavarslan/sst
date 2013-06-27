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


import sst
from sst import tests
from sst.scripts import test as script_test


class TestDjangoDevServer(testtools.TestCase):

    def setUp(self):
        super(TestDjangoDevServer, self).setUp()

    def test_django_start(self):
        self.addCleanup(script_test.kill_django, sst.DEVSERVER_PORT)
        proc = script_test.run_django(sst.DEVSERVER_PORT)
        self.assertIsNotNone(proc)

    def test_django_devserver_port_used(self):
        used = tests.check_devserver_port_used(sst.DEVSERVER_PORT)
        self.assertFalse(used)
        self.addCleanup(script_test.kill_django, sst.DEVSERVER_PORT)
        script_test.run_django(sst.DEVSERVER_PORT)
        used = tests.check_devserver_port_used(sst.DEVSERVER_PORT)
        self.assertTrue(used)
        e = self.assertRaises(RuntimeError,
                              script_test.run_django, sst.DEVSERVER_PORT)
        self.assertEqual('Error: port %s is in use.\n'
                         'Can not launch devserver for internal tests.'
                         % (sst.DEVSERVER_PORT,),
                         e.args[0])
