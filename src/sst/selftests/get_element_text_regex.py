import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')


num_links = len(sst.actions.get_elements(tag='a'))

assert num_links == len(sst.actions.get_elements(tag='a', text_regex='.*'))


sst.actions.get_element(tag='p', text_regex='^Some text here')
sst.actions.exists_element(tag='p', text_regex='^Some text here')

sst.actions.get_element(tag='p', text_regex='^Some text.*$')
sst.actions.exists_element(tag='p', text_regex='^Some text.*$')

assert len(sst.actions.get_elements(tag='p', text_regex='^Some text.*$')) == 1
