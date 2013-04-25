from sst import actions
import sst.actions


foo = 3
sst.actions.set_wait_timeout(1, 0.2)
sst.actions.set_base_url('http://foo/')

args = sst.actions.run_test('_test')
assert args == {
    'one': 'foo',
    'two': 2
}

# check the context hasn't been altered
assert foo == 3
assert actions._TIMEOUT == 1
assert actions._POLL == 0.2
assert actions.BASE_URL == 'http://foo/'

args = sst.actions.run_test('_test', one='ONE', two=3.1)
assert args == {
    'one': 'ONE',
    'two': 3.1
}
