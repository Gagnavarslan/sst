from sst.actions import *


go_to('http://finance.search.yahoo.com/')
assert_title_contains('Yahoo Finance Search')
element = get_element(id='yschsp')
write_textfield(element, 'AMZN', clear=False)
click_button('yschbt')
assert_title_contains('AMZN - Yahoo')
