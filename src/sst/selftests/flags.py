import sst.actions
from sst import config

from unittest import SkipTest


try:
    # this should always skip
    sst.actions.check_flags('never-passed')
except SkipTest:
    pass
else:
    raise AssertionError('Test not skipped')

assert config.flags == [], (
    'Flags should be empty for test run: %r' % (config.flags,))

config.flags = ['foo']
try:
    # this should not skip, because 'foo' is a flag
    sst.actions.check_flags('foo')
    sst.actions.check_flags('FOO')
finally:
    config.flags = []
