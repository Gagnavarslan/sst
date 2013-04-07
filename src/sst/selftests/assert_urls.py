from sst.actions import *
from urlparse import urlparse


assert_equal(get_base_url(), 'http://localhost:8000/')

# haven't visited a url yet, so all assert_url* fail
fails(assert_url, 'http://localhost:8000/')
fails(assert_url_contains, 'localhost')
fails(assert_url_domain, 'localhost')

# now visit a url and test assertions
go_to('/begin')

assert_url('/begin')
assert_url('/begin/')
assert_url('begin/')
assert_url('http://localhost:8000/begin')
assert_url('http://localhost:8000/begin/')
assert_url(urlparse('http://wrongurl/begin').path)
fails(assert_url, 'http://wrongurl/begin')

assert_url_contains('http://localhost:8000/begin')
assert_url_contains('localhost:8000')
assert_url_contains('http://.*/begin', regex=True)
assert_url_contains('.*//localhost', regex=True)
assert_url_contains('lo[C|c]a.*host', regex=True)
fails(assert_url_contains, 'foobar')
fails(assert_url_contains, 'foobar', regex=True)

assert_url_domain('localhost')
fails(assert_url_domain, 'localhost:8000')
fails(assert_url_domain, '')

# visit url with query strings and fragments, then test assertions
go_to('/begin?query_string#fragment_id')

assert_url('http://localhost:8000/begin?query_string#fragment_id')
assert_url('/begin?query_string#fragment_id')
fails(assert_url, '/begin')
fails(assert_url, 'http://localhost:8000/begin')
