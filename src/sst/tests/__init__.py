#
#   Copyright (c) 2013 Canonical Ltd.
#
#   This file is part of: SST (selenium-simple-test)
#   https://launchpad.net/selenium-simple-test
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import inspect
import os
import shutil
import socket
import sys
import tempfile

import testtools

from sst import (
    cases,
    loaders,
)

discover = loaders.discoverRegularTests


class SSTBrowserLessTestCase(cases.SSTTestCase):
    """A specialized test class for tests that don't need a browser."""

    # We don't use a browser here so disable its use to speed the tests
    # (i.e. the browser won't be started)
    def start_browser(self):
        pass

    def stop_browser(self):
        pass


class ImportingLocalFilesTest(testtools.TestCase):
    """Class for tests requiring import of locally generated files.

    This setup the tests working dir in a newly created temp dir and restore
    sys.modules and sys.path at the end of the test.
    """
    def setUp(self):
        super(ImportingLocalFilesTest, self).setUp()
        set_cwd_to_tmp(self)
        protect_imports(self)
        sys.path.insert(0, self.test_base_dir)


def set_cwd_to_tmp(test):
    """Create a temp dir an cd into it for the test duration.

    This is generally called during a test setup.
    """
    test.test_base_dir = tempfile.mkdtemp(prefix='mytests-', suffix='.tmp')
    test.addCleanup(shutil.rmtree, test.test_base_dir, True)
    current_dir = os.getcwdu()
    test.addCleanup(os.chdir, current_dir)
    os.chdir(test.test_base_dir)


def protect_imports(test):
    """Protect sys.modules and sys.path for the test duration.

    This is useful to test imports which modifies sys.modules or requires
    modifying sys.path.
    """
    # Protect sys.modules and sys.path to be able to test imports
    test.patch(sys, 'path', list(sys.path))
    orig_modules = sys.modules.copy()

    def cleanup_modules():
        # Remove all added modules
        added = [m for m in sys.modules.keys() if m not in orig_modules]
        if added:
            for m in added:
                del sys.modules[m]
        # Restore deleted or modified modules
        sys.modules.update(orig_modules)
    test.addCleanup(cleanup_modules)


def check_devserver_port_used(port):
    """check if port is ok to use for django devserver"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # immediately reuse a local socket in TIME_WAIT state
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('127.0.0.1', port))
        used = False
    except socket.error:
        used = True
    finally:
        sock.close()
    return used


def write_tree_from_desc(description):
    """Write a tree described in a textual form to disk.

    The textual form describes the file contents separated by file/dir names.

    'file: <file name>' on a single line starts a file description. The file
    name must be the relative path from the tree root.

    'dir: <dir name>' on a single line starts a dir description.

    'link: <link source> <link name>' on a single line describes a symlink to
    <link source> named <link name>. The source may not exist, spaces are not
    allowed.

    :param description: A text where files and directories contents is
        described in a textual form separated by file/dir names.
    """
    cur_file = None
    for line in description.splitlines():
        if line.startswith('file: '):
            # A new file begins
            if cur_file:
                cur_file.close()
            cur_file = open(line[len('file: '):], 'w')
            continue
        if line.startswith('dir:'):
            # A new dir begins
            if cur_file:
                cur_file.close()
                cur_file = None
            os.mkdir(line[len('dir: '):])
            continue
        if line.startswith('link: '):
            # We don't support spaces in names
            link_desc = line[len('link: '):]
            try:
                source, link = link_desc.split()
            except ValueError:
                raise ValueError('Invalid link description: %s' % (link_desc,))
            os.symlink(source, link)
            continue
        if cur_file is not None:  # If no file is declared, nothing is written
            # splitlines() removed the \n, let's add it again
            cur_file.write(line + '\n')
    if cur_file:
        cur_file.close()


def get_case(kind):
    # Define the class in a function so test loading don't try to load it as a
    # regular test class.

    class Test(testtools.TestCase):

        # For error and failure to avoid spurious failures when the file is
        # edited.
        traceback_line = None

        def test_pass(self):
            pass

        def test_fail(self):
            self.traceback_line = inspect.currentframe().f_lineno + 1
            raise self.failureException

        def test_error(self):
            self.traceback_line = inspect.currentframe().f_lineno + 1
            raise SyntaxError

        def test_skip(self):
            self.skipTest('')

        def test_skip_reason(self):
            self.skipTest('Because')

        def test_expected_failure(self):
            # We expect the test to fail and it does
            self.expectFailure("1 should be 0", self.assertEqual, 1, 0)

        def test_unexpected_success(self):
            # We expect the test to fail but it doesn't
            self.expectFailure("1 is not 1", self.assertEqual, 1, 1)

    test_method = 'test_%s' % (kind,)
    return Test(test_method)


def expand_template_for_test(template, test, kwargs=None):
    """Expand common references in template.

    Tests that check runs output can be simplified if they use templates
    instead of litteral expected strings. There are plenty of examples below.

    :param template: A string where common strings have been replaced by a
        keyword so 1) tests are easier to read, 2) we don't run into pep8
        warnings for long lines.

    :param test: The test case under scrutiny.

    :param kwargs: A dict with more keywords for the template. This allows
        some tests to add more keywords when they are test specific.
    """
    if kwargs is None:
        kwargs = dict()
    # Getting the file name right is tricky, depending on whether the module
    # was just recompiled or not __file__ can be either .py or .pyc but when it
    # appears in an exception, the .py is always used.
    filename = __file__.replace('.pyc', '.py').replace('.pyo', '.py')
    traceback_fixed_length = kwargs.get('traceback_fixed_length', None)
    if traceback_fixed_length is not None:
        # We need to calculate the traceback detail length which includes the
        # file name.
        full_length = traceback_fixed_length + len(filename)
        kwargs['subunit_traceback_length'] = '%X' % (full_length,)
    traceback_line = getattr(test, 'traceback_line', None)
    kwargs['traceback_line'] = traceback_line
    # To allow easier reading for template, we format some known values
    kwargs.update(dict(classname='%s.%s' % (test.__class__.__module__,
                                            test.__class__.__name__),
                       name=test._testMethodName,
                       filename=filename))
    return template.format(**kwargs)
