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


import os
import sys
from cStringIO import StringIO


import testtools


from sst import (
    cases,
    xvfbdisplay,
)


class TestXvfb(testtools.TestCase):

    def test_start(self):
        xvfb = xvfbdisplay.Xvfb()
        self.addCleanup(xvfb.stop)
        xvfb.start()
        self.assertEqual(':%d' % xvfb.vdisplay_num, os.environ['DISPLAY'])
        self.assertIsNot(None, xvfb.proc)

    def test_stop(self):
        orig = os.environ['DISPLAY']
        xvfb = xvfbdisplay.Xvfb()
        xvfb.start()
        self.assertNotEqual(orig, os.environ['DISPLAY'])
        xvfb.stop()
        self.assertEquals(orig, os.environ['DISPLAY'])


class Headless(cases.SSTTestCase):
    """A specialized test class for tests around xvfb."""

    # We don't use a browser here so disable its use to speed the tests
    # (i.e. the browser won't be started)
    def start_browser(self):
        pass

    def stop_browser(self):
        pass


class TestSSTTestCaseWithXfvb(testtools.TestCase):

    def setUp(self):
        super(TestSSTTestCaseWithXfvb, self).setUp()
        # capture test output so we don't pollute the test runs
        self.out = StringIO()
        self.patch(sys, 'stdout', self.out)

    def assertRunSuccessfully(self, test):
        result = testtools.TestResult()
        test.run(result)
        self.assertEqual([], result.errors)
        self.assertEqual([], result.failures)

    def test_headless_new_xvfb(self):
        class HeadlessNewXvfb(Headless):

            xserver_headless = True

            def test_headless(self):
                # A headless server has been started for us
                self.assertNotEqual(None, self.xvfb.proc)

        self.assertRunSuccessfully(HeadlessNewXvfb("test_headless"))

    def test_headless_reused_xvfb(self):
        external_xvfb = xvfbdisplay.Xvfb()
        external_xvfb.start()
        self.addCleanup(external_xvfb.stop)

        class HeadlessReusedXvfb(Headless):

            xserver_headless = True
            xvfb = external_xvfb

            def test_headless(self):
                # We reuse the existing xvfb
                self.assertIs(external_xvfb, self.xvfb)

        self.assertRunSuccessfully(HeadlessReusedXvfb("test_headless"))
