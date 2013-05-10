import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_element(id='select_with_id_1')
sst.actions.assert_element(css_class='unique_class', id='some_id')
sst.actions.assert_element(name='longscroll', href='/longscroll')

sst.actions.fails(sst.actions.assert_element, id='nonexistent')
sst.actions.fails(
    sst.actions.assert_element, css_class='unique_class', name='fish')
