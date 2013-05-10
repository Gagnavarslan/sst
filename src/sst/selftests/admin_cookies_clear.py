import sst
import sst.actions

import helpers


helpers.setup_cleanup_test_db()

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/admin/')
sst.actions.assert_title('Log in | Django site admin')

# login to Admin site
sst.actions.write_textfield('id_username', 'sst')
sst.actions.write_textfield('id_password', 'password')
sst.actions.click_element(sst.actions.get_element(value='Log in'))
sst.actions.assert_title('Site administration | Django site admin')
sst.actions.assert_element(
    tag='h1', id='site-name', text='Django administration')

# make sure you didn't get bounced back to login page
sst.actions.fails(sst.actions.assert_title, 'Log in | Django site admin')

# get cookies of current session (set of dicts)
cookies = sst.actions.get_cookies()
assert len(cookies) > 0
for cookie in cookies:
    assert (cookie['name'] in ('csrftoken', 'sessionid'))
    assert (len(cookie['value']) > 1)

# logout
sst.actions.click_link(sst.actions.get_element(text='Log out'))
sst.actions.assert_title('Logged out | Django site admin')

# get cookies of current session (set of dicts)
cookies = sst.actions.get_cookies()
assert len(cookies) > 0

# clear cookies
sst.actions.clear_cookies()
cookies = sst.actions.get_cookies()
sst.actions.assert_equal(len(cookies), 0)
