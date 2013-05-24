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

import testtools

from sst import command


class TestArgParsing(testtools.TestCase):

    def parse_args(self, provided_args):
        # command.get_opts_run and friends relies on optparse defaulting to
        # sys.argv[1:]. To comply with that, we add a dummy first arg to
        # represent the script name and remove it from the returned args.
        opts, remaining_args = command.get_opts_run(
            ['dummy-for-tests'] + provided_args)
        self.assertEqual('dummy-for-tests', remaining_args[0])
        return opts, remaining_args[1:]

    def test_default_values(self):
        opts, args = self.parse_args([])
        self.assertIs(None, opts.excludes)
        self.assertEqual([], args)

    def test_single_regexp(self):
        opts, args = self.parse_args(['foo'])
        self.assertEquals(['foo'], args)
        self.assertIs(None, opts.excludes)

    def test_multiple_regexps(self):
        opts, args = self.parse_args(
            ['foo', 'bar', 'baz'])
        self.assertEquals(['foo', 'bar', 'baz'], args)
        self.assertIs(None, opts.excludes)

    def test_single_exclude(self):
        opts, args = self.parse_args(['--exclude', 'foo'])
        self.assertEquals(['foo'], opts.excludes)
        self.assertEqual([], args)

    def test_multiple_excludes(self):
        opts, args = self.parse_args(
            ['--exclude', 'foo', '-e', 'bar', '-ebaz'])
        self.assertEquals(['foo', 'bar', 'baz'], opts.excludes)
        self.assertEqual([], args)
