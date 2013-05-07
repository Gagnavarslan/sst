import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

# checks that clicking works at the element level as well
sst.actions.click_element(
    sst.actions.get_element(id='the_band_link'), wait=False)
sst.actions.assert_url('/begin')

sst.actions.go_to('/')

# checks the wait option
sst.actions.click_element(
    sst.actions.get_element(id='the_band_link'), wait=True)
sst.actions.assert_url('/begin')
