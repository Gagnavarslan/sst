import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_displayed('select_with_id_1')
sst.actions.fails(sst.actions.assert_displayed, 'hidden_input')
