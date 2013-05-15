import os
import shutil

import sst.actions


def skip_as_jenkins():
    """Skip test when running as Jenkins user."""
    try:
        user = os.environ['USER']
    except KeyError:
        user = 'notjenkins'
    if user.lower() == 'jenkins':
        sst.actions.skip()


def setup_cleanup_test_db():
    """Restore testproj.db before a test and cleanup db after test."""
    # this will copy testproj.db from testproj.db.orginal as setup
    # and remove database after test as a cleanup.
    # (this is used for all tests that access local django admin app only)
    here = os.path.abspath(os.path.dirname(__file__))
    test_db = os.path.abspath(
        os.path.join(here, '..', '..', '..', 'testproject/testproj.db'))
    if os.path.isfile(test_db):
        os.remove(test_db)
    shutil.copyfile(test_db + '.original', test_db)
    sst.actions.add_cleanup(os.remove, test_db)
