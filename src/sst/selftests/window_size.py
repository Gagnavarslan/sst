import sst
import sst.actions

# check original window size
width, height = sst.actions.get_window_size()
assert isinstance(width, int)
assert isinstance(height, int)
assert width > 0
assert height > 0

# resize window
width = 450
height = 420
sst.actions.set_window_size(width, height)
w, h = sst.actions.get_window_size()
sst.actions.assert_equal(w, width)
sst.actions.assert_equal(h, height)

# set window to same size
sst.actions.set_window_size(width, height)
w, h = sst.actions.get_window_size()
sst.actions.assert_equal(w, width)
sst.actions.assert_equal(h, height)

# load content so we can clock a popup
sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

# switch to new window/tab and resize it
sst.actions.click_link('popup_link')
sst.actions.switch_to_window(index_or_name='_NEW_WINDOW')
sst.actions.assert_title('Popup Window')

width = 260
height = 275
sst.actions.set_window_size(width, height)
w, h = sst.actions.get_window_size()
sst.actions.assert_equal(width, w)
sst.actions.assert_equal(height, h)
