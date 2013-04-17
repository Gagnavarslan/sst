import os
import shutil

from sst.actions import *


# get copy of testproj.db for test
# remove database before/after test 
test_db = 'src/testproject/testproj.db'
if os.path.isfile(test_db):
    os.remove(test_db)
shutil.copyfile(test_db + '.original', test_db)
add_cleanup(os.remove, test_db)

go_to('/admin/')
assert_title('Log in | Django site admin')

# login to Admin site
write_textfield('id_username', 'sst')
write_textfield('id_password', 'password')
click_element(get_element(value='Log in'))
assert_title('Site administration | Django site admin')
assert_element(tag='h1', id='site-name', text='Django administration')

# make sure you didn't get bounced back to login page
fails(assert_title, 'Log in | Django site admin')

# logout
click_link(get_element(text='Log out'))
assert_title('Logged out | Django site admin')
