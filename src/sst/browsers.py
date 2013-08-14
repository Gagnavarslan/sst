#
#   Copyright (c) 2011-2013 Canonical Ltd.
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

import logging
import platform
import shutil
import subprocess
import time

from selenium import webdriver
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common import utils
from selenium.webdriver.firefox import (
    firefox_binary,
    webdriver as ff_webdriver,
)


logger = logging.getLogger('SST')


class BrowserFactory(object):
    """Handle browser creation for tests.

    One instance is used for a given test run.
    """

    webdriver_class = None

    def __init__(self):
        super(BrowserFactory, self).__init__()

    def setup_for_test(self, test):
        """Setup the browser for the given test.

        Some browsers accept more options that are test (and browser) specific.

        Daughter classes should redefine this method to capture them.
        """
        pass

    def browser(self):
        """Create a browser based on previously collected options.

        Daughter classes should override this method if they need to provide
        more context.
        """
        return self.webdriver_class()


# MISSINGTEST: Exercise this class -- vila 2013-04-11
class RemoteBrowserFactory(BrowserFactory):

    webdriver_class = webdriver.Remote

    def __init__(self, capabilities, remote_url):
        super(RemoteBrowserFactory, self).__init__()
        self.capabilities = capabilities
        self.remote_url = remote_url

    def browser(self):
        return self.webdriver_class(self.capabilities, self.remote_url)


# MISSINGTEST: Exercise this class -- vila 2013-04-11
class ChromeFactory(BrowserFactory):

    webdriver_class = webdriver.Chrome


# MISSINGTEST: Exercise this class (requires windows) -- vila 2013-04-11
class IeFactory(BrowserFactory):

    webdriver_class = webdriver.Ie


# MISSINGTEST: Exercise this class -- vila 2013-04-11
class PhantomJSFactory(BrowserFactory):

    webdriver_class = webdriver.PhantomJS


# MISSINGTEST: Exercise this class -- vila 2013-04-11
class OperaFactory(BrowserFactory):

    webdriver_class = webdriver.Opera


class FirefoxBinary(firefox_binary.FirefoxBinary):
    """Workarounds selenium firefox issues.

    There is race condition in the way firefox is spawned. The exact cause
    hasn't been properly diagnosed yet but it's around:

    - getting a free port from the OS with selenium.webdriver.common.utils
      free_port(),

    - release the port immediately but record it in ff prefs so that ff can
      listen on that port for the internal http server.

    It has been observed that this leads to hanging processes for 'firefox
    -silent'.
    """

    def _start_from_profile_path(self, path):
        self._firefox_env["XRE_PROFILE_PATH"] = path

        if platform.system().lower() == 'linux':
            self._modify_link_library_path()
        command = [self._start_cmd, "-silent"]
        if self.command_line is not None:
            for cli in self.command_line:
                command.append(cli)

# The following exists upstream and is known to create hanging firefoxes,
# leading to zombies.
#        out, _ = Popen(command, stdout=PIPE, stderr=STDOUT,
#                       env=self._firefox_env).communicate()
#        logger.debug('firefox -silent returned: %s' % (out,))
        command[1] = '-foreground'
        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=self._firefox_env)

    def _wait_until_connectable(self):
        """Blocks until the extension is connectable in the firefox.

        The base class implements this by checking utils.is_connectable() every
        second (sleep_for == 1) and failing after 30 attempts (max_tries ==
        30). Expriments showed that once a firefox can't be connected to, it's
        better to start a new one instead so we don't wait 30 seconds to fail
        in the end (the caller should catch WebDriverException and starts a new
        firefox).
        """
        connectable = False
        max_tries = 6
        sleep_for = 1
        for count in range(1, max_tries):
            connectable = utils.is_connectable(self.profile.port)
            if connectable:
                break
            logger.debug('Cannot connect to process %d with port: %d, count %d'
                         % (self.process.pid, self.profile.port, count))
            if self.process.poll() is not None:
                # Browser has exited
                raise selenium_exceptions.WebDriverException(
                    "The browser appears to have exited "
                    "before we could connect. The output was: %s" %
                    self._get_firefox_output())
            time.sleep(sleep_for)
        if not connectable:
            self.kill()
            raise selenium_exceptions.WebDriverException(
                'Cannot connect to the selenium extension, Firefox output: %s'
                % (self._get_firefox_output(),))
        return connectable


class WebDriverFirefox(ff_webdriver.WebDriver):
    """Workarounds selenium firefox issues."""

    def __init__(self, firefox_profile=None, firefox_binary=None, timeout=30,
                 capabilities=None, proxy=None):
        try:
            super(WebDriverFirefox, self).__init__(
                firefox_profile, FirefoxBinary(), timeout, capabilities, proxy)
        except selenium_exceptions.WebDriverException:
            # If we can't start, cleanup profile
            shutil.rmtree(self.profile.path)
            if self.profile.tempfolder is not None:
                shutil.rmtree(self.profile.tempfolder)
            raise


class FirefoxFactory(BrowserFactory):

    webdriver_class = WebDriverFirefox

    def setup_for_test(self, test):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('intl.accept_languages', 'en')
        if test.assume_trusted_cert_issuer:
            profile.set_preference('webdriver_assume_untrusted_issuer', False)
            profile.set_preference(
                'capability.policy.default.Window.QueryInterface', 'allAccess')
            profile.set_preference(
                'capability.policy.default.Window.frameElement.get',
                'allAccess')
        self.profile = profile

    def browser(self):
        return self.webdriver_class(self.profile)


# MISSINGTEST: Exercise this class -- vila 2013-04-11
browser_factories = {
    'Chrome': ChromeFactory,
    'Firefox': FirefoxFactory,
    'Ie': IeFactory,
    'Opera': OperaFactory,
    'PhantomJS': PhantomJSFactory,
}
