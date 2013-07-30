#
#   Copyright (c) 2011-2013 Canonical Ltd.
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


__version__ = '0.2.5dev'

DEVSERVER_PORT = 8120  # django devserver for internal acceptance tests


def discover(test_loader, package, dir_path, names):
    # Tests are only in directories below, the rest should not be looked at
    return test_loader.discoverTestsFromNames(dir_path, ['tests', 'selftests'])
