
===================
    SST - Changelog
===================

* downloads available at `Python Package Index <http://pypi.python.org/pypi/sst#downloads>`_


Official Releases:
------------------


version **0.2.2** (2012 ??? ??)
*******************************

* add ``wait_for_and_refresh`` action
* ``set_dropdown_value`` can set text or value now 

version **0.2.1** (2012 Apr 22)
*******************************

* handle ``file:`` based urls (static, non-http)
* added ``assert_equal`` and ``assert_not_equal`` actions
* added ``refresh`` action
* with `debug` on, current exception is printed before entering pdb


version **0.2.0** (2012 Feb 26)
*******************************

* ``wait_for`` displays tracebacks
* screenshots not taken on skipped test
* test runner stops cleanly on keyboard interrupt
* Firefox set as default browser in ``sst.config`` for interactive use
* new ``text_regex`` parameter for filtering ``get_element`` / ``get_elements`` result sets
* new Actions:

 * ``assert_attribute``
 * ``assert_css_property``
 * ``assert_table_row_contains_text``
 * ``assert_table_headers``
 * ``assert_table_has_rows actions``
 * ``go_back``

* new command line options:

 * ``--with-flags=WITH_FLAGS``
 * ``--disable-flag-skips``

* performance tracing (har recording) using Browsermob proxy.  enabled with command line option:

 * ``--browsermob=``


version **0.1.0** (2012 Jan 01)
*******************************

* initial release: `SST on PyPI <http://pypi.python.org/pypi/sst>`_
* dev project: `selenium-simple-test on Launchpad <https://launchpad.net/selenium-simple-test>`_
