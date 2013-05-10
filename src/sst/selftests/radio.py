import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_radio('radio_with_id_1')
sst.actions.assert_radio(sst.actions.get_element(id='radio_with_id_1'))
sst.actions.fails(sst.actions.assert_radio, 'does not exist')
sst.actions.fails(sst.actions.assert_radio, 'headline')

sst.actions.assert_radio_value('radio_with_id_1', True)
sst.actions.assert_radio_value(
    sst.actions.get_element(id='radio_with_id_1'), True)
sst.actions.fails(sst.actions.assert_radio_value, 'radio_with_id_1', False)
sst.actions.fails(sst.actions.assert_radio_value, 'headline', True)

sst.actions.assert_radio_value('radio_with_id_2', False)
sst.actions.fails(sst.actions.assert_radio_value, 'radio_with_id_2', True)

sst.actions.set_radio_value('radio_with_id_1')
sst.actions.assert_radio_value('radio_with_id_1', True)
sst.actions.assert_radio_value('radio_with_id_2', False)

sst.actions.set_radio_value('radio_with_id_2')
sst.actions.assert_radio_value('radio_with_id_1', False)
sst.actions.assert_radio_value('radio_with_id_2', True)

sst.actions.set_radio_value(sst.actions.get_element(id='radio_with_id_1'))
sst.actions.assert_radio_value('radio_with_id_1', True)
sst.actions.assert_radio_value('radio_with_id_2', False)

sst.actions.fails(sst.actions.set_radio_value, 'does not exist')
sst.actions.fails(sst.actions.set_radio_value, 'headline')

sst.actions.assert_text('label1', 'First')
sst.actions.fails(sst.actions.assert_text, 'label1', 'the wrong text')
sst.actions.fails(sst.actions.assert_text, 'does not exist', 'does not matter')
sst.actions.fails(sst.actions.assert_text, 'radio_with_id_1', 'has no text')
