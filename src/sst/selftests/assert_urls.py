from sst.actions import *
from sst import DEVSERVER_PORT

from urlparse import urlparse


# haven't visited a url yet, so all assert_url* fail
fails(assert_url, 'http://localhost:%s/' % DEVSERVER_PORT)
fails(assert_url_contains, 'localhost')
fails(assert_url_network_location, 'localhost')

# now visit a url and test assertions
go_to('%sbegin' % get_base_url())

assert_url('/begin')
assert_url('/begin/')
assert_url('begin/')
assert_url('http://localhost:%s/begin' % DEVSERVER_PORT)
assert_url('http://localhost:%s/begin/' % DEVSERVER_PORT)
assert_url(urlparse('http://wrongurl/begin').path)
fails(assert_url, 'http://wrongurl/begin')

assert_url_contains('http://localhost:%s/begin' % DEVSERVER_PORT)
assert_url_contains('localhost:%s' % DEVSERVER_PORT)
assert_url_contains('.*/begin', regex=True)
assert_url_contains('http://.*/begin', regex=True)
assert_url_contains('.*//localhost', regex=True)
assert_url_contains('lo[C|c]a.*host', regex=True)
fails(assert_url_contains, 'foobar')
fails(assert_url_contains, 'foobar', regex=True)

assert_url_network_location('localhost:%s' % DEVSERVER_PORT)
fails(assert_url_network_location, 'localhost')
fails(assert_url_network_location, '')

# visit url with query strings and fragments, then test assertions
go_to('/begin?query_string#fragment_id')

assert_url('http://localhost:%s/begin?query_string#fragment_id' % DEVSERVER_PORT)
assert_url('/begin?query_string#fragment_id')
fails(assert_url, '/begin')
fails(assert_url, 'http://localhost:%s/begin' % DEVSERVER_PORT)
