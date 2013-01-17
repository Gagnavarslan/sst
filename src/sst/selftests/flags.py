from sst.actions import *
from sst import config

from unittest2 import SkipTest


try:
    # this should always skip
    check_flags('never-passed')
except SkipTest:
    pass
else:
    raise AssertionError('Test not skipped')

assert config.flags == [], (
    'Flags should be empty for test run: %r' % (config.flags,))

config.flags = ['foo']
try:
    # this should not skip, because 'foo' is a flag
    check_flags('foo')
    check_flags('FOO')
finally:
    config.flags = []
