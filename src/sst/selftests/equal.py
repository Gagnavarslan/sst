import sst.actions


sst.actions.assert_equal(1, 1)
sst.actions.assert_equal('foo', 'foo')

sst.actions.fails(sst.actions.assert_equal, 1, 2)
sst.actions.fails(sst.actions.assert_equal, 'foo', 'bar')

sst.actions.assert_not_equal(1, 2)
sst.actions.assert_not_equal('foo', 'bar')

sst.actions.fails(sst.actions.assert_not_equal, 1, 1)
sst.actions.fails(sst.actions.assert_not_equal, 'foo', 'foo')
