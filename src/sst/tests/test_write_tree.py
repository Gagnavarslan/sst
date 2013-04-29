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
import testtools

from sst import tests


class TestWriteTree(testtools.TestCase):

    def setUp(self):
        super(TestWriteTree, self).setUp()
        tests.set_cwd_to_tmp(self)

    def test_empty_description(self):
        self.assertEqual([], os.listdir('.'))
        tests.write_tree_from_desc('')
        self.assertEqual([], os.listdir('.'))

    def test_empty_file(self):
        tests.write_tree_from_desc('''file: foo''')
        self.assertEqual('', file('foo').read())

    def test_simple_file(self):
        tests.write_tree_from_desc('''file: foo
tagada
''')
        self.assertEqual('tagada\n', file('foo').read())

    def test_file_in_a_dir(self):
        tests.write_tree_from_desc('''dir: dir
file: dir/foo
bar
''')
        self.assertEqual('bar\n', file('dir/foo').read())

