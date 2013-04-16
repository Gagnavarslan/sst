from sst.actions import *
from sst import config

if config.browser_type == 'phantomjs':
    skip()
if config.browser_type == 'chrome':
    skip()

JAVASCRIPT_DISABLED = True

go_to('/nojs/')

assert_text('test', "Before JS")

from sst import config
assert config.javascript_disabled
