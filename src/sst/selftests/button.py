import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_button('mainform')
sst.actions.assert_button('lonely')
sst.actions.fails(sst.actions.assert_button, 'headline')
sst.actions.fails(sst.actions.assert_button, 'foobar')

sst.actions.assert_button(sst.actions.get_element(value='Begin', tag='input'))

# this button has no behaviour, but the action should not fail
sst.actions.click_button('lonely', wait=False)

# this button has no behaviour, but the action should not fail
sst.actions.click_button('lonely2', wait=False)

sst.actions.click_button('mainform')
sst.actions.assert_url('/begin')
sst.actions.assert_title('The Next Page')

sst.actions.click_link('the_band_link')
sst.actions.assert_url('/')

sst.actions.click_link('longscroll_link')
sst.actions.assert_url('/longscroll')

# button is initially scrolled out of view
sst.actions.click_button('mainform')
sst.actions.assert_url('/begin')
