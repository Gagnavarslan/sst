import sst.actions


sst.actions.set_wait_timeout(10)
assert sst.actions.get_wait_timeout() == 10

sst.actions.set_wait_timeout(20)
assert sst.actions.get_wait_timeout() == 20
