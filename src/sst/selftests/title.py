import sst.actions
from sst import DEVSERVER_PORT

# tests go_to, assert_url, assert_title, set_base_url
# reset_base_url, get_base_url

sst.actions.go_to('/')

sst.actions.assert_url('/')
sst.actions.fails(sst.actions.assert_url, '/foo')

sst.actions.assert_title('The Page Title')
sst.actions.fails(sst.actions.assert_title, 'this is not the title')

sst.actions.assert_title_contains('The Page')
sst.actions.assert_title_contains('.*Pag[E|e]', regex=True)
sst.actions.fails(sst.actions.assert_title_contains, 'foobar')

sst.actions.set_base_url('localhost:%s' % DEVSERVER_PORT)
assert sst.actions.get_base_url() == 'http://localhost:%s' % DEVSERVER_PORT

sst.actions.set_base_url('http://localhost:%s/' % DEVSERVER_PORT)
assert sst.actions.get_base_url() == 'http://localhost:%s/' % DEVSERVER_PORT
sst.actions.go_to('/')

# assert_url adds the base url for relative urls
# so test both ways
sst.actions.assert_url('http://localhost:%s/' % DEVSERVER_PORT)
sst.actions.assert_url('/')

sst.actions.fails(sst.actions.assert_url, '/begin/')

sst.actions.reset_base_url()
assert sst.actions.get_base_url() == 'http://localhost:%s/' % DEVSERVER_PORT
sst.actions.go_to('/')
sst.actions.assert_url('http://localhost:%s/' % DEVSERVER_PORT)

# assert_url works also without the trailing slash
sst.actions.assert_url('http://localhost:%s' % DEVSERVER_PORT)
