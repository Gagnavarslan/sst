import sst
import sst.actions

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/yui')

sst.actions.write_textfield('text_with_default_value', '25', check=True)
