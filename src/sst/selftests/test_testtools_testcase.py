from testtools import TestCase

# make sure a regular testtools.TestCase works with runner


class TestTestToolsTestCase(TestCase):

    def shortDescription(self):
        return None

    def test_true(self):
        self.assertTrue(True)
