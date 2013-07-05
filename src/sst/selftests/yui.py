import sst
import sst.actions

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/yui')

# FIXME: This has been observed to fail with a value of '125'. The theory is
# that this happened because write_textfield first clear the field (using
# send_keys() which shouldn't trigger the 'on change' event) and then set the
# new value. The associated yui.html defines that on an empty value (''), the
# default value (1) should be restored. So, '1' + '25' == '125'. For an unknown
# reason the 'on change' event has been triggered... If you can reproduce this
# issue, please get in touch ! -- vila 2013-07-05
sst.actions.write_textfield('text_with_default_value', '25', check=True)
