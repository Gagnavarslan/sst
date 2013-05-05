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

    def test_single_line_without_return(self):
        self.assertEqual([], os.listdir('.'))
        tests.write_tree_from_desc('file: foo')
        self.assertEqual(['foo'], os.listdir('.'))
        self.assertEqual('', file('foo').read())

    def test_leading_line_is_ignored(self):
        self.assertEqual([], os.listdir('.'))
        tests.write_tree_from_desc('tagada\nfile: foo')
        self.assertEqual(['foo'], os.listdir('.'))
        self.assertEqual('', file('foo').read())

    def test_orphan_line_is_ignored(self):
        self.assertEqual([], os.listdir('.'))
        tests.write_tree_from_desc('''
dir: foo
orphan line
file: foo/bar.py
baz
''')
        self.assertEqual(['foo'], os.listdir('.'))
        self.assertEqual(['bar.py'], os.listdir('foo'))
        self.assertEqual('baz\n', file('foo/bar.py').read())

    def test_empty_file_content(self):
        tests.write_tree_from_desc('''file: foo''')
        self.assertEqual('', file('foo').read())

    def test_simple_file_content(self):
        tests.write_tree_from_desc('''file: foo
tagada
''')
        self.assertEqual('tagada\n', file('foo').read())

    def test_file_content_in_a_dir(self):
        tests.write_tree_from_desc('''dir: dir
file: dir/foo
bar
''')
        self.assertEqual('bar\n', file('dir/foo').read())

    def test_simple_symlink_creation(self):
        tests.write_tree_from_desc('''file: foo
tagada
link: foo bar
''')
        self.assertEqual('tagada\n', file('foo').read())
        self.assertEqual('tagada\n', file('bar').read())

    def test_broken_symlink_creation(self):
        tests.write_tree_from_desc('''link: foo bar
''')
        self.assertEqual('foo', os.readlink('bar'))

    def test_invalid_symlink_description_raises(self):
        e = self.assertRaises(ValueError,
                              tests.write_tree_from_desc, '''link: foo
''')
        self.assertEqual(e.message, 'Invalid link description: foo')
