from sst import runtests


class TestBoth(runtests.SSTTestCase):

    def test_one(self):
        assert True

    def test_two(self):
        assert True
