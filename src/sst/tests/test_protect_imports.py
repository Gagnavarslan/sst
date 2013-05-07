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

import sys
import testtools

from sst import tests


class TestProtectImports(testtools.TestCase):

    def setUp(self):
        super(TestProtectImports, self).setUp()
        tests.protect_imports(self)

    def run_successful_test(self, test):
        result = testtools.TestResult()
        test.run(result)
        self.assertTrue(result.wasSuccessful())

    def test_add_module(self):
        self.assertIs(None, sys.modules.get('foo', None))

        class Test(testtools.TestCase):

            def test_it(self):
                tests.protect_imports(self)
                sys.modules['foo'] = 'bar'

        self.run_successful_test(Test('test_it'))
        self.assertIs(None, sys.modules.get('foo', None))

    def test_remove_module(self):
        self.assertIs(None, sys.modules.get('I_dont_exist', None))
        sys.modules['I_dont_exist'] = 'bar'

        class Test(testtools.TestCase):

            def test_it(self):
                tests.protect_imports(self)
                self.assertEqual('bar', sys.modules['I_dont_exist'])
                del sys.modules['I_dont_exist']
        self.run_successful_test(Test('test_it'))
        self.assertEqual('bar', sys.modules['I_dont_exist'])

    def test_modify_module(self):
        self.assertIs(None, sys.modules.get('I_dont_exist', None))
        sys.modules['I_dont_exist'] = 'bar'

        class Test(testtools.TestCase):

            def test_it(self):
                tests.protect_imports(self)
                self.assertEqual('bar', sys.modules['I_dont_exist'])
                sys.modules['I_dont_exist'] = 'qux'
        self.run_successful_test(Test('test_it'))
        self.assertEqual('bar', sys.modules['I_dont_exist'])

    def test_sys_path_restored(self):
        tests.set_cwd_to_tmp(self)
        inserted = self.test_base_dir
        self.assertFalse(inserted in sys.path)

        class Test(testtools.TestCase):

            def test_it(self):
                tests.protect_imports(self)
                sys.path.insert(0, inserted)
        self.run_successful_test(Test('test_it'))
        self.assertFalse(inserted in sys.path)
