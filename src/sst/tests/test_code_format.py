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
from os.path import dirname

import pep8

import testtools


class Pep8ConformanceTestCase(testtools.TestCase):

    def test_pep8_conformance(self):
        # scan recursively starting from the 'src' directory
        root_dirname = os.path.realpath(__file__ + '/../../..')
        print root_dirname
        self.pep8style = pep8.StyleGuide()
        result = self.pep8style.input_dir(root_dirname)
        self.assertEqual(self.pep8style.options.report.total_errors, 0)
