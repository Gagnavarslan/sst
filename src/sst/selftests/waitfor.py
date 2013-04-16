from sst.actions import *
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

go_to('/')
set_wait_timeout(0.1)

wait_for(get_condition(True))
fails(wait_for, get_condition(False))

wait_for(get_condition(raises=True))
fails(wait_for, get_condition(False, raises=True))

wait_for(assert_url, '/')
fails(wait_for, assert_url, '/thing')

wait_for(assert_url, url='/')
fails(wait_for, assert_url, url='/thing')

CALLS = 0
set_wait_timeout(0.1, 0.01)
fails(wait_for, get_condition(wait=0.2))
assert CALLS > 6

fails(wait_for, get_condition(wait=0.2, raises=True))

set_wait_timeout(0.5)
wait_for(get_condition(wait=0.2))
wait_for(get_condition(wait=0.2, raises=True))

set_wait_timeout(0.3, 0.1)
CALLS = 0
wait_for(get_condition(wait=0.2))
assert CALLS <= 3

set_wait_timeout(5, 0.1)

wait_for_and_refresh(get_condition(True))
fails(wait_for_and_refresh, get_condition(False))
