import sst.actions


# navigate to populate history
sst.actions.go_to('/')
sst.actions.click_element('the_band_link')
sst.actions.assert_url('/begin')
sst.actions.go_to('/')
sst.actions.assert_url('/')
sst.actions.click_element('the_band_link')
sst.actions.assert_url('/begin')

# go back in Browser history
sst.actions.go_back()
sst.actions.assert_url('/')
sst.actions.go_back()
sst.actions.assert_url('/begin')
sst.actions.go_back()
sst.actions.assert_url('/')
