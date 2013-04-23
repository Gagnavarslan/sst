import sst.actions


width, height = sst.actions.get_window_size()
assert isinstance(width, int)
assert isinstance(height, int)
assert width > 0
assert height > 0

width, height = sst.actions.set_window_size(200, 300)
assert isinstance(width, int)
assert isinstance(height, int)
sst.actions.assert_equal(width, 200)
sst.actions.assert_equal(height, 300)

width, height = sst.actions.get_window_size()
assert isinstance(width, int)
assert isinstance(height, int)
sst.actions.assert_equal(width, 200)
sst.actions.assert_equal(height, 300)

width, height = sst.actions.set_window_size(450, 420)
sst.actions.assert_equal(width, 450)
sst.actions.assert_equal(height, 420)

width, height = sst.actions.get_window_size()
sst.actions.assert_equal(width, 450)
sst.actions.assert_equal(height, 420)

width, height = sst.actions.set_window_size(380, 320)
# set window to same size
sst.actions.set_window_size(380, 320)

width, height = sst.actions.get_window_size()
sst.actions.assert_equal(width, 380)
sst.actions.assert_equal(height, 320)

sst.actions.go_to('/')

# switch to new window/tab and resize it
sst.actions.click_link('popup_link')
sst.actions.switch_to_window(index_or_name='_NEW_WINDOW')
sst.actions.assert_title('Popup Window')

width, height = sst.actions.set_window_size(260, 275)
sst.actions.assert_equal(width, 260)
sst.actions.assert_equal(height, 275)

width, height = sst.actions.get_window_size()
sst.actions.assert_equal(width, 260)
sst.actions.assert_equal(height, 275)
