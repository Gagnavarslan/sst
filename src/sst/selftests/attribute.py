import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.assert_attribute('longscroll_link', 'name', 'longscroll')
sst.actions.assert_attribute('longscroll_link', 'name', 'scroll', regex=True)

sst.actions.fails(
    sst.actions.assert_attribute, 'longscroll_link', 'name', 'shortscroll')
sst.actions.fails(
    sst.actions.assert_attribute, 'longscroll_link', 'name', 'shortscroll',
    regex=True)
sst.actions.fails(
    sst.actions.assert_attribute, 'longscroll_link', 'fish', 'shortscroll')
sst.actions.fails(
    sst.actions.assert_attribute, 'longscroll_link', 'fish', 'shortscroll',
    regex=True)
