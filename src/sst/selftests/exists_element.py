import sst.actions


sst.actions.go_to('/')

assert sst.actions.exists_element(id='select_with_id_1')
assert not sst.actions.exists_element(id='non_existing_element')
