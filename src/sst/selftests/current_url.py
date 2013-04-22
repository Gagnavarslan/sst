import sst.actions
from sst import DEVSERVER_PORT


sst.actions.go_to('/')
url = sst.actions.get_current_url()
base_url = sst.actions.get_base_url()
sst.actions.assert_equal(base_url, 'http://localhost:%s/' % DEVSERVER_PORT)
sst.actions.assert_equal(url, 'http://localhost:%s/' % DEVSERVER_PORT)

sst.actions.go_to('/begin')
url = sst.actions.get_current_url()
base_url = sst.actions.get_base_url()
sst.actions.assert_equal(base_url, 'http://localhost:%s/' % DEVSERVER_PORT)
sst.actions.assert_equal(url, 'http://localhost:%s/begin' % DEVSERVER_PORT)
