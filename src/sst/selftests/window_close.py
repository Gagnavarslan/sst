from sst.actions import *
from sst import config

# PhantomJS can not do multiple windows by design
if config.browser_type == 'phantomjs':
    skip()

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
