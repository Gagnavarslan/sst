import sst.actions


sst.actions.set_wait_timeout(6, 0.3)
sst.actions.set_base_url('http://bar/')

args = {}

foo = 6
args['one'] = sst.actions.get_argument('one', 'foo')
args['two'] = sst.actions.get_argument('two', 2)

RESULT = args
