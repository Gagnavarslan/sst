import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_title('The Page Title')
sst.actions.assert_url('/')

sst.actions.refresh()

sst.actions.assert_title('The Page Title')
sst.actions.assert_url('/')
