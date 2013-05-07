import os
import sst
import sst.actions
from sst import config

# Test actions related to file input elements.


# file input is currently only implemented for Firefox in sst
if config.browser_type != 'firefox':
    sst.actions.skip()


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

# Assert that the input file is a textfield.
sst.actions.assert_textfield('file_input')
sst.actions.assert_textfield(sst.actions.get_element(id='file_input'))

# Enter a path to an existing file on the file input.
file_path = os.path.abspath(__file__)
sst.actions.write_textfield('file_input', file_path)
sst.actions.assert_text('file_input', file_path)
