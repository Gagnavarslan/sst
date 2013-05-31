import sst
import sst.actions

# tests for assert_text, text_contains

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

elem = sst.actions.get_element(tag='body')
sst.actions.assert_text_contains(elem, 'Some text here')
sst.actions.fails(sst.actions.assert_text_contains,
                  elem,
                  'dont find this text here'
                  )

body = sst.actions.get_element(tag='body')
sst.actions.assert_text_contains(body, '.*[C|c]ountry.*', regex=True)
