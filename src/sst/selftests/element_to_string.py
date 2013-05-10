import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')
sst.actions.assert_title('The Page Title')

element_with_id = sst.actions.get_element(id='some_id')
element_string = sst.actions._element_to_string(element_with_id)
sst.actions.assert_equal('some_id', element_string)

element_without_id_with_text = sst.actions.get_element(css_class='no_id')
element_string = sst.actions._element_to_string(element_without_id_with_text)
sst.actions.assert_equal('Element without id, with text.', element_string)

element_without_id_without_text = sst.actions.get_element(
    css_class='no_id_no_text')
element_string = sst.actions._element_to_string(
    element_without_id_without_text)
sst.actions.assert_equal('<p class="no_id_no_text"></p>', element_string)
