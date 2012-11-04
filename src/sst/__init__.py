#!/usr/bin/env python
#
#   Copyright (c) 2011 Canonical Ltd.
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


__all__ = ['runtests']
__version__ = '0.2.2'


try:
    from .runtests import runtests
except ImportError as e:
    # Selenium not installed
    # this means we can import the __version__
    # for setup.py when we install, without
    # *having* to install selenium first
    def runtests(*args, **kwargs):
        raise e

