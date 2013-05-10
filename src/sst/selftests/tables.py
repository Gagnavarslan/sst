import sst
import sst.actions

sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/tables')

sst.actions.assert_table_headers(
    'empty', ['Head 0', 'Head 1', 'Head 2', 'Head 3'])
sst.actions.assert_table_has_rows('empty', 0)
sst.actions.assert_table_has_rows('one-row', 1)

sst.actions.fails(
    sst.actions.assert_table_headers, 'notthere',
    ['Head 0', 'Head 1', 'Head 2', 'Head 3'])
sst.actions.fails(
    sst.actions.assert_table_headers, 'empty', ['Head 0', 'Head 1', 'Head 2'])
sst.actions.fails(
    sst.actions.assert_table_headers, 'empty',
    ['Wrong', 'Head 1', 'Head 2', 'Head 3'])
sst.actions.fails(sst.actions.assert_table_has_rows, 'notthere', 0)
sst.actions.fails(sst.actions.assert_table_has_rows, 'empty', 1)

# XXXX Should this be able to work?
sst.actions.fails(sst.actions.assert_table_has_rows, 'no-body', 0)

sst.actions.fails(sst.actions.assert_table_has_rows, 'one-row', 0)
sst.actions.fails(sst.actions.assert_table_has_rows, 'one-row', 2)

sst.actions.assert_table_row_contains_text(
    'one-row', 0, ['Cell 0', 'Cell 1', 'Cell 2', 'Cell 3'])
sst.actions.assert_table_row_contains_text(
    'one-row', 0, ['Cell 0', 'Cell 1', 'Cell 2', 'Cell 3'], regex=True)
sst.actions.assert_table_row_contains_text(
    'one-row', 0, ['^Cell', '^Cell', '^Cell', '^Cell'], regex=True)

sst.actions.fails(
    sst.actions.assert_table_row_contains_text, 'one-row', 0,
    ['Wrong', 'Cell 1', 'Cell 2', 'Cell 3'])
sst.actions.fails(
    sst.actions.assert_table_row_contains_text, 'one-row', 0,
    ['Cell 0', 'Cell 1', 'Cell 2'])
sst.actions.fails(
    sst.actions.assert_table_row_contains_text, 'one-row', 0,
    ['Cell 0', 'Cell 1', 'Cell 2', 'Extra'])
sst.actions.fails(sst.actions.assert_table_row_contains_text, 'one-row', 1, [])
sst.actions.fails(
    sst.actions.assert_table_row_contains_text, 'one-row', 0,
    ['Wrong', 'Cell 1', 'Cell 2', 'Cell 3'], regex=True)
sst.actions.fails(
    sst.actions.assert_table_row_contains_text, 'one-row', 0,
    ['Cell 0', 'Cell 1', 'Cell 2'], regex=True)
