from sst.actions import *
from sst import config

# PhantomJS can not do multiple windows by design
if config.browser_type == 'phantomjs':
    skip()

go_to('/')
click_link('popup_link')

# switch to new window/tab
switch_to_window(index_or_name='_NEW_WINDOW')
assert_title('Popup Window')

# switch back to default/main window/tab
switch_to_window()
assert_title('The Page Title')

# switch to new window/tab
switch_to_window('_NEW_WINDOW')
assert_title('Popup Window')

# verify we can access content in new window
elem = get_element(tag='p', id='popup_id', text='Popup text here')
assert_text(elem, 'Popup text here')

# switch back to default/main window/tab
switch_to_window(index_or_name='')
assert_title('The Page Title')

# switch to new window/tab using index
switch_to_window(index_or_name=1)
assert_title('Popup Window')

# switch back to default/main window using index
switch_to_window(0)
assert_title('The Page Title')

# fails when the window name does not exist
fails(switch_to_window, index_or_name='not_a_window')

# fails when the window name does not exist
fails(switch_to_window, 'not_a_window')

# fails when the window index does not exist
fails(switch_to_window, index_or_name=99)

# fails when the window index does not exist
fails(switch_to_window, 99)

# verify we are still back on main window
assert_title('The Page Title')
