import sst
import sst.actions

# tests for assert_text, text_contains

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

title = sst.actions.get_element(tag='title')
sst.actions.assert_text(title, 'The Page Title')
sst.actions.assert_text_contains(title, 'The Page')
sst.actions.fails(sst.actions.assert_text_contains, title, 'foobar')

body = sst.actions.get_element(tag='body')
sst.actions.assert_text_contains(body, '.*[C|c]ountry.*', regex=True)
