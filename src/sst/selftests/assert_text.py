import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')
sst.actions.assert_title('The Page Title')

# Test an element.
element = sst.actions.get_element(id='some_id')
sst.actions.assert_text(element, 'Some text here')

# Test an id.
sst.actions.assert_text('some_id', 'Some text here')

# Test wrong text.
sst.actions.fails(sst.actions.assert_text, 'some_id', 'Wrong text')

# Test no text.
try:
    sst.actions.assert_text('element_without_text', '')
except AssertionError as error:
    sst.actions.assert_equal(
        "Element u'element_without_text' has no text.", error.message)
else:
    raise AssertionError('assert_text did not fail.')

# Test text field with no value.
sst.actions.assert_text('text_1', '')
