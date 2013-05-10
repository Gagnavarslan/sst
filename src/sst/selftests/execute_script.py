import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')


orig_title = 'The Page Title'
new_title = 'New Title'


# get original title.
sst.actions.assert_title(orig_title)
orig_elem = sst.actions.get_element(tag='title')

# change the title with javascript.
script = 'document.title = "%s"' % new_title
sst.actions.execute_script(script)

# check title was changed.
sst.actions.assert_title(new_title)
sst.actions.assert_not_equal(orig_elem, sst.actions.get_element(tag='title'))

# refresh title is changed back after refresh.
sst.actions.refresh()
sst.actions.assert_title(orig_title)

# check the return value of the script.
assert sst.actions.execute_script('return 5') == 5
