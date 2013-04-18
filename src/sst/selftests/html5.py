from sst.actions import *
from sst import DEVSERVER_PORT

go_to('/html5')

assert_textfield('email')
write_textfield('email', 'foo@bar.com', check=True)

assert_textfield('url')
write_textfield('url', 'http://localhost:%s' % DEVSERVER_PORT, check=True)

assert_textfield('search')
write_textfield('search', 'something', check=True)

assert_textfield('number')
write_textfield('number', '33', check=True)
