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

import sst
import sst.actions


def is_png(data):
    return (data[:8] == '\211PNG\r\n\032\n'and (data[12:16] == 'IHDR'))


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/page_to_save')
screenshot_path = sst.actions.take_screenshot()
assert os.path.isfile(screenshot_path)
with open(screenshot_path, 'rb') as screenshot_file:
    data = screenshot_file.read()
    assert is_png(data)
# TODO compare the screenshot with the expected one.
# This is easy to do if we are using the same browser. It's harder to compare
# screenshots taken on different browsers.
