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

import pep8
import testtools

import sst
import sst.selftests


class Pep8ConformanceTestCase(testtools.TestCase):

    packages = [sst, sst.scripts, sst.tests, sst.selftests]

    def test_pep8_conformance(self):
        pep8style = pep8.StyleGuide(show_source=True)
        for package in self.packages:
            dir = os.path.dirname(package.__file__)
            pep8style.input_dir(dir)
        self.assertEqual(pep8style.options.report.total_errors, 0)
