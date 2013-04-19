import sst.actions
from time import time


CALLS = 0


def get_condition(result=True, wait=0, raises=False,
                  cond_args=None, cond_kwargs=None):
    initial = time()

    def condition(*args, **kwargs):
        global CALLS
        CALLS += 1
        if cond_args is not None:
            if cond_args != args:
                # can't raise an assertion error here!
                raise TypeError('wrong args passed')
        if cond_kwargs is not None:
            if cond_kwargs != kwargs:
                # can't raise an assertion error here!
                raise TypeError('wrong args passed')
        if time() > initial + wait:
            return result
        if raises:
            raise AssertionError('not yet')
        return False
    return condition

sst.actions.go_to('/')
sst.actions.set_wait_timeout(0.1)

sst.actions.wait_for(get_condition(True))
sst.actions.fails(sst.actions.wait_for, get_condition(False))

sst.actions.wait_for(get_condition(raises=True))
sst.actions.fails(sst.actions.wait_for, get_condition(False, raises=True))

sst.actions.wait_for(sst.actions.assert_url, '/')
sst.actions.fails(sst.actions.wait_for, sst.actions.assert_url, '/thing')

sst.actions.wait_for(sst.actions.assert_url, url='/')
sst.actions.fails(sst.actions.wait_for, sst.actions.assert_url, url='/thing')

CALLS = 0
sst.actions.set_wait_timeout(0.1, 0.01)
sst.actions.fails(sst.actions.wait_for, get_condition(wait=0.2))
assert CALLS > 6

sst.actions.fails(sst.actions.wait_for, get_condition(wait=0.2, raises=True))

sst.actions.set_wait_timeout(0.5)
sst.actions.wait_for(get_condition(wait=0.2))
sst.actions.wait_for(get_condition(wait=0.2, raises=True))

sst.actions.set_wait_timeout(0.3, 0.1)
CALLS = 0
sst.actions.wait_for(get_condition(wait=0.2))
assert CALLS <= 3

sst.actions.set_wait_timeout(5, 0.1)

sst.actions.wait_for_and_refresh(get_condition(True))
sst.actions.fails(sst.actions.wait_for_and_refresh, get_condition(False))
