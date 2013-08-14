.. toctree::
   :hidden:

   actions
   remote
   changelog
   releasing
   packaging

============================
    SST - Web Test Framework
============================

:Web Home: http://testutils.org/sst
:Project Home: https://launchpad.net/selenium-simple-test
:PyPI: http://pypi.python.org/pypi/sst
:License: Apache License, Version 2.0
:Author: Copyright (c) 2011-2013 Canonical Ltd.


---------------------------------
    Automated Testing with Python
---------------------------------

SST (selenium-simple-test) is a web test framework that uses Python
to generate functional browser-based tests.

Tests are made up of scripts or test case classes, created by composing
actions that drive a browser and assert conditions. You have the flexibilty
of the full Python language, along with a convenient set of functions to
simplify web testing.

SST consists of:

 * user actions and assertions (API) in Python
 * test case loader (generates/compiles scripts to unittest cases)
 * console test runner
 * concurrent/parallel tests
 * data parameterization/injection
 * selectable output reports
 * selectable browsers
 * headless (xvfb) mode
 * screenshots on errors

Test output is displayed to the console and optionally saved as 
JUnit-compatible XML for compatibility with CI systems.


-----------
    Install
-----------

SST can be installed from `PyPI <http://pypi.python.org/pypi/sst>`_ using
`pip <http://www.pip-installer.org>`_::

    pip install -U sst

For example, on an Ubuntu/Debian system, you could Install SST (system-wide)
like this::

    $ sudo apt-get install python-pip xvfb
    $ sudo pip install -U sst

or with a `virtualenv`::

    $ sudo apt-get install python-virtualenv xvfb
    $ virtualenv ENV
    $ source ENV/bin/activate
    (ENV)$ pip install sst

* note: `xvfb` is only needed if you want to run SST in headless mode


---------------------------
    Example SST test script
---------------------------

a sample test case in SST::

    from sst.actions import *

    go_to('http://www.ubuntu.com/')
    assert_title_contains('Ubuntu')


------------------------------------
    Running a test with SST
------------------------------------

Create a Python script (.py) file, and add your test code.

Then call your test script from the command line, using `sst-run`::

    $ sst-run mytest

* note: you don't add the .py extension to your test invocation


-----------------------------------
    Actions reference (sst.actions)
-----------------------------------

Test scripts perform actions in the browser as if they were a user.
SST provides a set of "actions" (functions) for use in your tests.
These actions are defined in the following API:

 * `Actions Reference <http://testutils.org/sst/actions.html>`_


------------------------------------
    Command line options for sst-run
------------------------------------

Usage: sst-run [options] [regexps]

* Calling sst-run with test regular expression(s) as argument(s) will run
  the tests whose test name(s) match the regular expression(s).

* You may optionally create data file(s) for data-driven testing.  Create a
  '^' delimited txt data file with the same name as the test script, plus
  the '.csv' extension.  This will run a test script using each row in the
  data file (1st row of data file is variable name mapping)

Options::

    -h, --help                show this help message and exit
    -d DIR_NAME               directory of test case files
    -r REPORT_FORMAT          report type: xml
    -b BROWSER_TYPE           select webdriver (Firefox, Chrome, PhantomJS, etc)
    -m SHARED_DIRECTORY       directory for shared modules
    -q                        output less debugging info during test run
    -V                        print version info and exit
    -s                        save screenshots on failures
    --failfast                stop test execution after first failure
    --debug                   drop into debugger on test fail or error
    --with-flags=WITH_FLAGS   comma separated list of flags to run tests with
    --disable-flag-skips      run all tests, disable skipping tests due to flags
    --extended-tracebacks     add extra information (page source) to failure reports
    --collect-only            collect/print cases without running tests
    -e EXCLUDE                all tests matching the EXCLUDE regular expresion will not be run
    --exclude=EXCLUDE         all tests matching the EXCLUDE regular expresion will not be run
    -x                        run browser in headless xserver (Xvfb)
    -c CONCURRENCY            concurrency (number of procs)
    --concurrency=CONCURRENCY concurrency (number of procs)


--------------------
    Organizing tests
--------------------

For logical organization of tests, you can use directories in your filesystem.
SST will recursively walk your directory tree and gather all tests for
execution.

For example, a simple test setup might look like::

    /selenium-simple-test
        /mytests
            foo.py

and you would call this from the command line::

    $ sst-run -d mytests

A more complex setup might look like::

    /selenium-simple-test
        /mytests
            /project_foo
                /feature_foo
                    foo.py
            /project_bar
                feature_bar.py
                feature_baz.py
            /shared
                module.py
                utils.py

and you would still call this from the command like::

    $ sst-run -d mytests

SST will find all of the tests in subdirectories (including symlinks) and
execute them. SST won't look in directories starting with an underscore. This
allows you to put Python packages/modules directly in your test directories
if you want. A better option is to use the shared directory.


--------------------------
    Selecting tests to run
--------------------------

While a test suite is meant to fully cover a code base, there are times when
you don't want to run all the tests but only the relevant ones covering the
part you're focusing on.

There are several ways to select the tests to run but first we need to
define a few terms:

All tests have a unique identifier (id) in a given tree:

- for a script this is the python path leading to the file,
  i.e. `dir.subdir.file` for script in the ``dir/subdir/file.py`` file,

- for a regular test this is the python path to access the test method,
  i.e. ``dir.subdir.file.class.method`` for a test method ``method`` in a
  test class ``class`` in a ``dir/subdir/file.py`` file.

``sst-run`` accepts patterns as arguments and will select only the tests
that matches at least one of the patterns. It also accepts ``--exclude pattern``
arguments, the selected tests will match none of the ``--exclude`` patterns.

In both cases, these patterns are python regular expressions.

The following commands will therefore run various selections of tests:

* A single test::

    sst-run ^dir.subdir.file.class.method

  for regular tests or::

    sst-run ^dir.subdir.file

  for a script

* All tests in a class::

    sst-run ^dir.subdir.file.class

* All tests in a file::

    sst-run ^dir.subdir.file

  note that if the file is a script a single test is run

* All tests in a subdirectory::

    sst-run ^dir.subdir

* All tests in a directory (i.e. a subtree)::

    sst-run ^dir

* All tests in a subtree except for a specific subdirectory::

    sst-run ^dir --exclude ^dir.subdir

* The whole test suite::

    sst-run 

  when invoked at the root of the test tree.


Note that '^' is used in the examples above to ensure that the test ids
*starts* with the given regular expression, in most cases you'll need to
specify the caret if only if the regexp can match other test ids in your
test suite. So, for example, with a test suite containing tests with ids
`a.b.foo`, `foo.x` and `foo.y`, `sst-run foo` will select all tests whereas
`sst-run ^foo` will only select `foo.x` and `foo.y`.

Combining test patterns and ``--exclude`` patterns should allow any subset
of the test suite to be selected. This is a powerful way to reduce the time
needed to run only the tests you care about at a given time, running the
whole test suite should still be used when you want to ensure no regressions
have been introduced.


-------------------------------------
    Using sst in unittest test suites
-------------------------------------

sst uses unittest test cases internally to wrap the execution of the script
and taking care of starting and stopping the browser. If you prefer to
integrate some sst tests into an existing unittest test suite you can use
SSTTestCase from cases.py::

  from sst.actions import *
  from sst import cases

  class TestUbuntu(cases.SSTTestCase):

      def test_ubuntu_home_page(self):
          go_to('http://www.ubuntu.com/')
          assert_title_contains('Ubuntu')

So, with the above in a file name test_ubuntu.py you can run the test with
(for example)::

  python -m unittest test_ubuntu.py

`sst-run` provides an headless xserver via the `-x` option. `SSTTestCase`
provides the same feature (sharing the same implementation) via two class
attributes.

`xserver_headless` when set to `True` will start an headless server for each
test (and stop it after the test). If you want to share the same server
across several tests, set `xvfb`. You're then responsible for starting and
stopping this server (see `src/sst/xvfbdisplay.py` for details or
`src/sst/tests/test_xvfb.py` for examples.


--------------------
    Shared directory
--------------------

SST allows you to have a directory called `shared` in the top level directory
of your tests, which is added to `sys.path`. Here you can keep helper modules
used by all your tests. `sst-run` will not run Python files in the `shared`
directory as tests.

By default SST looks in the test directory you specify to find `shared`,
alternatively you can specify a different directory using the `-m` command
line argument to `sst-run`.

If there is no `shared` directory in the test directory, then `sst-run` will
walk up from the test directory to the current directory looking for one. This
allows you to run tests just from a subdirectory without having to explicitly
specify where the shared directory is.


---------------------
    sst.config module
---------------------

Inside tests you can import the `sst.config` module to know various things
about the current test environment. The `sst.config` module has the following
information::

    from sst import config

    # which browser is being used?
    config.browser_type

    # full path to the shared directory
    config.shared_directory

    # full path to the results directory
    config.results_directory

    # flags for the current test run
    config.flags

    # A per test cache. A dictionary that is cleared at the start of each test.
    config.cache


--------------------------------
    Development on Ubuntu/Debian
--------------------------------

* SST is primarily being developed on Linux, specifically Ubuntu. It should
  work fine on other platforms, but any issues (or even better - patches)
  should be reported on the Launchpad project.

* Get a copy of SST Trunk, create and activate a virtualenv, install
  requirements, and run examples/self-tests from the dev branch::

    $ sudo apt-get install bzr python-virtualenv xvfb
    $ bzr branch lp:selenium-simple-test
    $ cd selenium-simple-test
    $ ./ci.sh --bootstrap
    $ source ENV/bin/activate
    (ENV)$ ./sst-run -d examples
    
* (optional) Install test dependencies and run SST's internal unit tests::

    (ENV)$ pip install mock nose pep8
    (ENV)$ ./ci.sh --unit

* (optional) Run SST's internal test application with acceptance tests::

    (ENV)$ ./ci.sh --acceptance

* `Launchpad Project <https://launchpad.net/selenium-simple-test>`_

* `Browse the Source (Trunk)
  <http://bazaar.launchpad.net/~canonical-isd-qa/selenium-simple-test/trunk/files>`_

* To manually setup dependencies, SST uses the following non-stdlib packages:

    * selenium
    * testtools
    * django (optional - needed for internal self-tests only)


------------------------
    Running the examples
------------------------

SST source code repository and package download contain some trivial example
scripts.

You can run them from your local sst directory like this::

    $ ./sst-run -d examples


--------------------------
    Running the self-tests
--------------------------

SST source code repository and package download contain a set of self-tests
based on an included test Django project.

You can run the suite of self-tests (and the test Django server) from your
local branch like this::

    $ ./ci.sh --bootstrap
    $ ./ci.sh --acceptance


-----------------
    Related links
-----------------

* `Selenium Project Home <http://selenium.googlecode.com>`_
* `Selenium WebDriver (from 'Architecture of Open Source Applications')
  <http://www.aosabook.org/en/selenium.html>`_
* `Python Unittest <http://docs.python.org/library/unittest.html>`_
