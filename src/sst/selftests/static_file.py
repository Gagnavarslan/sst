
# test for loading local files by file:// rather than http://

import os

import sst.actions


static_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'static.html'))

# using full path
sst.actions.go_to('file:////%s' % static_file)
sst.actions.assert_title('The Static Page')
sst.actions.assert_element(tag='h1', text='Hello World')

# using base_url
sst.actions.set_base_url('file:////')
sst.actions.go_to(static_file)
sst.actions.assert_title('The Static Page')
sst.actions.assert_element(tag='h1', text='Hello World')
