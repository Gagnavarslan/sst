from sst.actions import *
from sst import runtests


class TestUbuntu(runtests.SSTTestCase):

    def test_ubuntu_home_page(self):
        go_to('http://www.ubuntu.com/')
        assert_title_contains('Ubuntu')
