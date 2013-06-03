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


import itertools
import os
import sys
import traceback
import unittest

from subunit import (
    ProtocolTestCase,
    TestProtocolClient,
)
from subunit.test_results import AutoTimingTestResultDecorator

from testtools import iterate_tests


# You can parallelize a test run across a configurable number of worker
# processes. While this can speed up CPU-bound test runs, it is mainly
# useful for IO-bound tests that spend most of their time waiting for
# data to arrive from someplace else and can benefit from parallelization.

def fork_for_tests(suite, concurrency_num=1):
    """Take suite and start up multiple runners by forking()

    :return: An iterable of TestCase-like objects which can each have
        run(result) called on them to feed tests to result.
    """
    result = []
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
                subunit_result = AutoTimingTestResultDecorator(
                    TestProtocolClient(stream)
                )
                process_suite.run(subunit_result)
            except:
                # Try and report traceback on stream, but exit with error even
                # if stream couldn't be created or something else goes wrong.
                # The traceback is formatted to a string and written in one go
                # to avoid interleaving lines from multiple failing children.
                try:
                    stream.write(traceback.format_exc())
                finally:
                    os._exit(1)
            os._exit(0)
        else:
            os.close(c2pwrite)
            stream = os.fdopen(c2pread, 'rb', 1)
            test = TestInOtherProcess(stream, pid)
            result.append(test)
    return result


def partition_tests(suite, count):
    """Partition suite into count lists of tests."""
    # This just assigns tests in a round-robin fashion.  On one hand this
    # splits up blocks of related tests that might run faster if they shared
    # resources, but on the other it avoids assigning blocks of slow tests to
    # just one partition.  So the slowest partition shouldn't be much slower
    # than the fastest.
    partitions = [list() for i in range(count)]
    tests = iterate_tests(suite)
    for partition, test in itertools.izip(itertools.cycle(partitions), tests):
        partition.append(test)
    return partitions


class TestInOtherProcess(ProtocolTestCase):
    def __init__(self, stream, pid):
        ProtocolTestCase.__init__(self, stream)
        self.pid = pid

    def run(self, result):
        try:
            ProtocolTestCase.run(self, result)
        finally:
            pid, status = os.waitpid(self.pid, 0)
