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

import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')
sst.actions.assert_title('The Page Title')

# Test get text from identifier.
identifier = 'some_id'
sst.actions.assert_equal('Some text here', sst.actions.get_text(identifier))

# Test get text from element.
element = sst.actions.get_element(id='some_id')
sst.actions.assert_equal('Some text here', sst.actions.get_text(element))

# Test get text from element without text.
sst.actions.assert_equal('', sst.actions.get_text('element_without_text'))
