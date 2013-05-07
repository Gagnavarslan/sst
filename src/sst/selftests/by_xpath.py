import sst
import sst.actions

# xpath locator tests
#
# see: http://seleniumhq.org/docs/appendix_locating_techniques.html


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/')

sst.actions.get_element_by_xpath("//p[contains(@class, 'unique_class')]")
sst.actions.get_element_by_xpath("//a[contains(@id, 'band_link')]")
sst.actions.get_element_by_xpath("//a[starts-with(@id, 'the_band_l')]")

sst.actions.get_elements_by_xpath('//p')
sst.actions.get_elements_by_xpath("//p[contains(@class, 'some_class')]")

sst.actions.fails(
    sst.actions.get_element_by_xpath, '//doesnotexist')
sst.actions.fails(
    sst.actions.get_element_by_xpath, "//a[contains(@id, 'doesnotexist')]")

assert len(sst.actions.get_elements_by_xpath(
    '//doesnotexist'
)) == 0
assert len(sst.actions.get_elements_by_xpath(
    "//p[contains(@class, 'unique_class')]"
)) == 1
assert len(sst.actions.get_elements_by_xpath(
    "//p[contains(@class, 'some_class')]"
)) == 2
