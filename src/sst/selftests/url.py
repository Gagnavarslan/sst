import sst
import sst.actions

# tests go_to, assert_url, assert_title, set_base_url
# reset_base_url, get_base_url


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_url('/')
sst.actions.fails(sst.actions.assert_url, '/foo')

sst.actions.set_base_url('localhost:%s' % sst.DEVSERVER_PORT)
assert sst.actions.get_base_url() == 'http://localhost:%s' % sst.DEVSERVER_PORT

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
assert (sst.actions.get_base_url()
        == 'http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

# assert_url adds the base url for relative urls
# so test both ways
sst.actions.assert_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.assert_url('/')

sst.actions.fails(sst.actions.assert_url, '/begin/')

# assert_url works also without the trailing slash
sst.actions.assert_url('http://localhost:%s' % sst.DEVSERVER_PORT)

sst.actions.reset_base_url()
assert sst.actions.get_base_url() is None
sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')
sst.actions.assert_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
