import os
from sst import config

assert locals() == config._current_context
assert config.browser_type
assert config.__args__ == {}
assert __name__ == 'context'
assert __file__.endswith('context.py')

this_dir = os.path.dirname(__file__)
this_shared = os.path.abspath(os.path.join(this_dir, 'shared'))
assert (config.shared_directory == this_shared)
