import sst
import sst.actions

from urlparse import urlparse


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
# haven't visited a url yet, so all assert_url* fail
sst.actions.fails(
    sst.actions.assert_url, 'http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.fails(
    sst.actions.assert_url_contains, 'localhost')
sst.actions.fails(
    sst.actions.assert_url_network_location, 'localhost')

# now visit a url and test assertions
sst.actions.go_to('%sbegin' % sst.actions.get_base_url())

sst.actions.assert_url('/begin')
sst.actions.assert_url('/begin/')
sst.actions.assert_url('begin/')
sst.actions.assert_url('http://localhost:%s/begin' % sst.DEVSERVER_PORT)
sst.actions.assert_url('http://localhost:%s/begin/' % sst.DEVSERVER_PORT)
sst.actions.assert_url(urlparse('http://wrongurl/begin').path)
sst.actions.fails(sst.actions.assert_url, 'http://wrongurl/begin')

sst.actions.assert_url_contains('http://localhost:%s/begin'
                                % sst.DEVSERVER_PORT)
sst.actions.assert_url_contains('localhost:%s' % sst.DEVSERVER_PORT)
sst.actions.assert_url_contains('.*/begin', regex=True)
sst.actions.assert_url_contains('http://.*/begin', regex=True)
sst.actions.assert_url_contains('.*//localhost', regex=True)
sst.actions.assert_url_contains('lo[C|c]a.*host', regex=True)
sst.actions.fails(sst.actions.assert_url_contains, 'foobar')
sst.actions.fails(sst.actions.assert_url_contains, 'foobar', regex=True)

sst.actions.assert_url_network_location('localhost:%s' % sst.DEVSERVER_PORT)
sst.actions.fails(sst.actions.assert_url_network_location, 'localhost')
sst.actions.fails(sst.actions.assert_url_network_location, '')

# visit url with query strings and fragments, then test assertions
sst.actions.go_to('/begin?query_string#fragment_id')

sst.actions.assert_url(
    'http://localhost:%s/begin?query_string#fragment_id' % sst.DEVSERVER_PORT)
sst.actions.assert_url('/begin?query_string#fragment_id')
sst.actions.fails(sst.actions.assert_url, '/begin')
sst.actions.fails(
    sst.actions.assert_url, 'http://localhost:%s/begin' % sst.DEVSERVER_PORT)
