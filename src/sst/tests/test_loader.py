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

from sst import (
    loader,
    tests,
)


class TestLoadScript(testtools.TestCase):

    def setUp(self):
        super(TestLoadScript, self).setUp()
        tests.set_cwd_to_tmp(self)

    def create_script(self, path, content):
        with open(path, 'w') as f:
            f.write(content)

    def test_load_simple_script(self):
        # A simple do nothing script with no imports
        self.create_script('foo.py', 'pass')
        suite = loader.TestLoader().loadTestsFromScript('.', 'foo.py')
        self.assertEqual(1, suite.countTestCases())

    def test_load_simple_script_with_csv(self):
        self.create_script('foo.py', "pass")
        with open('foo.csv', 'w') as f:
            f.write("'foo'^'bar'\n")
            f.write('1^baz\n')
            f.write('2^qux\n')
        suite = loader.TestLoader().loadTestsFromScript('.', 'foo.py')
        self.assertEqual(2, suite.countTestCases())
