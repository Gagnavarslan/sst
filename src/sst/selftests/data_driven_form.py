import sst
import sst.actions

# vars from data_driven_form.csv are available in namespace
assert('textfield1' in dir())
assert('password1' in dir())
assert('list_field' in dir())
assert('should_pass' in dir())
# flake8 complains that it can't find the magical symbols, so we explicitly
# create them. The following lines are useless otherwise, the symbols *are*
# available but it's easier to work around flake8 here.
textfield1 = globals()['textfield1']
list_field = globals()['list_field']
password1 = globals()['password1']
should_pass = globals()['should_pass']

assert(len(list_field) > 1)
assert((list_field[0] == 1) or (list_field[0] == 'a'))
assert isinstance(should_pass, bool)

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
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
