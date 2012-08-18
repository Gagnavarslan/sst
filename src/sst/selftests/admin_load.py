from sst.actions import *

import helpers


# skip this test when running from CI
helpers.skip_as_jenkins()

go_to('/admin/')
assert_title_contains('Django site admin')

# logout of Admin if needed
elem = get_element(tag='title')
if 'Log in' not in elem.text:
    click_link(get_element(text='Log out'))
    assert_title('Logged out | Django site admin')
    refresh()

assert_title('Log in | Django site admin')
