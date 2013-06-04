from sst.actions import *
from sst import cases


class TestUbuntu(cases.SSTTestCase):

    def test_ubuntu_home_page(self):
        go_to('http://www.ubuntu.com/')
        assert_title_contains('Ubuntu')
