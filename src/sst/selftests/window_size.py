import sst.actions


width, height = sst.actions.get_window_size()
assert isinstance(width, int)
assert isinstance(height, int)
assert width > 0
assert height > 0

expected_width, expected_height = sst.actions.set_window_size(200, 300)
width, height = sst.actions.get_window_size()
assert isinstance(expected_width, int)
assert isinstance(expected_height, int)
assert width == expected_width == 200
assert height == expected_height == 300

expected_width, expected_height = sst.actions.set_window_size(450, 420)
width, height = sst.actions.get_window_size()
assert width == expected_width == 450
assert height == expected_height == 420

expected_width, expected_height = sst.actions.set_window_size(380, 320)
# set window to same size
sst.actions.set_window_size(380, 320)
width, height = sst.actions.get_window_size()
assert width == expected_width == 380
assert height == expected_height == 320

sst.actions.go_to('/')

# switch to new window/tab and resize it
sst.actions.click_link('popup_link')
sst.actions.switch_to_window(index_or_name='_NEW_WINDOW')
sst.actions.assert_title('Popup Window')
expected_width, expected_height = sst.actions.set_window_size(260, 275)
width, height = sst.actions.get_window_size()
assert width == expected_width == 260
assert height == expected_height == 275
