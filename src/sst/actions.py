#
#   Copyright (c) 2011,2012,2013 Canonical Ltd.
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

"""Actions to make Selenium tests simple.

Tests are comprised of Python scripts or test case classes.

Files whose names begin with an underscore will *not* be executed as tests.

Tests drive the browser with Selenium WebDriver by importing and using SST
actions.

The standard set of actions are imported by starting the test scripts with::

    from sst import actions


Actions that work on page elements take either an element id or an
element object as their first argument. If the element you are working with
doesn't have a specific id you can get the element object with the
`get_element` action. `get_element` allows you to find an element by its
id, tag, text, class or other attributes. See the `get_element` documentation.

"""

import codecs
import errno
import logging
import os
import re
import time

from datetime import datetime
from functools import wraps
from pdb import set_trace as debug
from urlparse import urljoin, urlparse

from selenium.webdriver.common import keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    NoSuchAttributeException,
    NoSuchElementException,
    NoSuchFrameException,
    NoSuchWindowException,
    StaleElementReferenceException,
    WebDriverException,
)

from sst import config

__all__ = [
    'accept_alert', 'add_cleanup', 'assert_attribute', 'assert_button',
    'assert_checkbox', 'assert_checkbox_value', 'assert_css_property',
    'assert_displayed', 'assert_dropdown', 'assert_dropdown_value',
    'assert_element', 'assert_equal', 'assert_link', 'assert_not_equal',
    'assert_radio', 'assert_radio_value', 'assert_table_has_rows',
    'assert_table_headers', 'assert_table_row_contains_text',
    'assert_text', 'assert_text_contains', 'assert_textfield',
    'assert_title', 'assert_title_contains', 'assert_url',
    'assert_url_contains', 'assert_url_network_location', 'check_flags',
    'clear_cookies', 'click_button', 'click_element', 'click_link',
    'close_window', 'debug', 'dismiss_alert', 'end_test', 'execute_script',
    'exists_element', 'fails', 'get_argument', 'get_base_url',
    'get_cookies', 'get_current_url', 'get_element',
    'get_element_by_css', 'get_element_by_xpath', 'get_element_source',
    'get_elements', 'get_elements_by_css', 'get_elements_by_xpath',
    'get_link_url', 'get_page_source', 'get_text', 'get_wait_timeout',
    'get_window_size', 'go_back', 'go_to', 'refresh', 'reset_base_url',
    'retry_on_exception', 'run_test', 'save_page_source', 'set_base_url',
    'set_checkbox_value', 'set_dropdown_value', 'set_radio_value',
    'set_wait_timeout', 'set_window_size', 'simulate_keys', 'skip', 'sleep',
    'switch_to_frame', 'switch_to_window',
    'take_screenshot', 'toggle_checkbox', 'wait_for',
    'wait_for_and_refresh', 'write_textfield'
]


_check_flags = True
_test = None

BASE_URL = None

logger = logging.getLogger('SST')


class EndTest(Exception):
    pass


debug.__doc__ = """Start the debugger, a shortcut for `pdb.set_trace()`."""


class _Sentinel(object):
    def __repr__(self):
        return 'default'
_sentinel = _Sentinel()


def _raise(msg):
    logger.debug(msg)
    raise AssertionError(msg)


def retry_on_exception(exception, retries=None):
    """Decorate a function so an `exception` triggers a retry.

    :param exception: If this exception is raised, the decorated function
        will be retried.
    :param retries: The number of times that the function will be retried.
        If it is `None`, the function will be retried until the time out set by
        `set_wait_timeout` expires.

    """
    def middle(func):

        @wraps(func)
        def inner(*args, **kwargs):
            tries = 0
            max_time = time.time() + _TIMEOUT

            def retry():
                return ((retries is None and time.time() < max_time) or
                        (retries is not None and tries <= retries))

            while(retry()):
                tries = tries + 1
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    logger.warning('Retrying after catching: %r' % e)
                time.sleep(_POLL)
            else:
                raise e

        return inner

    return middle


def set_base_url(url):
    """Set the URL used for relative arguments to the `go_to` action."""
    global BASE_URL
    if not url.startswith('http') and not url.startswith('file'):
        url = 'http://' + url
    logger.debug('Setting base url to: %r' % url)
    BASE_URL = url


def get_base_url():
    """Return the base URL used by `go_to`."""
    return BASE_URL


def reset_base_url():
    """Restore the base url to the default.

    This is called automatically for you when a test script completes.

    """
    global BASE_URL
    BASE_URL = None


def end_test():
    """End the test.

    It can be used conditionally to exit a test under certain conditions.

    """
    raise EndTest


def skip(reason=''):
    """Skip the test.

    Unlike `end_test` a skipped test will be reported as a skip rather than a
    pass.

    :argument reason: The reason to skip the test. It will be recorded in the
        test result.

    """
    _test.skipTest(reason)


def refresh(wait=True):
    """Refresh the current page.

    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.

    """
    logger.debug('Refreshing current page')
    _test.browser.refresh()

    if wait:
        _waitforbody()


def take_screenshot(filename='screenshot.png', add_timestamp=True):
    """Take a screenshot of the browser window.

    It is called automatically on failures when running in `-s` mode.

    :argument filename: The name of the file where the screenshot will be
        saved.
    :argument add_timestamp: If `True`, a timestamp will be added to the
        `filename`.
    :return: The path to the saved screenshot.

    """
    logger.debug('Capturing Screenshot')
    _make_results_dir()
    if add_timestamp:
        filename = _add_time_stamp(filename)
    screenshot_file = os.path.join(config.results_directory, filename)
    _test.browser.get_screenshot_as_file(screenshot_file)
    return screenshot_file


def _add_time_stamp(filename):
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    root, extension = os.path.splitext(filename)
    return '{0}-{1}{2}'.format(root, now, extension)


def save_page_source(filename='pagedump.html', add_timestamp=True):
    """Save the source of the currently opened page.

    It is called automatically on failures when running in `-s` mode.

    :argument filename: The name of the file where the page will be dumped.
    :argument add_timestamp: If `True`, a timestamp will be added to the
        `filename`.
    :return: The path to the saved file.

    """
    logger.debug('Saving page source')
    _make_results_dir()
    if add_timestamp:
        filename = _add_time_stamp(filename)
    # FIXME: Urgh, config.results_directory is a global set in
    # runtests() -- vila 2012-10-29
    page_source_file = os.path.join(config.results_directory, filename)
    with codecs.open(page_source_file, 'w', encoding='utf-8') as f:
        f.write(get_page_source())
    return page_source_file


def _make_results_dir():
    """Make results directory if it does not exist."""
    _test.assertIsNot(None, config.results_directory,
                      "results_directory should be set")
    try:
        os.makedirs(config.results_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def sleep(seconds):
    """Delay execution for the given number of seconds.

    :argument seconds: The number of seconds to sleep. It may be a floating
        point number for subsecond precision.

    """
    logger.debug('Sleeping %s secs' % seconds)
    time.sleep(seconds)


def _fix_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        if BASE_URL is None:
            _raise('BASE_URL is not set, did you call set_base_url ?')
        url = urljoin(BASE_URL, url)
    return url


def _add_trailing_slash(url):
    if not url.endswith('/'):
        url += '/'
    return url


def get_argument(name, default=_sentinel):
    """Get an argument from the one the test was called with.

    A test is called with arguments when it is executed by the `run_test`. You
    can optionally provide a default value that will be used if the argument
    is not set.

    :argument name: The name of the argument.
    :argument default: Value that will be used if the argument is not set.
    :raise: `LookupError` if you don't provide a default value and the
        argument is missing.
    :return: The argument value.

    """
    args = config.__args__

    value = args.get(name, default)
    if value is _sentinel:
        raise LookupError(name)
    return value


def run_test(name, **kwargs):
    """Execute a test, with the specified arguments.

    Tests are executed with the same browser (and browser session) as the
    test calling `run_test`. This includes whether or not Javascript is
    enabled.

    Before the test is called the timeout and base url are reset, but will be
    restored to their orginal value when `run_test` returns.

    :argument name: The name of the test to run. It is the test file name
        without the '.py'. You can specify tests in an alternative directory
        with relative path syntax. e.g.: `subdir/foo`.
    :argument kwargs: The arguments to pass to the test. Arguments can be
        retrieved by the test with `get_argument`.
    :return: The value of the `RESULT` variable, if set by the test being run.

    """
    # Delayed import to workaround circular imports.
    from sst import context
    logger.debug('Executing test: %s' % name)
    return context.run_test(name, kwargs)


def go_to(url='', wait=True):
    """Go to a URL.

    :arguement url: The URL to go to. If it is a relative URL it will be added
        to the base URL. You can change the base url for the test with
        `set_base_url`.
    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.

    """
    url = _fix_url(url)

    logger.debug('Going to... %s' % url)
    _test.browser.get(url)

    if wait:
        _waitforbody()


def go_back(wait=True):
    """Go one step backward in the browser history.

    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.

    """
    logger.debug('Going back one step in browser history')
    _test.browser.back()

    if wait:
        _waitforbody()


def assert_checkbox(id_or_elem):
    """Assert that an element is a checkbox.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a checkbox.
    :return: The element object.

    """
    elem = _get_elem(id_or_elem)
    _elem_is_type(elem, id_or_elem, 'checkbox')
    return elem


def assert_checkbox_value(id_or_elem, value):
    """Assert the value of a checkbox.

    :argument id_or_elem: The identifier of the element, or an element object.
    :argument value: The expected value of the checkbox. Pass `True` if you
        want to assert that the checkbox is selected, `False` otherwise.
    :raise: AssertionError if the element doesn't exist, if it is not a
        checkbox, or if the checkbox value is not the expected.

    """
    checkbox = assert_checkbox(id_or_elem)
    real = checkbox.is_selected()
    msg = 'Checkbox: %r - Has Value: %r' % (_element_to_string(checkbox), real)
    if real != value:
        _raise(msg)


def _element_to_string(element):
    """Get a string that can be used to recognize the element.

    If the element has an id, use it as it will uniquely identify the element.
    Otherwise, fall back to the text. If it has no text, to the value.
    Fallback to outerHTML as a last resort.

    """
    element_id = element.get_attribute('id')
    if element_id:
        return element_id
    else:
        element_text = get_text(element)
        if element_text:
            return element_text
        else:
            element_value = element.get_attribute('value')
            if element_value:
                return element_value
            else:
                return element.get_attribute('outerHTML')


def get_text(id_or_elem):
    """Return the text of an element.

    :argument id_or_elem: The identifier of the element, or an element object.
    :raise: AssertionError if the element doesn't exist.

    """
    element = _get_elem(id_or_elem)
    return element.text


def toggle_checkbox(id_or_elem):
    """Toggle the checkbox value.

    :argument id_or_elem: The identifier of the element, or an element object.
    :raise: AssertionError if the element doesn't exist or if it is not a
        checkbox.

    """
    checkbox = assert_checkbox(id_or_elem)
    element_string = _element_to_string(checkbox)
    logger.debug('Toggling checkbox: %r' % element_string)
    before = checkbox.is_selected()
    checkbox.click()
    after = checkbox.is_selected()
    if before == after:
        msg = 'Checkbox: %r - was not toggled, value remains: %r' \
            % (element_string, before)
        _raise(msg)


def set_checkbox_value(id_or_elem, new_value):
    """Set the value of a checkbox.

    :argument id_or_elem: The identifier of the element, or an element object.
    :argument new_value: The new value for the checkbox. Pass `True` if you
        want to select the checkbox, `False` otherwise.
    :raise: AssertionError if the element doesn't exist or if it is not a
        checkbox.

    """
    checkbox = assert_checkbox(id_or_elem)
    logger.debug(
        'Setting checkbox %r to %r' % (_element_to_string(checkbox),
                                       new_value))
    # There is no method to 'unset' a checkbox in the browser object
    current_value = checkbox.is_selected()
    if new_value != current_value:
        toggle_checkbox(id_or_elem)


def _make_keycode(key_to_make):
    """Return a keycode from a key name."""
    k = keys.Keys()
    keycode = k.__getattribute__(key_to_make.upper())
    return keycode


def simulate_keys(id_or_elem, key_to_press):
    """Simulate keys sent to an element.

    Available keys can be found in `selenium/webdriver/common/keys.py`

    e.g.::

        simulate_keys('text_1', 'BACK_SPACE')

    :argument id_or_elem: The identifier of the element, or an element object.
    :argument key_to_press: The name of the key to press.
    :raise: AssertionError if the element doesn't exist.

    """
    key_element = _get_elem(id_or_elem)
    msg = 'Simulating keypress on %r with %r key' \
        % (_element_to_string(key_element), key_to_press)
    logger.debug(msg)
    key_code = _make_keycode(key_to_press)
    key_element.send_keys(key_code)


_textfields = (
    'text', 'password', 'textarea', 'email',
    'url', 'search', 'number', 'file')


def assert_textfield(id_or_elem):
    """Assert that an element is a textfield, textarea or password box.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a text field.
    :return: The element object.

    """
    elem = _get_elem(id_or_elem)
    _elem_is_type(elem, id_or_elem, *_textfields)  # see _textfields tuple
    return elem


def write_textfield(id_or_elem, new_text, check=True, clear=True):
    """Write a text into a text field.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument new_text: The text to write.
    :argument check: If `True`, a check will be made to make sure that the
        text field contents after writing are the same as `new_text`.
    :argument clear: If `True`, the field will be cleared before writting into
        it.

    """
    textfield = assert_textfield(id_or_elem)
    msg = 'Writing to textfield %r with text %r' \
        % (_element_to_string(textfield), new_text)
    logger.debug(msg)

    # clear field with send_keys(), don't use clear() (see
    # http://code.google.com/p/selenium/issues/detail?id=214 for rationale)
    if clear:
        textfield.send_keys(keys.Keys().CONTROL, 'a')
        textfield.send_keys(keys.Keys().DELETE)

    if isinstance(new_text, unicode):
        textfield.send_keys(new_text)
    else:
        textfield.send_keys(str(new_text))
    if not check:
        return
    logger.debug('Check text wrote correctly')
    current_text = textfield.get_attribute('value')
    if current_text != new_text:
        msg = 'Textfield: %r - did not write. Text was: %r' \
            % (_element_to_string(textfield), current_text)
        _raise(msg)


def assert_link(id_or_elem):
    """Assert that an element is a link.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a link.
    :return: The element object.

    """
    link = _get_elem(id_or_elem)
    if link.tag_name != 'a':
        msg = 'The text %r is not part of a Link or a Link ID' \
            % _element_to_string(link)
        _raise(msg)
    return link


def get_link_url(id_or_elem):
    """Return the URL from a link.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a link.

    """
    logger.debug('Getting url from link %r' % id_or_elem)
    link = assert_link(id_or_elem)
    link_url = link.get_attribute('href')
    return link_url


def get_current_url():
    """Get the URL of the current page."""
    return _test.browser.current_url


def click_link(id_or_elem, check=False, wait=True):
    """Click a link.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument check: If `True`, the resulting URL will be check to be the same
        as the one on the link. Default is `False` because some links do
        redirects.
    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.
    :raise: AssertionError if the element doesn't exist or isn't a link.

    """
    link = assert_link(id_or_elem)
    link_url = link.get_attribute('href')

    logger.debug('Clicking link %r' % _element_to_string(link))
    link.click()

    if wait:
        _waitforbody()

    # some links do redirects - so we
    # don't check by default
    if check:
        assert_url(link_url)


def assert_displayed(id_or_elem):
    """Assert that an element is displayed.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't displayed.
    :return: The element object.

    """
    element = _get_elem(id_or_elem)
    if not element.is_displayed():
        message = 'Element is not displayed'
        _raise(message)
    return element


def click_element(id_or_elem, wait=True):
    """Click on an element of any kind not specific to links or buttons.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.

    """
    elem = _get_elem(id_or_elem)

    logger.debug('Clicking element %r' % _element_to_string(elem))
    elem.click()

    if wait:
        _waitforbody()


def assert_title(title):
    """Assert the page title.

    :argument title: The expected title.
    :raise: AssertionError if the title is not the expected.

    """
    real_title = _test.browser.title
    msg = 'Title is: %r. Should be: %r' % (real_title, title)
    if real_title != title:
        _raise(msg)


def assert_title_contains(text, regex=False):
    """Assert that the page title contains a text.

    :argument text: The expected text.
    :argument regex: If `True`, `text` will be used as a regex pattern.
    :raise: AssertionError if the title doesn't contain the expected text.

    """
    real_title = _test.browser.title
    msg = 'Title is: %r. Does not contain %r' % (real_title, text)
    if regex:
        if not re.search(text, real_title):
            _raise(msg)
    else:
        if not text in real_title:
            _raise(msg)


def assert_url(url):
    """Assert the current URL.

    :argument url: The expected URL. It can be an absolute URL or relative to
        the base url.
    :raise: AssertionError if the URL is not the expected.

    """
    url = _fix_url(url)
    url = _add_trailing_slash(url)
    real_url = _test.browser.current_url
    real_url = _add_trailing_slash(real_url)
    msg = 'Url is: %r. Should be: %r' % (real_url, url)
    if url != real_url:
        _raise(msg)


def assert_url_contains(text, regex=False):
    """Assert that the current URL contains a text.

    :argument text: The expected text.
    :argument regex: If `True`, `text` will be used as a regex pattern.
    :raise: AssertionError if the URL doesn't contain the expected text.

    """
    real_url = _test.browser.current_url
    msg = 'Url is %r. Does not contain %r' % (real_url, text)
    if regex:
        if not re.search(text, real_url):
            _raise(msg)
    else:
        if text not in real_url:
            _raise(msg)


def assert_url_network_location(netloc):
    """Assert the current URL's network location.

    :argument netloc: The expected network location. It is a string containing
        `domain:port`. In the case of port 80, `netloc` may contain domain
        only.
    :raise: AssertionError if the network location is not the expected.

    """
    real_netloc = urlparse(_test.browser.current_url).netloc
    if netloc != real_netloc:
        msg = 'Url network location is: %r. Should be: %r' % (
            real_netloc, netloc)
        _raise(msg)


_TIMEOUT = 10
_POLL = 0.1


def set_wait_timeout(timeout, poll=None):
    """Set the timeout and poll frequency used by `wait_for`.

    The default timeout at the start of a test is 10 seconds and the poll
    frequency is 0.1 seconds.

    :argument timeout: The new timeout in seconds.
    :argument poll: The poll frequency in seconds. It is how long `wait_for`
       should wait in between checking its condition.

    """
    msg = 'Setting wait timeout to %rs' % timeout
    if poll is not None:
        msg += ('. Setting poll time to %rs' % poll)
    logger.debug(msg)
    _set_wait_timeout(timeout, poll)


def _set_wait_timeout(timeout, poll=None):
    global _TIMEOUT
    global _POLL
    _TIMEOUT = timeout
    if poll is not None:
        _POLL = poll


def get_wait_timeout():
    """Get the timeout, in seconds, used by `wait_for`."""
    return _TIMEOUT


def _get_name(obj):
    try:
        return obj.__name__
    except:
        return repr(obj)


def _wait_for(condition, refresh_page, timeout, poll, *args, **kwargs):
    logger.debug('Waiting for %r' % _get_name(condition))
    # Disable logging levels equal to or lower than INFO.
    logging.disable(logging.INFO)
    result = None
    try:
        max_time = time.time() + timeout
        msg = _get_name(condition)
        while True:
            #refresh the page if requested
            if refresh_page:
                refresh()
            e = None
            try:
                result = condition(*args, **kwargs)
            except AssertionError as e:
                pass
            else:
                if result is not False:
                    break
            if time.time() > max_time:
                error = 'Timed out waiting for: %s' % msg
                if e:
                    error += '\nError during wait: %s' % e
                _raise(error)
            time.sleep(poll)
    finally:
        # Re-enable logging.
        logging.disable(logging.NOTSET)
    return result


# Selenium sometimes raises StaleElementReferenceException which leads to
# spurious failures. In those cases, using this decorator will retry the
# function once and avoid the spurious failure. This is a work-around until
# selenium is properly fixed and should not be abused (or there is a
# significant risk to hide bugs in the user scripts).
@retry_on_exception(StaleElementReferenceException, retries=1)
def wait_for(condition, *args, **kwargs):
    """Wait for an action to succeed.

    It is Useful for checking the results of actions that may take some time
    to complete.

    e.g::

        wait_for(assert_title, 'Some page title')

    :argument condition: A function to wait for. It can either be an action or
        a function that returns False or throws an AssertionError for failure,
        and returns anything different from False (including not returning
        anything) for success.
    :argument args: The arguments to pass to the `condition` function.
    :argument kwargs: The keyword arguments to pass to the `condition`
        function.
    :raise: AssertionError if `condition` does not succeed within the timeout.
        You can set the timeout for `wait_for` by calling `set_wait_timeout`
    :return: The value returned by `condition`.

    """
    return _wait_for(condition, False, _TIMEOUT, _POLL, *args, **kwargs)


def wait_for_and_refresh(condition, *args, **kwargs):
    """Wait for an action to succeed.

    It is Useful for checking the results of actions that may take some time
    to complete.

    The difference to `wait_for` is, that `wait_for_and_refresh()` will
    refresh the current page with after every condition check.

    :argument condition: A function to wait for. It can either be an action or
        a function that returns False or throws an AssertionError for failure,
        and returns anything different from False (including not returning
        anything) for success.
    :argument args: The arguments to pass to the `condition` function.
    :argument kwargs: The keyword arguments to pass to the `condition`
        function.
    :raise: AssertionError if `condition` does not succeed within the timeout.
        You can set the timeout for `wait_for` by calling `set_wait_timeout`
    :return: The value returned by `condition`.

    """
    return _wait_for(condition, True, _TIMEOUT, _POLL, *args, **kwargs)


def fails(action, *args, **kwargs):
    """Check that an action raises an AssertionError.

    If the action raises a different exception, it will be propagated normally.

    :argument action: A function to check.
    :argument args: The arguments to pass to the `action` function.
    :argument kwargs: The keyword arguments to pass to the `action` function.
    :raise: AssertionError if the `action` doesn't raise an AssertionError.

    """
    logger.debug('Trying action failure: %s' % _get_name(action))
    try:
        action(*args, **kwargs)
    except AssertionError:
        return
    msg = 'Action %r did not fail' % _get_name(action)
    _raise(msg)


def _get_elem(id_or_elem):
    if isinstance(id_or_elem, WebElement):
        return id_or_elem
    try:
        return _test.browser.find_element_by_id(id_or_elem)
    except (NoSuchElementException, WebDriverException):
        msg = 'Element with id: %r does not exist' % id_or_elem
        _raise(msg)


# Takes an optional 2nd input type for cases like textfield & password
#    where types are similar
def _elem_is_type(elem, name, *elem_types):
    try:
        result = elem.get_attribute('type')
    except NoSuchAttributeException:
        msg = 'Element has no type attribute'
        _raise(msg)
    if not result in elem_types:
        msg = 'Element %r is not one of %r' % (name, elem_types)
        _raise(msg)


def assert_dropdown(id_or_elem):
    """Assert that an element is a drop-down list.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a drop-down
        list.
    :return: The element object.

    """
    elem = _get_elem(id_or_elem)
    _elem_is_type(elem, id_or_elem, 'select-one')
    return elem


def set_dropdown_value(id_or_elem, text=None, value=None):
    """Set the value of a drop-down list.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument text: The text of the drop-down option that will be selected. If
        you pass the `text` argument, you shouldn't pass `value` too.
    :argument value: The value of the drop-down option that will be selected.
        If  you pass the `value` argument, you shouldn't pass `text` too.
    :raise: AssertionError if the element doesn't exist, if it isn't a
        drop-down list, if you passed both `text` and `value`, or if the option
        is not in the drop-down list.

    """
    elem = assert_dropdown(id_or_elem)
    logger.debug(
        'Setting %r option list to %r' % (_element_to_string(elem),
                                          text or value))
    if text and not value:
        for element in elem.find_elements_by_tag_name('option'):
            if element.text == text:
                element.click()
                return
        msg = 'The following option could not be found in the list: %r' % text
    elif value and not text:
        for element in elem.find_elements_by_tag_name('option'):
            if element.get_attribute("value") == value:
                element.click()
                return
        msg = 'The following option could not be found in the list: %r' % value
    else:
        msg = 'Use set_dropdown_value() with either text or value!'
    _raise(msg)


def assert_dropdown_value(id_or_elem, text_in):
    """Assert the selected option in a drop-list.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument text_in: The expected text of the selected option.
    :raise: AssertionError if the element doesn't exist, if it isn't a
        drop-down list or if the selected text is not the expected.

    """
    elem = assert_dropdown(id_or_elem)
    # Because there is no way to connect the current
    # text of a select element we have to use 'value'
    current = elem.get_attribute('value')
    for element in elem.find_elements_by_tag_name('option'):
        if text_in == element.text and \
                current == element.get_attribute('value'):
            return
    msg = 'The option is not currently set to: %r' % text_in
    _raise(msg)


def assert_radio(id_or_elem):
    """Assert that an element is a radio button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a radio
        button.
    :return: The element object.

    """
    elem = _get_elem(id_or_elem)
    _elem_is_type(elem, id_or_elem, 'radio')
    return elem


def assert_radio_value(id_or_elem, value):
    """Assert the value of a radio button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument value: The expected valueof the radio button. Pass `True` if you
        want to assert that the radio button is selected, `False` otherwise.
    :raise: AssertionError if the element doesn't exist, isn't a radio button,
        or the value is not the expected.

    """
    elem = assert_radio(id_or_elem)
    selected = elem.is_selected()
    msg = 'Radio %r should be set to: %s.' % (_element_to_string(elem), value)
    if value != selected:
        _raise(msg)


def set_radio_value(id_or_elem):
    """Select a radio button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a radio
        button.

    """
    elem = assert_radio(id_or_elem)
    logger.debug('Selecting radio button item %r' % _element_to_string(elem))
    elem.click()


def assert_text(id_or_elem, text):
    """Assert the text of an element.

    For text fields, it checks the value attribute instead of the text of the
    element.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument text: The expected text.
    :raise: AssertionError if the element doesn't exist or its text is not the
        expected.

    """
    real = _get_text_for_assertion(id_or_elem)
    if real != text:
        msg = 'Element text should be %r. It is %r.' % (text, real)
        _raise(msg)


def _get_text_for_assertion(id_or_elem):
    elem = _get_elem(id_or_elem)
    if _is_text_field(elem):
        value = elem.get_attribute('value')
        if not value:
            # The text field is empty.
            return ''
        else:
            return value
    else:
        text = get_text(elem)
        if not text:
            msg = 'Element %r has no text.' % _element_to_string(elem)
            _raise(msg)
        else:
            return text


def _is_text_field(element):
    # XXX refactor assert_textfield. It should be the other way around,
    # assert_textfield should call is_text_field. -- elopio 2013-04-18
    try:
        assert_textfield(element)
        return True
    except AssertionError:
        return False


def assert_text_contains(id_or_elem, text, regex=False):
    """Assert that the element contains a text.

    For text fields, it checks the value attribute instead of the text of the
    element.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument text: The expected text.
    :argument regex: If `True`, `text` will be used as a regex pattern.
    :raise: AssertionError if the element doesn't exist or its text doesn't
        contain the expected.

    """
    real = _get_text_for_assertion(id_or_elem)
    msg = 'Element text is %r. Does not contain %r.' % (real, text)
    if regex:
        if not re.search(text, real):
            _raise(msg)
    else:
        if text not in real:
            _raise(msg)


def _check_text(elem, text):
    return get_text(elem) == text


def _match_text(elem, regex):
    text = get_text(elem) or ''
    return bool(re.search(regex, text))


def get_elements(tag=None, css_class=None, id=None, text=None,
                 text_regex=None, **kwargs):
    """Return element objects.

    This action will find and return all matching elements by any of several
    attributes.

    :argument tag: The HTML tag of the element.
    :argument css_class: The value of the class attribute of the element.
    :argument id: The value of the id attribute of the element.
    :argument text: The text of the element. If you pass the `text` argument,
        you shouldn't pass the `text_regex` too.
    :argument text_regex: A regular expression to look for in the text of the
        element. If you pass the `text_regex` argument, you shouldn't pass
        the `text` too.
    :argument kwargs: Keyword arguments to look for values of additional
        attributes. The key will be the attribute name.
    :raise: TypeError if you pass both `text` and `text_regex`. AssertionError
        if no element matches the attributes.
    :return: A list with the elements that match.

    """
    if text and text_regex:
        raise TypeError("You can't use text and text_regex arguments")

    selector_string = ''
    if tag:
        selector_string = tag
    if css_class:
        css_class_selector = css_class.strip().replace(' ', '.')
        selector_string += ('.%s' % css_class_selector)
    if id:
        selector_string += ('#%s' % id)

    selector_string += ''.join(['[%s=%r]' % (key, value) for
                                key, value in kwargs.items()])
    try:
        if text and not selector_string:
            elems = _test.browser.find_elements_by_xpath(
                '//*[text() = %r]' % text)
        else:
            if not selector_string:
                msg = 'Could not identify element: no arguments provided'
                _raise(msg)
            elems = _test.browser.find_elements_by_css_selector(
                selector_string)
    except (WebDriverException, NoSuchElementException) as e:
        msg = 'Element not found: %s' % e
        _raise(msg)

    if text:
        # if text was specified, filter elements
        elems = [element for element in elems if _check_text(element, text)]
    elif text_regex:
        elems = [elem for elem in elems if _match_text(elem, text_regex)]

    if not elems:
        msg = 'Could not identify elements: 0 elements found'
        _raise(msg)

    return elems


def get_element(tag=None, css_class=None, id=None, text=None,
                text_regex=None, **kwargs):
    """Return an element object.

    This action will find and return one elements by any of several
     attributes.

    :argument tag: The HTML tag of the element.
    :argument css_class: The value of the class attribute of the element.
    :argument id: The value of the id attribute of the element.
    :argument text: The text of the element. If you pass the `text` argument,
        you shouldn't pass the `text_regex` too.
    :argument text_regex: A regular expression to look for in the text of the
        element. If you pass the `text_regex` argument, you shouldn't pass
        the `text` too.
    :argument kwargs: Keyword arguments to look for values of additional
        attributes. The key will be the attribute name.
    :raise: TypeError if you pass both `text` and `text_regex`. AssertionError
        if no element matches the attributes or if more than one element
        match.
    :return: The elements that matches.

    """
    elems = get_elements(tag=tag, css_class=css_class,
                         id=id, text=text, text_regex=text_regex, **kwargs)

    if len(elems) != 1:
        msg = 'Could not identify element: %s elements found' % len(elems)
        _raise(msg)

    return elems[0]


def exists_element(tag=None, css_class=None, id=None, text=None,
                   text_regex=None, **kwargs):
    """Check if an element exists.

    :argument tag: The HTML tag of the element.
    :argument css_class: The value of the class attribute of the element.
    :argument id: The value of the id attribute of the element.
    :argument text: The text of the element. If you pass the `text` argument,
        you shouldn't pass the `text_regex` too.
    :argument text_regex: A regular expression to look for in the text of the
        element. If you pass the `text_regex` argument, you shouldn't pass
        the `text` too.
    :argument kwargs: Keyword arguments to look for values of additional
        attributes. The key will be the attribute name.
    :raise: TypeError if you pass both `text` and `text_regex`.
    :return: True if the element exists, False otherwise.

    """
    try:
        get_elements(tag=tag, css_class=css_class, id=id, text=text,
                     text_regex=text_regex, **kwargs)
        return True
    except AssertionError:
        return False


def assert_element(tag=None, css_class=None, id=None, text=None,
                   text_regex=None, **kwargs):
    """Assert that an element exists.

    :argument tag: The HTML tag of the element.
    :argument css_class: The value of the class attribute of the element.
    :argument id: The value of the id attribute of the element.
    :argument text: The text of the element. If you pass the `text` argument,
        you shouldn't pass the `text_regex` too.
    :argument text_regex: A regular expression to look for in the text of the
        element. If you pass the `text_regex` argument, you shouldn't pass
        the `text` too.
    :argument kwargs: Keyword arguments to look for values of additional
        attributes. The key will be the attribute name.
    :raise: TypeError if you pass both `text` and `text_regex`. AssertionError
        if the element doesn't exist.

    """
    try:
        elems = get_elements(tag=tag, css_class=css_class, id=id, text=text,
                             text_regex=text_regex, **kwargs)
        return elems
    except AssertionError:
        msg = 'Could not assert element exists'
        _raise(msg)


def assert_button(id_or_elem):
    """Assert that an element is a button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a button.
    :return: The element object.

    """
    elem = _get_elem(id_or_elem)
    if elem.tag_name == 'button':
        return elem
    if elem.get_attribute('type') == 'button':
        return elem
    _elem_is_type(elem, id_or_elem, 'submit')
    return elem


def click_button(id_or_elem, wait=True):
    """Click a button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.
    :raise: AssertionError if the element doesn't exist or isn't a button.

    """
    button = assert_button(id_or_elem)

    logger.debug('Clicking button %r' % _element_to_string(button))
    button.click()

    if wait:
        _waitforbody()


def get_elements_by_css(selector):
    """Return all the elements that match a CSS selector.

    :argument selector: The CSS selector that will be used to search for the
        elements.
    :raise: AssertionError if no element matches the `selector`.
    :return: A list with the elements that match.

    """
    try:
        return _test.browser.find_elements_by_css_selector(selector)
    except (WebDriverException, NoSuchElementException) as e:
        msg = 'Element not found: %s' % e
        _raise(msg)


def get_element_by_css(selector):
    """Return the element that matches a CSS selector.

    :argument selector: The CSS selector that will be used to search for the
        element.
    :raise: AssertionError if no element matches the `selector` of if more
        than one match.
    :return: The elements that matches.

    """
    elements = get_elements_by_css(selector)
    if len(elements) != 1:
        msg = 'Could not identify element: %s elements found' % len(elements)
        _raise(msg)
    return elements[0]


def get_elements_by_xpath(selector):
    """Return all the elements that match an XPath selector.

    :argument selector: The XPath selector that will be used to search for the
        elements.
    :raise: AssertionError if no element matches the `selector`.
    :return: A list with the elements that match.

    """
    try:
        return _test.browser.find_elements_by_xpath(selector)
    except (WebDriverException, NoSuchElementException) as e:
        msg = 'Element not found: %s' % e
        _raise(msg)


def get_element_by_xpath(selector):
    """Return the element that matches an XPath selector.

    :argument selector: The XPath selector that will be used to search for the
        element.
    :raise: AssertionError if no element matches the `selector` of if more
        than one match.
    :return: The elements that matches.

    """
    elements = get_elements_by_xpath(selector)
    if len(elements) != 1:
        msg = 'Could not identify element: %s elements found' % len(elements)
        _raise(msg)
    return elements[0]


def _waitforbody():
    wait_for(get_element, tag='body')


def get_page_source():
    """Gets the source of the current page."""
    return _test.browser.page_source


def close_window():
    """ Closes the current window."""
    logger.debug('Closing the current window')
    _test.browser.close()


def switch_to_window(index_or_name=None):
    """Switch focus to a window.

    :argument index_or_name: The index or the name of the window that will be
        focused. If `None` focus will switch to the default window.
    :raise: Assertion error if the index is greater than the available windows,
        or the window couldn't be found.

    """
    if index_or_name is None:
        logger.debug('Switching to default window')
        _test.browser.switch_to_window('')
    elif isinstance(index_or_name, int):
        index = index_or_name
        window_handles = _test.browser.window_handles
        if index >= len(window_handles):
            msg = 'Index %r is greater than available windows.' % index
            _raise(msg)
        window = window_handles[index]
        try:
            logger.debug('Switching to window: %r' % window)
            _test.browser.switch_to_window(window)
        except NoSuchWindowException:
            msg = 'Could not find window: %r' % window
            _raise(msg)
    else:
        name = index_or_name
        try:
            logger.debug('Switching to window: %r' % name)
            _test.browser.switch_to_window(name)
        except NoSuchWindowException:
            msg = 'Could not find window: %r' % name
            _raise(msg)


def switch_to_frame(index_or_name=None):
    """Switch focus to a frame.

    :argument index_or_name: The index or the name of the frame that will be
        focused. If `None` focus will switch to the default frame.
    :raise: Assertion error if the frame couldn't be found.

    """
    if index_or_name is None:
        logger.debug('Switching to default content frame')
        _test.browser.switch_to_default_content()
    else:
        logger.debug('Switching to frame: %r' % index_or_name)
        try:
            _test.browser.switch_to_frame(index_or_name)
        except NoSuchFrameException:
            msg = 'Could not find frame: %r' % index_or_name
            _raise(msg)


def _alert_action(action, expected_text=None, text_to_write=None):
    """Accept or dismiss a JavaScript alert, confirmation or prompt.

    :argument action: The action to execute on the alert. It can be either
        `accept` or `dismiss`.
    :argument expected_text: The expected text of the alert. If `None`, the
        alert will not be checked.
    :argument text_to_write: The text to write in the alert prompt. If `None`,
        no text will be written.
    :raise: AssertionError if the alert doesn't contain the expected text, or
        if an unknown action is passed.

    """
    wait_for(_test.browser.switch_to_alert)
    alert = _test.browser.switch_to_alert()
    alert_text = alert.text
    if expected_text and expected_text != alert_text:
        error_message = 'Element text should be %r. It is %r.' \
            % (expected_text, alert_text)
        _raise(error_message)
    if text_to_write:
        alert.send_keys(text_to_write)
    if action == 'accept':
        alert.accept()
    elif action == 'dismiss':
        alert.dismiss()
    else:
        _raise('%r is an unknown action for an alert' % action)


def accept_alert(expected_text=None, text_to_write=None):
    """Accept a JavaScript alert, confirmation or prompt.

    Note that the action that opens the alert should not wait for a page with
    a body element. This means that you should call functions like
    `click_element` with the argument `wait=Fase`.

    :argument expected_text: The expected text of the alert. If `None`, the
        alert will not be checked.
    :argument text_to_write: The text to write in the alert prompt. If `None`,
        no text will be written.

    """
    logger.debug('Accepting Alert')
    _alert_action('accept', expected_text, text_to_write)


def dismiss_alert(expected_text=None, text_to_write=None):
    """Dismiss a JavaScript alert.

    Note that the action that opens the alert should not wait for a page with
    a body element. This means that you should call functions like
    `click_element` with the argument `wait=Fase`.

    :argument expected_text: The expected text of the alert. If `None`, the
        alert will not be checked.
    :argument text_to_write: The text to write in the alert prompt. If `None`,
        no text will be written.

    """
    logger.debug('Dismissing Alert')
    _alert_action('dismiss', expected_text, text_to_write)


def assert_table_headers(id_or_elem, headers):
    """Assert the headers of a table.

    The headers are the `<th>` tags.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument headers: A sequence of the expected headers.
    :raise: AssertionError if the element doesn't exist, or if its headers are
        not the expected.

    """
    logger.debug('Checking headers for %r' % (id_or_elem,))
    elem = _get_elem(id_or_elem)
    if not elem.tag_name == 'table':
        _raise('Element %r is not a table.' % (id_or_elem,))
    header_elems = elem.find_elements_by_tag_name('th')
    header_text = [get_text(e) for e in header_elems]
    if not header_text == headers:
        msg = ('Expected headers:%r. Actual headers%r\n' %
               (headers, header_text))
        _raise(msg)


def assert_table_has_rows(id_or_elem, num_rows):
    """Assert the number of rows of a table.

    The rows are the `<tr>` tags inside the `<tbody>`

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument num_rows: The expected number of rows.
    :raise: AssertionError if the element doesn't exist, it isn't a table, it
        doesn't have a tbody, or if its number of rows is not the expected.

    """
    logger.debug('Checking table %r has %s rows' % (id_or_elem, num_rows))
    elem = _get_elem(id_or_elem)
    if not elem.tag_name == 'table':
        _raise('Element %r is not a table.' % (id_or_elem,))
    body = elem.find_elements_by_tag_name('tbody')
    if not body:
        _raise('Table %r has no tbody.' % (id_or_elem,))
    rows = body[0].find_elements_by_tag_name('tr')
    if not len(rows) == num_rows:
        msg = 'Expected %s rows. Found %s.' % (num_rows, len(rows))
        _raise(msg)


def assert_table_row_contains_text(id_or_elem, row, contents, regex=False):
    """Assert that a row of a table contains a text.

    The row will be looked for inside the <tbody>, to check headers use
    `assert_table_headers`.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument row: The row index, starting from 0.
    :argument contents: A sequence of strings. Each where string will should
        be the same as the text of the corresponding column.
    :argument regex: If `True`, the strings in `contents` will be used as
        regular expressions.
    :raise: AssertionError if the element doesn't exist, it isn't a table, it
        doesn't have a tbody, if the rows number if bigger than the number of
        rows in the table, or if the row texts doesn't match the expected.

    """
    logger.debug(
        'Checking the contents of table %r, row %s.' % (id_or_elem, row))
    elem = _get_elem(id_or_elem)
    if not elem.tag_name == 'table':
        _raise('Element %r is not a table.' % (id_or_elem,))
    body = elem.find_elements_by_tag_name('tbody')
    if not body:
        _raise('Table %r has no tbody.' % (id_or_elem,))
    rows = body[0].find_elements_by_tag_name('tr')
    if len(rows) <= row:
        msg = 'Asked to fetch row %s. Highest row is %s' % (row, len(rows) - 1)
        _raise(msg)
    columns = rows[row].find_elements_by_tag_name('td')
    cells = [get_text(e) for e in columns]
    if not regex:
        success = cells == contents
    elif len(contents) != len(cells):
        success = False
    else:
        success = all(re.search(expected, actual) for expected, actual in
                      zip(contents, cells))
    if not success:
        msg = ('Expected row contents: %r. Actual contents: %r' %
               (contents, cells))
        _raise(msg)


def assert_attribute(id_or_elem, attribute, value, regex=False):
    """Assert an the value of an element's attribute.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument attribute: The name of the attribute to assert.
    :argument value: The expected value.
    :argument regex: If `True`, the `value` will be used as regular expression.
    :raise: AssertionError if the element doesn't exist, or if the value is not
        the expected.

    """
    elem = _get_elem(id_or_elem)
    logger.debug(
        'Checking attribute %r of %r' % (attribute, _element_to_string(elem)))
    actual = elem.get_attribute(attribute)
    if not regex:
        success = value == actual
    else:
        success = actual is not None and re.search(value, actual)
    if not success:
        msg = 'Expected attribute: %r. Actual attribute: %r' % (value, actual)
        _raise(msg)


def assert_css_property(id_or_elem, property, value, regex=False):
    """Assert the value of an element's CSS property.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument property: The name of the CSS property to assert.
    :argument value: The expected value.
    :argument regex: If `True`, the `value` will be used as regular expression.
    :raise: AssertionError if the element doesn't exist, or if the value is not
        the expected.

    """
    elem = _get_elem(id_or_elem)
    logger.debug(
        'Checking css property %r: %r of %r' % (
            property, value, _element_to_string(elem)))
    actual = elem.value_of_css_property(property)
    # some browsers return string with space padded commas, some don't.
    actual = actual.replace(', ', ',')
    if not regex:
        success = value == actual
    else:
        success = actual is not None and re.search(value, actual)
    if not success:
        msg = 'Expected property: %r. Actual property: %r' % (value, actual)
        _raise(msg)


def check_flags(*args):
    """Skip a test if one of the flags wasn't supplied at the command line.

    Flags are case-insensitive.

    :argument args: A list of flags to check.

    """
    if not _check_flags:
        # Flag checking disabled
        return
    missing = set(arg.lower() for arg in args) - set(config.flags)
    if missing:
        _msg = 'Flags required but not used: %s' % ', '.join(missing)
        skip(_msg)


def assert_equal(first, second):
    """Assert that two objects are equal."""
    if _test is None:
        assert first == second
    else:
        _test.assertEqual(first, second)


def assert_not_equal(first, second):
    """Assert that two objects are not equal."""
    if _test is None:
        assert first != second
    else:
        _test.assertNotEqual(first, second)


def add_cleanup(func, *args, **kwargs):
    """Add a function to be called when the test is completed.

    Functions added are called on a LIFO basis and are called on test failure
    or success.

    They allow a test to clean up after itself.

    :argument func: The function to call.
    :argument args: The arguments to pass to `func`.
    :argument kwargs: The keyword arguments to pass to `func`.

    """
    _test.addCleanup(func, *args, **kwargs)


def get_cookies():
    """Get the cookies of the current session.

    :return: A set of dicts with the session cookies.

    """
    return _test.browser.get_cookies()


def clear_cookies():
    """Clear the cookies of the current session."""
    logger.debug('Clearing browser session cookies')
    _test.browser.delete_all_cookies()


def set_window_size(width, height):
    """Resize the current window.

    :argument width: The new width for the window, in pixels.
    :argument height: The new height for the window, in pixels.

    """
    logger.debug('Resizing window to: %s x %s' % (width, height))

    _test.browser.set_window_size(width, height)

    def _was_resized():
        w, h = get_window_size()
        if (w == width) and (h == height):
            return True
        else:
            return False

    wait_for(_was_resized)


def get_window_size():
    """Get the current window size.

    :return: A pair (width, height), in pixels.

    """
    results = _test.browser.get_window_size()
    width = results['width']
    height = results['height']
    return (width, height)


def execute_script(script, *args):
    """Execute JavaScript in the currently selected frame or window.

    Within the script, use `document` to refer to the current document.

    For example::

        execute_script('document.title = "New Title"')

    :argument script: The script to execute.
    :argument args: A list of arguments to be made available to the script.
    :return: The return value of the script.

    """
    logger.debug('Executing script')
    return _test.browser.execute_script(script, *args)


def get_element_source(id_or_elem):
    """Get the innerHTML source of an element.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist

    """
    elem = _get_elem(id_or_elem)
    return elem.get_attribute('innerHTML')
