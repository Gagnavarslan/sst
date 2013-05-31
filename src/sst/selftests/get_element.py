import sst
import sst.actions


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

# unique id
elem = sst.actions.get_element(id='longscroll_link')
sst.actions.assert_text(elem, 'link to longscroll page')

# unique id + tag
elem = sst.actions.get_element(tag='a', id='longscroll_link')
sst.actions.assert_text(elem, 'link to longscroll page')

# unique id + non-unique css_class
elem = sst.actions.get_element(id='longscroll_link', css_class='link class a1')
sst.actions.assert_text(elem, 'link to longscroll page')

# tag + unique id + non-unique css_class
elem = sst.actions.get_element(
    tag='a', id='longscroll_link', css_class='link class a1')
sst.actions.assert_text(elem, 'link to longscroll page')

# unique id + tag
elem = sst.actions.get_element(tag='a', id='longscroll_link')
sst.actions.assert_text(elem, 'link to longscroll page')

# unique id + tag + href
elem = sst.actions.get_element(
    tag='a', id='longscroll_link', href='/longscroll')
sst.actions.assert_text(elem, 'link to longscroll page')

# unique id + href
elem = sst.actions.get_element(id='longscroll_link', href='/longscroll')
sst.actions.assert_text(elem, 'link to longscroll page')

# unique_id + tag + href + text
elem = sst.actions.get_element(
    tag='a', id='longscroll_link', href='/longscroll',
    text='link to longscroll page')
sst.actions.assert_text(elem, 'link to longscroll page')

# unique_id + href + text
elem = sst.actions.get_element(
    id='longscroll_link', href='/longscroll', text='link to longscroll page')
sst.actions.assert_text(elem, 'link to longscroll page')

# href + text
elem = sst.actions.get_element(
    href='/longscroll', text='link to longscroll page')
sst.actions.assert_text(elem, 'link to longscroll page')

# href
elem = sst.actions.get_element(href='/longscroll')
sst.actions.assert_text(elem, 'link to longscroll page')

# css_class
elem = sst.actions.get_element(css_class='unique_class')
sst.actions.assert_text(elem, 'Some text here')

# css_class + unique_id
elem = sst.actions.get_element(css_class='unique_class', id='some_id')
sst.actions.assert_text(elem, 'Some text here')

# css_class + unique_id + tag
elem = sst.actions.get_element(css_class='unique_class', id='some_id', tag='p')
sst.actions.assert_text(elem, 'Some text here')

# arbitrary attribute
sst.actions.get_element(value='unique')

# text
elem = sst.actions.get_element(text='Foo bar baz')
sst.actions.assert_text(elem, 'Foo bar baz')

# text + tag
elem = sst.actions.get_element(tag='h2', text='Foo bar baz')
sst.actions.assert_text(elem, 'Foo bar baz')

# text + tag
elem = sst.actions.get_element(tag='td', text='Get text from TD')
sst.actions.assert_text(elem, 'Get text from TD')

# radio buttons
elem = sst.actions.get_element(id='radio_with_id_1')
sst.actions.assert_radio(elem)
elem = sst.actions.get_element(tag='input', id='radio_with_id_1')
sst.actions.assert_radio(elem)
elem = sst.actions.get_element(type='radio', name='radio_with_id', checked='1')
sst.actions.assert_radio(elem)
