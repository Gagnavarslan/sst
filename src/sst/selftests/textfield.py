import sst
import sst.actions


# password functionality is so close to textfield that
# we will include it with common textfield use


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_textfield('text_1')
sst.actions.assert_textfield(sst.actions.get_element(id='text_1'))

sst.actions.assert_textfield('pass_1')
sst.actions.assert_textfield(sst.actions.get_element(id='pass_1'))

# fails for non existent element
sst.actions.fails(sst.actions.assert_textfield, 'foobar')
# fails for element that exists but isn't a textfield
sst.actions.fails(sst.actions.assert_textfield, 'radio_with_id_1')

sst.actions.write_textfield('text_1', 'I pity the Foobar..')
sst.actions.assert_text('text_1', "I pity the Foobar..")

sst.actions.write_textfield('text_1', 'Overwriting')
sst.actions.assert_text('text_1', "Overwriting")

sst.actions.write_textfield('text_1', 'No checking', check=False)
sst.actions.assert_text('text_1', 'No checking')

# check with empty text
sst.actions.write_textfield('text_1', '')
sst.actions.assert_text('text_1', '')

# checks the password field to see if it is editable
sst.actions.write_textfield('pass_1', 'qaT3st')
sst.actions.assert_text('pass_1', 'qaT3st')
sst.actions.fails(sst.actions.assert_text, 'pass_1', 'fake_text')
