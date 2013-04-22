import sst.actions

import helpers


helpers.setup_cleanup_test_db()

sst.actions.go_to('/admin/')
sst.actions.assert_title('Log in | Django site admin')
