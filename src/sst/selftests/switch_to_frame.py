from sst.actions import *
from sst import config

# PhantomJS can not do multiple windows by design
if config.browser_type == 'phantomjs':
    skip()

go_to('/')
click_link('popup_link')

# switch to new window/tab
switch_to_window('_NEW_WINDOW')
assert_title('Popup Window')

# fails when frame index is out of range
fails(switch_to_frame, index_or_name=2)

# switch to a valid frame index
switch_to_frame(index_or_name=1)
elem = get_element(id='frame_b_id')
assert_text(elem, 'Frame B text here')

# fails because we are in sibling frame
fails(get_element, id='frame_a_id')

# switch back to default frame
switch_to_frame()
get_element(tag='p', id='popup_id', text='Popup text here')
assert_title('Popup Window')

# switch to a valid frame name
switch_to_frame(index_or_name='frame_a')
elem = get_element(id='frame_a_id')
assert_text(elem, 'Frame A text here')

# switch back to default frame
switch_to_frame()
get_element(tag='p', id='popup_id', text='Popup text here')
assert_title('Popup Window')

# switch back to default/main window/tab
switch_to_window()
assert_title('The Page Title')
