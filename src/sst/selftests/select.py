import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_dropdown('select_with_id_1')

sst.actions.assert_dropdown(sst.actions.get_element(id='select_with_id_1'))

sst.actions.fails(sst.actions.assert_dropdown, 'fake_id')

sst.actions.fails(sst.actions.assert_dropdown, 'headline')

sst.actions.set_dropdown_value('select_with_id_1', 'Select Two')
sst.actions.assert_dropdown_value('select_with_id_1', 'Select Two')

#  the following should fail saying that the option
#  is not set to the expected value
sst.actions.fails(
    sst.actions.assert_dropdown_value, 'select_with_id_1', 'Fake Text')

#  The following should fail saying that the option does not exist
sst.actions.fails(
    sst.actions.set_dropdown_value, 'select_with_id_1', 'Fake Text')
