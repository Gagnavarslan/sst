import sst
import sst.actions
from sst import config

# PhantomJS can not do multiple windows by design
if config.browser_type == 'phantomjs':
    sst.actions.skip()

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')
sst.actions.click_link('popup_link')

# switch to new window/tab
sst.actions.switch_to_window(index_or_name='_NEW_WINDOW')
sst.actions.assert_title('Popup Window')

# switch back to default/main window/tab
sst.actions.switch_to_window()
sst.actions.assert_title('The Page Title')

# switch to new window/tab
sst.actions.switch_to_window('_NEW_WINDOW')
sst.actions.assert_title('Popup Window')

# verify we can access content in new window
elem = sst.actions.get_element(tag='p', id='popup_id', text='Popup text here')
sst.actions.assert_text(elem, 'Popup text here')

# switch back to default/main window/tab
sst.actions.switch_to_window(index_or_name='')
sst.actions.assert_title('The Page Title')

# switch to new window/tab using index
sst.actions.switch_to_window(index_or_name=1)
sst.actions.assert_title('Popup Window')

# switch back to default/main window using index
sst.actions.switch_to_window(0)
sst.actions.assert_title('The Page Title')

# fails when the window name does not exist
sst.actions.fails(sst.actions.switch_to_window, index_or_name='not_a_window')

# fails when the window name does not exist
sst.actions.fails(sst.actions.switch_to_window, 'not_a_window')

# fails when the window index does not exist
sst.actions.fails(sst.actions.switch_to_window, index_or_name=99)

# fails when the window index does not exist
sst.actions.fails(sst.actions.switch_to_window, 99)

# verify we are still back on main window
sst.actions.assert_title('The Page Title')
