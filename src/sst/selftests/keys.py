import sst
import sst.actions

# tests for simulate_keys


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')
sst.actions.assert_title('The Page Title')

sst.actions.write_textfield('text_1', 'Foobar..')

sst.actions.simulate_keys('text_1', 'BACK_SPACE')
sst.actions.simulate_keys('text_1', 'back_space')  # not case sensitive
sst.actions.simulate_keys('text_1', 'SPACE')
sst.actions.simulate_keys('text_1', 'Space')

sst.actions.assert_text('text_1', 'Foobar  ')


# available keys (from selenium/webdriver/common/keys.py):
#
#  'NULL'
#  'CANCEL'
#  'HELP'
#  'BACK_SPACE'
#  'TAB'
#  'CLEAR'
#  'RETURN'
#  'ENTER'
#  'SHIFT'
#  'LEFT_SHIFT'
#  'CONTROL'
#  'LEFT_CONTROL'
#  'ALT'
#  'LEFT_ALT'
#  'PAUSE'
#  'ESCAPE'
#  'SPACE'
#  'PAGE_UP'
#  'PAGE_DOWN'
#  'END'
#  'HOME'
#  'LEFT'
#  'ARROW_LEFT'
#  'UP'
#  'ARROW_UP'
#  'RIGHT'
#  'ARROW_RIGHT'
#  'DOWN'
#  'ARROW_DOWN'
#  'INSERT'
#  'DELETE'
#  'SEMICOLON'
#  'EQUALS'

#  'NUMPAD0'
#  'NUMPAD1'
#  'NUMPAD2'
#  'NUMPAD3'
#  'NUMPAD4'
#  'NUMPAD5'
#  'NUMPAD6'
#  'NUMPAD7'
#  'NUMPAD8'
#  'NUMPAD9'
#  'MULTIPLY'
#  'ADD'
#  'SEPARATOR'
#  'SUBTRACT'
#  'DECIMAL'
#  'DIVIDE'

#  'F1'
#  'F2'
#  'F3'
#  'F4'
#  'F5'
#  'F6'
#  'F7'
#  'F8'
#  'F9'
#  'F10'
#  'F11'
#  'F12'

#  'META'
#  'COMMAND'
