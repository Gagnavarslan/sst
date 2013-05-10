import sst
import sst.actions


# test get_page_source

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

txt = sst.actions.get_page_source()

assert (txt != '')
assert '<html' in txt
assert '</head>' in txt
assert '<body>' in txt


# test get_element_source

elems = sst.actions.get_elements(tag='p')
for elem in elems:
    txt = sst.actions.get_element_source(elem)
    assert (len(txt) >= 0)
