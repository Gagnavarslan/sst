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


from selenium import webdriver


class BrowserFactory(object):
    """Handle browser creation for tests.

    One instance is used for a given test run.
    """

    webdriver_class = None

    def __init__(self, javascript_disabled=False):
        super(BrowserFactory, self).__init__()
        self.javascript_disabled = javascript_disabled

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


class FirefoxFactory(BrowserFactory):

    webdriver_class = webdriver.Firefox

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
        if test.javascript_disabled or self.javascript_disabled:
            profile.set_preference('javascript.enabled', False)
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
