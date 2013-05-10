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
sst.actions.switch_to_window('_NEW_WINDOW')
sst.actions.assert_title('Popup Window')

# fails when frame index is out of range
sst.actions.fails(sst.actions.switch_to_frame, index_or_name=2)

# switch to a valid frame index
sst.actions.switch_to_frame(index_or_name=1)
elem = sst.actions.get_element(id='frame_b_id')
sst.actions.assert_text(elem, 'Frame B text here')

# fails because we are in sibling frame
sst.actions.fails(sst.actions.get_element, id='frame_a_id')

# switch back to default frame
sst.actions.switch_to_frame()
sst.actions.get_element(tag='p', id='popup_id', text='Popup text here')
sst.actions.assert_title('Popup Window')

# switch to a valid frame name
sst.actions.switch_to_frame(index_or_name='frame_a')
elem = sst.actions.get_element(id='frame_a_id')
sst.actions.assert_text(elem, 'Frame A text here')

# switch back to default frame
sst.actions.switch_to_frame()
sst.actions.get_element(tag='p', id='popup_id', text='Popup text here')
sst.actions.assert_title('Popup Window')

# switch back to default/main window/tab
sst.actions.switch_to_window()
sst.actions.assert_title('The Page Title')
