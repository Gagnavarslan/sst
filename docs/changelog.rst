
===================
    SST - Changelog
===================

* downloads available at `Python Package Index <http://pypi.python.org/pypi/sst#downloads>`_


Official Releases:
------------------

version **0.2.3** (?? ?? ??)
*******************************

* added the ``save_page_source`` action.
* added a parameter to ``take_screenshot`` to include a timestamp in the file 
  name
* expose the SSTTestCase class which is used internally to create test cases
* start implementing an internal test suite (#1084007)
* ensure Xvfb is properly killed if sst-run is interrupted (#1084006)
* protect ``wait_for`` from transient failures caused by
  StaleElementReferenceException (#1084008)
* include test class full name in test ids for SSTScriptTestCase (#1087606)
* add support for xfvb to SSTTestCase (#1084011)
* removed ``junitxml`` package dependency for junit-style xml output
* in xml report mode, progress is printed to stdout during test run
* added ``get_window_size`` action
* added ``set_window_size`` action
* added ``testtools`` dependency
* command-line test names may use glob patterns for discovery
* added `--collect-only` option to `sst-run` command line


version **0.2.2** (2012 Nov 4)
*******************************

* added ``wait_for_and_refresh`` action
* ``set_dropdown_value`` can set text or value now
* added ``add_cleanup`` action
* made internal tests compatible with Django 1.4
* added ``config.cache``, a per test cache (dictionary) cleared at the start of
  every test
* added ``--extended-tracebacks`` command line option
* added ``get_cookies`` and ``clear_cookies`` actions
* added ``execute_script`` action
* added ``get_element_source`` action
* removed PyVirtualDisplay dependency; replaced with lightweight Xvfb wrapper


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
