from sst.actions import *
from sst import config

# disabling javascript is currently only implemented for Firefox in sst
if config.browser_type != 'firefox':
    skip()

JAVASCRIPT_DISABLED = True

go_to('/nojs/')

assert_text('test', "Before JS")

from sst import config
assert config.javascript_disabled
