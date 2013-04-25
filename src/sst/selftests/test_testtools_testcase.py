from testtools import TestCase

# make sure a regular testtools.TestCase works with runner


class TestTestToolsTestCase(TestCase):

    def test_true(self):
        self.assertTrue(True)
