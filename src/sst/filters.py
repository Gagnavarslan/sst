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
#

import re
import unittest


def filter_suite(condition, suite):
    """Return tests for which ``condition`` is True in ``suite``.

    :param condition: A callable receiving a test and returning True if the
        test should be kept.

    :param suite: A test suite that can be iterated. It contains either tests
        or suite inheriting from ``unittest.TestSuite``.

    ``suite`` is a tree of tests and suites, the returned suite respect the
    received suite layout, only removing empty suites.
    """
    filtered_suite = suite.__class__()
    for test in suite:
        if issubclass(test.__class__, unittest.TestSuite):
            # We received a suite, we'll filter a suite
            filtered = filter_suite(condition, test)
            if filtered.countTestCases():
                # Keep only non-empty suites
                filtered_suite.addTest(filtered)
        elif condition(test):
            # The test is kept
            filtered_suite.addTest(test)
    return filtered_suite


def include_regexps(regexps, suite):
    """Returns the tests that match one of ``regexps``.

    :param regexps: A list of test id regexps (strings, will be compiled
        internally) to include. All tests are included if no regexps are
        provided.

    :param suite: The test suite to filter.
    """
    if not regexps:
        return suite

    def matches_one_of(test):
        tid = test.id()
        for reg in regexps:
            if re.search(reg, tid) is not None:
                return True
        return False
    return filter_suite(matches_one_of, suite)


def exclude_regexps(regexps, suite):
    """Returns the tests whose id does not match with any of the regexps."""
    if not regexps:
        # No regexpes, no filtering
        return suite

    def matches_none_of(test):
        # A test is kept if its id matches none of the 'excludes' regexps
        tid = test.id()
        for regexp in regexps:
            if re.search(regexp, tid):
                return False
        return True
    return filter_suite(matches_none_of, suite)
