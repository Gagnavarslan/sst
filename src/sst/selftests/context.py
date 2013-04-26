import os
from sst import config

assert locals() == config._current_context
assert config.browser_type
assert config.__args__ == {}
assert not config.javascript_disabled
assert __name__ == 'context'
assert __file__.endswith('context.py')

thisdir = os.path.dirname(__file__)
assert (config.shared_directory
        == os.path.abspath(os.path.join(thisdir, 'shared')))
