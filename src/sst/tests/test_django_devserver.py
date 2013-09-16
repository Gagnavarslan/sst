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

from selenium.webdriver.common import utils

from sst import tests
from sst.scripts import test as script_test


class TestDjangoDevServer(testtools.TestCase):

    def setUp(self):
        super(TestDjangoDevServer, self).setUp()
        # We should not rely on the current directory being the root of the sst
        # project, the best way to achieve that is to change to a newly created
        # one.
        tests.set_cwd_to_tmp(self)

    def get_free_port(self):
        # We should really have a way to tell django to use a free port
        # provided by the OS but until then, we'll use the selenium trick. It's
        # racy but hopefully the OS doesn't reuse a port it just provided too
        # fast... -- vila 2013-07=05
        return utils.free_port()

    def test_django_start(self):
        port = self.get_free_port()
        self.addCleanup(script_test.kill_django, port)
        proc = script_test.run_django(port)
        self.assertIsNotNone(proc)

    def test_django_devserver_port_used(self):
        port = self.get_free_port()
        used = tests.check_devserver_port_used(port)
        self.assertFalse(used)
        self.addCleanup(script_test.kill_django, port)
        script_test.run_django(port)
        used = tests.check_devserver_port_used(port)
        self.assertTrue(used)
        e = self.assertRaises(RuntimeError,
                              script_test.run_django, port)
        self.assertEqual('Port %s is in use.\n'
                         'Can not launch Django server for internal tests.'
                         % (port,),
                         e.args[0])
