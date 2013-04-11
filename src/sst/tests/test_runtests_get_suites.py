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


import os

import testtools
import unittest2

from sst import tests
from sst import runtests


def _make_test_files(dir):

    os.mkdir(dir)

    # generate files with TestCase classes
    testclass_file_names = (
        'test_a_real_test.py',
        'test_a_real_test1.py',
        'test_a_real_test2.py',
        '_hidden_class.py',
        'class_hide_case',
        'class_hiding_case.py',
    )
    for fn in testclass_file_names:
        with open(os.path.join(dir, fn), 'w') as f:
            f.write('from sst import runtests\n')
            f.write('class Test_%s(runtests.SSTTestCase):\n' % fn[:-3])
            f.write('    def test_%s(self): pass\n' % fn[:-3])

    # generate empty files
    file_names = (
        '__init__.py',
        'script1.py',
        'script2.py',
        'not_a_test',
        'test_not_a_test.p',
        '_hidden2.py'
    )
    for fn in file_names:
        with open(os.path.join(dir, fn), 'w') as f:
            pass



class TestGetSuites(testtools.TestCase):

    def setUp(self):
        super(TestGetSuites, self).setUp()
        tests.set_cwd_to_tmp(self)
        self.cases_dir = os.path.join(self.test_base_dir, 'cases')


    def test_runtests_get_suites(self):
        _make_test_files(self.cases_dir)

        test_names = ('*', )
        test_dir = self.cases_dir
        shared_dir = '.'
        collect_only = False
        screenshots_on = False
        failfast = False,
        debug = False
        extended = False

        found = runtests.get_suites(
            test_names, test_dir, shared_dir, collect_only,
            runtests.FirefoxFactory(False, None),
            screenshots_on, failfast, debug, extended
        )
        suite = found[0]._tests

        # assert we loaded correct number of cases
        self.assertEquals(len(suite), 6)

        expected_scripted_tests = (
            'test_script1',
            'test_script2',
            'test_class_hiding_case',
        )
        expected_testcase_tests = (
            'test_test_a_real_test',
            'test_test_a_real_test1',
            'test_test_a_real_test2',
        )

        for test in suite:
            if issubclass(test.__class__, runtests.SSTTestCase):
                self.assertIsInstance(test, runtests.SSTTestCase)
                name = test.id().split('.')[-1]
                self.assertIn(name, expected_scripted_tests)
            elif issubclass(test.__class__, unittest2.suite.TestSuite):
                self.assertIsInstance(test, unittest2.suite.TestSuite)
                for test_class in test._tests:
                    for case in test_class._tests:
                        for t in case._tests:
                            name = t.id().split('.')[-1]
                            self.assertIn(name, expected_testcase_tests)
            else:
                raise Exception('Can not identify test')
