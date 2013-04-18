from sst.actions import *

import helpers


helpers.setup_cleanup_test_db()

go_to('/admin/')
assert_title_contains('Django site admin')

assert_title('Log in | Django site admin')

# login to Admin site
write_textfield('id_username', 'sst')
write_textfield('id_password', 'password')
click_element(get_element(value='Log in'))
assert_title('Site administration | Django site admin')
assert_element(tag='h1', id='site-name', text='Django administration')

# make sure you didn't get bounced back to login page
fails(assert_title, 'Log in | Django site admin')

# get cookies of current session (set of dicts)
cookies = get_cookies()
assert len(cookies) > 0
for cookie in cookies:
    assert (cookie['name'] in ('csrftoken', 'sessionid'))
    assert (len(cookie['value']) > 1)

# logout
click_link(get_element(text='Log out'))
assert_title('Logged out | Django site admin')
