import sst
import sst.actions

""" negative (fails) tests for object identification """


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')
sst.actions.assert_title('The Page Title')


# need at least one parameter
sst.actions.fails(sst.actions.get_element)

# should fail if no elements match
sst.actions.fails(sst.actions.get_element, tag='foobar')
sst.actions.fails(sst.actions.get_element, id='foobar')
sst.actions.fails(sst.actions.get_element, tag='foobar', id='foobar')

# should fail if more than one element found
sst.actions.fails(sst.actions.get_element, tag='p')

# find by css class
sst.actions.fails(sst.actions.get_element, css_class='some_class')
sst.actions.fails(sst.actions.get_element, css_class="foobar")

# checking arbitrary attributes
sst.actions.fails(sst.actions.get_element, value='first')

# should fail for a partial match
sst.actions.fails(sst.actions.get_element, text='Foo bar')
