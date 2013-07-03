import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/index.html')

# get cookies of current session (set of dicts)
cookies = sst.actions.get_cookies()
assert len(cookies) == 2
cookie1 = cookies[0]
cookie2 = cookies[1]
sst.actions.assert_equal(cookie1['name'], 'foo')
sst.actions.assert_equal(cookie1['value'], 'bar')
sst.actions.assert_equal(cookie2['name'], 'baz')
sst.actions.assert_equal(cookie2['value'], 'qux')

# clear cookies
sst.actions.clear_cookies()
cookies = sst.actions.get_cookies()
sst.actions.assert_equal(len(cookies), 0)
