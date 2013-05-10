import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/html5')

sst.actions.assert_textfield('email')
sst.actions.write_textfield('email', 'foo@bar.com', check=True)

sst.actions.assert_textfield('url')
sst.actions.write_textfield(
    'url', 'http://localhost:%s' % sst.DEVSERVER_PORT, check=True)

sst.actions.assert_textfield('search')
sst.actions.write_textfield('search', 'something', check=True)

sst.actions.assert_textfield('number')
sst.actions.write_textfield('number', '33', check=True)
