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

import testtools

from sst import filters


def create_tests_from_ids(ids):
    suite = unittest.TestSuite()

    def test_id(name):
        return lambda: name

    for tid in ids:
        # We need an existing method to create a test. Arbitrarily, we use
        # id(), that souldn't fail ;) We won't run the test anyway.
        test = unittest.TestCase(methodName='id')
        # We can't define the lambda here or 'name' stay bound to the
        # variable instead of the value, use a proxy to capture the value.
        test.id = test_id(tid)
        suite.addTest(test)
    return suite


class TestFilterTestsById(testtools.TestCase):

    def assertFiltered(self, expected, condition, ids):
        """Check that ``condition`` filters tests created from ``ids``."""
        filtered = filters.filter_suite(condition, create_tests_from_ids(ids))
        self.assertEqual(expected,
                         [t.id() for t in testtools.iterate_tests(filtered)])

    def test_filter_none(self):
        test_names = ['foo', 'bar']
        self.assertFiltered(test_names, lambda t: True, test_names)

    def test_filter_all(self):
        test_names = ['foo', 'bar']
        self.assertFiltered([], lambda t: False, test_names)

    def test_filter_start(self):
        self.assertFiltered(['foo', 'footix'],
                            lambda t: t.id().startswith('foo'),
                            ['foo', 'footix', 'bar', 'baz', 'fo'])

    def test_filter_in(self):
        self.assertFiltered(['bar', 'baz'],
                            lambda t: t.id() in ('bar', 'baz'),
                            ['foo', 'footix', 'bar', 'baz', 'fo'])

    def test_filter_single(self):
        self.assertFiltered(['bar'],
                            lambda t: t.id() == 'bar',
                            ['foo', 'bar', 'baz'])

    def test_filter_regexp(self):
        ba = re.compile('ba')
        self.assertFiltered(['bar', 'baz', 'foobar'],
                            lambda t: bool(ba.search(t.id())),
                            ['foo', 'bar', 'baz', 'foobar', 'qux'])


class TestFilterTestsByRegexps(testtools.TestCase):

    def assertFiltered(self, expected, regexps, ids):
        """Check that ``regexps`` filters tests created from ``ids``."""
        filtered = filters.include_regexps(regexps, create_tests_from_ids(ids))
        self.assertEqual(expected,
                         [t.id() for t in testtools.iterate_tests(filtered)])

    def test_filter_none(self):
        self.assertFiltered(['foo', 'bar'], [], ['foo', 'bar'])

    def test_filter_one_regexp(self):
        self.assertFiltered(['foo', 'foobar', 'barfoo'], ['.*foo.*'],
                            ['foo', 'foobar', 'barfoo', 'baz'])

    def test_filter_several_regexps(self):
        self.assertFiltered(['foo', 'foobar', 'barfoo'], ['foo', 'arf'],
                            ['foo', 'foobar', 'barfoo', 'baz'])

    def test_filter_unanchored(self):
        self.assertFiltered(['foo', 'foobar', 'barfoo', 'xfoox'], ['foo'],
                            ['foo', 'foobar', 'barfoo', 'baz', 'xfoox'])

    def test_filter_start(self):
        self.assertFiltered(['foo', 'foobar'], ['^foo'],
                            ['foo', 'foobar', 'barfoo', 'baz', 'xfoox'])

    def test_filter_ends(self):
        self.assertFiltered(['foo', 'barfoo'], ['foo$'],
                            ['foo', 'foobar', 'barfoo', 'baz', 'xfoox'])


class TestFilterTestsByExcludedPrefixes(testtools.TestCase):

    def assertFiltered(self, expected, regexps, ids):
        """Check that ``prefixes`` filters tests created from ``ids``."""
        filtered = filters.exclude_regexps(regexps,
                                           create_tests_from_ids(ids))
        self.assertEqual(expected,
                         [t.id() for t in testtools.iterate_tests(filtered)])

    def test_no_excludes(self):
        self.assertFiltered(['foo', 'bar'], [], ['foo', 'bar'])

    def test_one_exclude(self):
        self.assertFiltered(['bar'], ['foo'],
                            ['foo.bar', 'bar', 'foo.baz'])

    def test_several_excludes(self):
        self.assertFiltered(['bar'], ['foo', 'bar.'],
                            ['foo.bar', 'bar', 'foo.baz', 'bar.baz'])
