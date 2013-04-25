import sst.actions


sst.actions.go_to('/')

sst.actions.assert_title('The Page Title')
sst.actions.assert_url('/')

sst.actions.refresh()

sst.actions.assert_title('The Page Title')
sst.actions.assert_url('/')
