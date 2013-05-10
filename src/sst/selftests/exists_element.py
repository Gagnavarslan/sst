import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

assert sst.actions.exists_element(id='select_with_id_1')
assert not sst.actions.exists_element(id='non_existing_element')
