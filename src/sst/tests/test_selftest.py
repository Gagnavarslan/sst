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


from cStringIO import StringIO

import testtools

from sst.tests import main


class TestTestProgram(testtools.TestCase):

    def run_test_program(self, module, argv, out):
        main.TestProgram(module, argv=['dummy'] + argv, stdout=out,
                         exit=False)

    def test_list(self):
        out = StringIO()
        # We need to specify __name__ as 'module' to get all the tests defined
        # in this file
        self.run_test_program(__name__, ['-l'], out)
        # At least this test should appear in the list (we don't check for an
        # exact list or this test will fail each time a new one is added).
        self.assertIn(self.id(), out.getvalue())

    def test_list_single(self):
        out = StringIO()
        # We need to specify None as 'module' or
        # unittest.loader.TestLoader.loadTestsFromName will not automatically
        # import the required modules
        self.run_test_program(None, ['-l', self.id()], out)
        self.assertEqual(self.id() + '\n', out.getvalue())
