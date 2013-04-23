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

# The following two imports are required by unittest when running a list of
# test names like test_list_single does below (that's probably a bug in
# TestLoader.loadTestsFromName...) -- vila 2012-11-29
import sst  # NOQA, see above
import sst.tests  # NOQA, see above
from sst.tests import main


class TestTestProgram(testtools.TestCase):

    def run_test_program(self, argv, out):
        main.TestProgram(__name__, argv=['dummy'] + argv, stdout=out,
                         exit=False)

    def test_list(self):
        out = StringIO()
        self.run_test_program(['-l'], out)
        # At least this test should appear in the list (we don't check for an
        # exact list or this test will fail each time a new one is added).
        self.assertIn(self.id(), out.getvalue())

    def test_list_single(self):
        out = StringIO()
        self.run_test_program(['-l', self.id()], out)
        self.assertEqual(self.id() + '\n', out.getvalue())
