import os

import sst.actions


def skip_as_jenkins():
    """Skip test when running as Jenkins user."""
    try:
        user = os.environ['USER']
    except KeyError:
        user = 'notjenkins'
    if user.lower() == 'jenkins':
        sst.actions.skip()
