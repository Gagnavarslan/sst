from sst.actions import *

import helpers


helpers.setup_cleanup_test_db()

go_to('/admin/')
assert_title('Log in | Django site admin')
