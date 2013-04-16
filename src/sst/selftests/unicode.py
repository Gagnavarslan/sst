from sst.actions import *
from sst import config

# currently failing in Chrome.  
# need to investigate and file upstream chromedriver bug.
if config.browser_type == 'chrome':
    skip()

go_to('/')

u = u'abcdéשאלק'
write_textfield('text_1', u)
assert_text('text_1', u)
assert_text_contains('text_1', u)

u = u'\u05e9\u05d0\u05dc\u05e7'
write_textfield('text_1', u)
assert_text('text_1', u)
assert_text_contains('text_1', u)

u = unichr(40960) + u'abcd' + unichr(1972)
write_textfield('text_1', u)
assert_text('text_1', u)
assert_text_contains('text_1', u)
