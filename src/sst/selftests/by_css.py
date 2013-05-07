import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.get_element_by_css('#headline')
sst.actions.get_element_by_css('.unique_class')

sst.actions.fails(sst.actions.get_element_by_css, '#doesnotexist')
sst.actions.fails(sst.actions.get_element_by_css, '.someclass')

assert len(sst.actions.get_elements_by_css('#doesnotexist')) == 0
assert len(sst.actions.get_elements_by_css('#headline')) == 1
assert len(sst.actions.get_elements_by_css('.some_class')) == 2
