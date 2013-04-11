from sst.actions import *
from sst import DEVSERVER_PORT

go_to('/')
url = get_current_url()
base_url = get_base_url()
assert_equal(base_url, 'http://localhost:%s/' % DEVSERVER_PORT)
assert_equal(url, 'http://localhost:%s/' % DEVSERVER_PORT)

go_to('/begin')
url = get_current_url()
base_url = get_base_url()
assert_equal(base_url, 'http://localhost:%s/' % DEVSERVER_PORT)
assert_equal(url, 'http://localhost:%s/begin' % DEVSERVER_PORT)
