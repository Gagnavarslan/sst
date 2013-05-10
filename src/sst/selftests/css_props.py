import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

elem = sst.actions.get_element(tag='body')
sst.actions.assert_css_property(
    elem, 'font-family', 'Ubuntu,Tahoma,sans-serif')

elem = sst.actions.get_element(tag='body')
sst.actions.assert_css_property(elem, 'font-family', 'Ubuntu', regex=True)

elems = sst.actions.get_elements(tag='h2')
for elem in elems:
    sst.actions.assert_css_property(elem, 'padding-left', '8px')

elems = sst.actions.get_elements(tag='h2')
for elem in elems:
    sst.actions.fails(
        sst.actions.assert_css_property, elem, 'padding-left', 'notfound')
