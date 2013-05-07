import sst
import sst.actions
from sst import config

# currently failing in Chrome.
# need to investigate and file upstream chromedriver bug.
if config.browser_type == 'chrome':
    sst.actions.skip()

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

u = u'abcdéשאלק'
sst.actions.write_textfield('text_1', u)
sst.actions.assert_text('text_1', u)
sst.actions.assert_text_contains('text_1', u)

u = u'\u05e9\u05d0\u05dc\u05e7'
sst.actions.write_textfield('text_1', u)
sst.actions.assert_text('text_1', u)
sst.actions.assert_text_contains('text_1', u)

u = unichr(40960) + u'abcd' + unichr(1972)
sst.actions.write_textfield('text_1', u)
sst.actions.assert_text('text_1', u)
sst.actions.assert_text_contains('text_1', u)
