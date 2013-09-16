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

"""Python testtools extension for running unittest suites concurrently.

The `testtools` project provides a ConcurrentTestSuite class, but does
not provide a `make_tests` implementation needed to use it.

This allows you to parallelize a test run across a configurable number of
worker processes. On multi-core CPUs, this will speed up CPU-bound test
runs. In any case it is useful for IO-bound tests that spend most of their time
waiting for data to arrive from disk or network and as such benefit from
concurrency.

Unix only.
"""

import os
import sys
import traceback
import unittest
import itertools

import subunit
from subunit import test_results
import testtools


class TestInOtherProcess(subunit.ProtocolTestCase):
    # Should be in subunit, I think. RBC.
    def __init__(self, stream, pid):
        super(TestInOtherProcess, self).__init__(stream)
        self.pid = pid

    def run(self, result):
        try:
            super(TestInOtherProcess, self).run(result)
        finally:
            pid, status = os.waitpid(self.pid, 0)
        # GZ 2011-10-18: If status is nonzero, should report to the result
        #                that something went wrong.


def fork_for_tests(concurrency_num=1):
    """Implementation of `make_tests` used to construct `ConcurrentTestSuite`.

    :param concurrency_num: number of processes to use.
    """
    def do_fork(suite):
        """Take suite and start up multiple runners by forking (Unix only).

        :param suite: TestSuite object.

        :return: An iterable of TestCase-like objects which can each have
        run(result) called on them to feed tests to result.
        """
        tests = []
        test_blocks = partition_tests(suite, concurrency_num)
        # Clear the tests from the original suite so it doesn't keep them alive
        suite._tests[:] = []
        for process_tests in test_blocks:
            process_suite = unittest.TestSuite(process_tests)
            # Also clear each split list so new suite has only reference
            process_tests[:] = []
            c2pread, c2pwrite = os.pipe()
            pid = os.fork()
            if pid == 0:
                try:
                    stream = os.fdopen(c2pwrite, 'wb', 1)
                    os.close(c2pread)
                    # Leave stderr and stdout open so we can see test noise
                    # Close stdin so that the child goes away if it decides to
                    # read from stdin (otherwise its a roulette to see what
                    # child actually gets keystrokes for pdb etc).
                    sys.stdin.close()
                    result = test_results.AutoTimingTestResultDecorator(
                        subunit.TestProtocolClient(stream)
                    )
                    process_suite.run(result)
                except:
                    # Try and report traceback on stream, but exit with error
                    # even if stream couldn't be created or something else
                    # goes wrong.  The traceback is formatted to a string and
                    # written in one go to avoid interleaving lines from
                    # multiple failing children.
                    try:
                        stream.write(traceback.format_exc())
                    finally:
                        os._exit(1)
                os._exit(0)
            else:
                os.close(c2pwrite)
                stream = os.fdopen(c2pread, 'rb', 1)
                test = TestInOtherProcess(stream, pid)
                tests.append(test)
        return tests
    return do_fork


def partition_tests(suite, count):
    """Partition suite into count lists of tests."""
    # This just assigns tests in a round-robin fashion.  On one hand this
    # splits up blocks of related tests that might run faster if they shared
    # resources, but on the other it avoids assigning blocks of slow tests to
    # just one partition.  So the slowest partition shouldn't be much slower
    # than the fastest.
    partitions = [list() for i in range(count)]
    tests = testtools.iterate_tests(suite)
    for partition, test in zip(itertools.cycle(partitions), tests):
        partition.append(test)
    return partitions
