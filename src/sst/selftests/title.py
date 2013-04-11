from sst.actions import *
from sst import DEVSERVER_PORT

# tests go_to, assert_url, assert_title, set_base_url
# reset_base_url, get_base_url

go_to('/')

assert_url('/')
fails(assert_url, '/foo')

assert_title('The Page Title')
fails(assert_title, 'this is not the title')

assert_title_contains('The Page')
assert_title_contains('.*Pag[E|e]', regex=True)
fails(assert_title_contains, 'foobar')

set_base_url('localhost:%s' % DEVSERVER_PORT)
assert get_base_url() == 'http://localhost:%s' % DEVSERVER_PORT

set_base_url('http://localhost:%s/' % DEVSERVER_PORT)
assert get_base_url() == 'http://localhost:%s/' % DEVSERVER_PORT
go_to('/')

# assert_url adds the base url for relative urls
# so test both ways
assert_url('http://localhost:%s/' % DEVSERVER_PORT)
assert_url('/')

fails(assert_url, '/begin/')

reset_base_url()
assert get_base_url() == 'http://localhost:%s/' % DEVSERVER_PORT
go_to('/')
assert_url('http://localhost:%s/' % DEVSERVER_PORT)

# assert_url works also without the trailing slash
assert_url('http://localhost:%s' % DEVSERVER_PORT)
