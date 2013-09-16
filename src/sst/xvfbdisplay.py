#
#   Copyright (c) 2012-2013 Canonical Ltd.
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
#
#   ----
#
#   wrapper for running inside Xvfb.
#   inspired by PyVirtualDisplay: http://pypi.python.org/pypi/PyVirtualDisplay
#

import os
import fnmatch
import random
import subprocess
import time


class Xvfb(object):

    def __init__(self, width=1024, height=768, colordepth=24):
        self.width = width
        self.height = height
        self.colordepth = colordepth

        self.proc = None
        if 'DISPLAY' in os.environ:
            self.old_display_num = os.environ['DISPLAY'].split(':')[1]
        else:
            self.old_display_num = 0

    def start(self):
        self.vdisplay_num = self.search_for_free_display()
        self.xvfb_cmd = [
            'Xvfb', ':%d' % (self.vdisplay_num,), '-screen', '0',
            '%dx%dx%d' % (self.width, self.height, self.colordepth)]
        self.proc = subprocess.Popen(self.xvfb_cmd,
                                     stdout=open(os.devnull),
                                     stderr=open(os.devnull),)
        time.sleep(0.1)  # give Xvfb time to start
        self._redirect_display(self.vdisplay_num)

    def stop(self):
        self._redirect_display(self.old_display_num)
        if self.proc is not None:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None

    def search_for_free_display(self):
        ls = map(lambda x: int(x.split('X')[1].split('-')[0]),
                 self._lock_files())
        min_display_num = 1000
        if len(ls):
            display_num = max(min_display_num, max(ls) + 1)
        else:
            display_num = min_display_num
        random.seed()
        display_num += random.randint(0, 100)
        return display_num

    def _lock_files(self):
        tmpdir = '/tmp'
        pattern = '.X*-lock'
        names = fnmatch.filter(os.listdir(tmpdir), pattern)
        ls = [os.path.join(tmpdir, child) for child in names]
        ls = [p for p in ls if os.path.isfile(p)]
        return ls

    def _redirect_display(self, display_num):
        os.environ['DISPLAY'] = ':%s' % display_num


def use_xvfb_server(test, xvfb=None):
    """Setup an xvfb server for a given test.

    :param xvfb: An Xvfb object to use. If none is supplied, default values are
        used to build it.

    :returns: The xvfb server used so tests can use the built one.
    """
    if xvfb is None:
        xvfb = Xvfb()
    xvfb.start()
    test.addCleanup(xvfb.stop)
    return xvfb


if __name__ == '__main__':
    # example:

    vdisplay = Xvfb(width=1280, height=720)
    vdisplay.start()

    # do stuff in virtual display here

    vdisplay.stop()
