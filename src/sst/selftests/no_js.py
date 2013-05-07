import sst
import sst.actions
from sst import config

# disabling javascript is currently only implemented for Firefox in sst
if config.browser_type != 'firefox':
    sst.actions.skip()

JAVASCRIPT_DISABLED = True

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/nojs/')

sst.actions.assert_text('test', "Before JS")

from sst import config
assert config.javascript_disabled
