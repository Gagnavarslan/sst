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


import testtools.run
import unittest


class TestProgram(testtools.run.TestProgram):

    def __init__(self, module, argv, stdout=None, testRunner=None, exit=True):
        if testRunner is None:
            testRunner = unittest.TextTestRunner
        super(TestProgram, self).__init__(module, argv=argv, stdout=stdout,
                                          testRunner=testRunner, exit=exit)
