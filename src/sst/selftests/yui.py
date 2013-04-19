import sst.actions

sst.actions.go_to('/yui')

sst.actions.write_textfield('text_with_default_value', '25', check=True)
