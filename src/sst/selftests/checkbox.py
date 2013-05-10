import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_checkbox('id_sreg_country')
sst.actions.assert_checkbox(sst.actions.get_element(id='id_sreg_country'))

# fails for non existent element
sst.actions.fails(sst.actions.assert_checkbox, 'foobar')
# fails for element that exists but isn't a checkbox
sst.actions.fails(sst.actions.assert_checkbox, 'radio_with_id_1')

sst.actions.assert_checkbox_value('id_sreg_country', False)
sst.actions.assert_checkbox_value(
    sst.actions.get_element(id='id_sreg_country'), False)

# fails when given the wrong value
sst.actions.fails(
    sst.actions.assert_checkbox_value, 'id_sreg_country', True)

sst.actions.toggle_checkbox('id_sreg_country')
sst.actions.assert_checkbox_value('id_sreg_country', True)

sst.actions.toggle_checkbox('id_sreg_country')
sst.actions.assert_checkbox_value('id_sreg_country', False)

# restore checkbox to True for next tests
sst.actions.toggle_checkbox('id_sreg_country')

sst.actions.set_checkbox_value('id_sreg_country', False)
sst.actions.assert_checkbox_value('id_sreg_country', False)

sst.actions.set_checkbox_value('id_sreg_country', True)
sst.actions.assert_checkbox_value('id_sreg_country', True)

# check doesn't fail when setting check box to
# the same value as it already is
sst.actions.set_checkbox_value('id_sreg_country', True)
sst.actions.assert_checkbox_value('id_sreg_country', True)
