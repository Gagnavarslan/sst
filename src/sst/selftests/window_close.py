import sst
import sst.actions
from sst import config

# PhantomJS can not do multiple windows by design
if config.browser_type == 'phantomjs':
    sst.actions.skip()

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')
sst.actions.click_link('popup_link')

# switch to new window/tab and close it
sst.actions.switch_to_window(index_or_name='_NEW_WINDOW')
sst.actions.assert_title('Popup Window')
sst.actions.close_window()

# switch back to default/main window/tab
sst.actions.switch_to_window()
sst.actions.assert_title('The Page Title')

# fails because the window no longer exists
sst.actions.fails(sst.actions.switch_to_window, index_or_name='NEW_WINDOW')
