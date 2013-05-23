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
import fnmatch
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


def filter_by_patterns(patterns, suite):
    """Returns the tests that match one of ``patterns``.

    :param patterns: A list of test name globs to include. All tests are
        included if no patterns are provided.

    :param suite: The test suite to filter.
    """
    if not patterns:
        return suite

    def filter_test_patterns(test):
        for pattern in patterns:
            if fnmatch.fnmatchcase(test.id(), pattern):
                return True
        return False
    return filter_suite(filter_test_patterns, suite)


def filter_by_regexps(regexps, suite):
    """Returns the tests that match one of ``regexps``.

    :param regexps: A list of test id regexps (strings, will be compiled
        internally) to include. All tests are included if no regexps are
        provided.

    :param suite: The test suite to filter.
    """
    if not regexps:
        return suite

    def filter_test_regexps(test):
        for reg in regexps:
            if re.search(reg, test.id()) is not None:
                return True
        return False
    return filter_suite(filter_test_regexps, suite)


def include_prefixes(prefixes, suite):
    """Returns the tests whose id starts with one of the prefixes."""
    if not prefixes:
        # No prefixes, no filtering
        return suite

    def starts_with_one_of(test):
        # A test is kept if its id starts with one of the prefixes
        tid = test.id()
        for prefix in prefixes:
            if tid.startswith(prefix):
                return True
        return False
    return filter_suite(starts_with_one_of, suite)


def exclude_prefixes(prefixes, suite):
    """Returns the tests whose id does not start with any of the prefixes."""
    if not prefixes:
        # No prefixes, no filtering
        return suite

    def starts_with_none_of(test):
        # A test is kept if its id matches none of the 'excludes' prefixes
        tid = test.id()
        for prefix in prefixes:
            if tid.startswith(prefix):
                return False
        return True
    return filter_suite(starts_with_none_of, suite)
