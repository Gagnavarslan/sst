from sst.actions import *


go_to('/')
assert_title('The Page Title')

# Test an element.
element = get_element(id='some_id')
assert_text(element, 'Some text here')

# Test an id.
assert_text('some_id', 'Some text here')

# Test wrong text.
fails(assert_text, 'some_id', 'Wrong text')

# Test no text with id.
try:
    assert_text('element_without_text', '')
except AssertionError as error:
    assert_equal(
        "Element 'element_without_text' has no text attribute", error.message)
else:
    raise AssertionError('assert_text did not fail.')

# Test no text with element.
try:
    assert_text(get_element(id='element_without_text'), '')
except AssertionError as error:
    expected_message = ("Element u\'<p id=\"element_without_text\"></p>\' "
                        "has no text attribute")
    assert_equal(
        expected_message, error.message)
else:
    raise AssertionError('assert_text did not fail.')
