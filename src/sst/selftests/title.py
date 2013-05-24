import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_title('The Page Title')
sst.actions.fails(sst.actions.assert_title, 'this is not the title')

sst.actions.assert_title_contains('The Page')
sst.actions.assert_title_contains('.*Pag[E|e]', regex=True)
sst.actions.fails(sst.actions.assert_title_contains, 'foobar')

# title has no text attribute since it's in head
title = sst.actions.get_element(tag='title')
sst.actions.fails(sst.actions.assert_text_contains, title, 'The Page Title')
