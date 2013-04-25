#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sst.tests import main

# We discover tests under src/sst/tests, the python 'load_test' protocol
# can be used in test modules for more fancy stuff.
discover_args = ['discover',
                 '--start-directory', './src/sst/tests',
                 '--top-level-directory', './src',
                 ]
main.TestProgram(__name__, argv=[sys.argv[0]] + discover_args + sys.argv[1:])
