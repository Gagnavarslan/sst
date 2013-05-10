import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_link('the_band_link')
sst.actions.assert_link(sst.actions.get_element(id='the_band_link'))

# fails for non existent element.
sst.actions.fails(sst.actions.assert_link, 'foobar')

# fails for element that exists but isn't a link.
sst.actions.fails(sst.actions.assert_link, 'radio_with_id_1')


sst.actions.click_link('the_band_link', wait=False)
sst.actions.assert_url('/begin')

sst.actions.click_link('the_band_link')
sst.actions.assert_url('/')

sst.actions.click_link('longscroll_link')
sst.actions.assert_url('/longscroll')

sst.actions.click_link('homepage_link_top')
sst.actions.assert_url('/')

sst.actions.click_link('longscroll_link')
sst.actions.assert_url('/longscroll')

# link is initially scrolled out of view.
sst.actions.click_link('homepage_link_bottom')
sst.actions.assert_url('/')

# assert a link without an href.
sst.actions.assert_link('no_href_link')
