from sst.actions import *

go_to('/')
click_link('popup_link')

# switch to new window/tab and close it
switch_to_window(index_or_name='_NEW_WINDOW')
assert_title('Popup Window')
close_window()

# switch back to default/main window/tab
switch_to_window()
assert_title('The Page Title')

# fails because the window no longer exists
fails(switch_to_window, index_or_name='NEW_WINDOW')
