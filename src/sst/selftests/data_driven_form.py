import sst.actions


# vars from data_driven_form.csv are available in namespace
assert('textfield1' in dir())
assert('password1' in dir())
assert('list_field' in dir())
assert(len(list_field) > 1)
assert((list_field[0] == 1) or (list_field[0] == 'a'))
assert isinstance(should_pass, bool)

sst.actions.go_to('/')
sst.actions.assert_title('The Page Title')

# fields come from the associated csv data file
sst.actions.write_textfield(
    sst.actions.get_element(name='textfield1'), textfield1)
sst.actions.write_textfield(
    sst.actions.get_element(name='password1'), password1)

sst.actions.click_button(
    sst.actions.get_element(tag='input', value='Begin'))
sst.actions.assert_title('The Next Page')
