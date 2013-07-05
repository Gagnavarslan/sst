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

from cStringIO import StringIO
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
        self.assertEqual(1, opts.concurrency)
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

    def test_concurrency(self):
        opts, args = self.parse_args(['--concurrency', '4'])
        self.assertEqual(4, opts.concurrency)
        opts, args = self.parse_args(['--concurrency=3'])
        self.assertEqual(3, opts.concurrency)
        opts, args = self.parse_args(['-c', '7'])
        self.assertEqual(7, opts.concurrency)
        opts, args = self.parse_args(['-c5'])
        self.assertEqual(5, opts.concurrency)


class TestCleanups(testtools.TestCase):

    def test_cleanup_now_consumes(self):
        out = StringIO()
        clean = command.Cleaner(out)
        self.called = False

        def cleaning():
            self.called = True
        clean.add('cleaning', cleaning)
        clean.cleanup_now()
        self.assertTrue(self.called)
        self.assertEqual('cleaning', out.getvalue())
        self.assertEqual([], clean.cleanups)

    def test_cleanup_catches_exceptions(self):
        out = StringIO()
        clean = command.Cleaner(out)

        def boom():
            1 / 0
        clean.add('boom\n', boom)
        clean.cleanup_now()
        lines = out.getvalue().splitlines()
        self.assertLess(2, len(lines))
        self.assertEqual('boom', lines[0])
        # We don't care about the detailed traceback as long as it ends up with
        # the expected exception.
        self.assertEqual(
            'ZeroDivisionError: integer division or modulo by zero',
            lines[-1])
        self.assertEqual([], clean.cleanups)

    def test_keyboard_interrupts(self):
        out = StringIO()
        clean = command.Cleaner(out)

        self.called = False

        def cleaning():
            self.called = True

        clean.add('cleaning', cleaning)

        def kb_interrupts():
            raise KeyboardInterrupt

        clean.add('interrupts', kb_interrupts)
        self.assertRaises(KeyboardInterrupt, clean.cleanup_now)
        self.assertEquals('interrupts', out.getvalue())
        # The cleanups are still in place
        self.assertEqual([('interrupts', kb_interrupts, (), {}),
                          ('cleaning', cleaning, (), {})],
                         clean.cleanups)
        # And the first cleanup has not been called
        self.assertFalse(self.called)

    def test_add_collects_args(self):
        clean = command.Cleaner()

        def func(*args, **kwargs):
            pass
        clean.add('foo', func, 1, 2, foo=4, bar=12)
        self.assertEquals(('foo', func, (1, 2), {'foo': 4, 'bar': 12}),
                          clean.cleanups[0])

    def test_usable_as_context_manager(self):
        self.called = False

        def cleaning():
            self.called = True

        with command.Cleaner() as cleaner:
            cleaner.add('cleaning', cleaning)
            self.assertFalse(self.called)

        self.assertTrue(self.called)
