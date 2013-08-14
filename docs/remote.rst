================
    SST - Remote
================

----------------------------------
    Using a remote Selenium server
----------------------------------

SST also supports running tests through a Selenium [RC] server, which amongst
other things allows for running your tests in the cloud through SauceLabs'
'OnDemand' service. A special command-line script (sst-remote) is provided for
this.

To give it a try, register for a free account at http://saucelabs.com and get
your API key, then just like above, run the example tests by simply providing
the url for SauceLabs' server on the command line, replacing your username and
password on the url below::

    $ ./sst-remote -d examples -u http://<your-user>:<your-api-key>@ondemand.saucelabs.com:80/wd/hub

If you want to use a local Selenium RC server instead, get the
'selenium-server-standalone-<version>.jar' file from
'http://code.google.com/p/selenium/downloads/list' and fire up a server with::

    $ java -jar selenium-server-standalone-<version>.jar

Then in another terminal run 'sst-remote' with::

    $ ./sst-remote -d examples -u http://127.0.0.1:4444/wd/hub

---------------------------------------
    Command line options for sst-remote
---------------------------------------

sst-remote <options> [testname]

* Calling sst-remote without any arguments runs all tests in the local 'tests' directory.

* Calling sst-remote with testname(s) as arguments will just run
  those tests. The testnames should not include the '.py' at
  the end of the filename.

* You may optionally create a data file for data-driven
  testing.  Create a '^' delimited txt data file with the same
  name as the test, plus the '.csv' extension.  This will
  run a test using each row in the data file (1st row of data
  file is variable name mapping)


Options:
  -h, --help            show this help message and exit
  -d DIR_NAME           directory of test case files
  -r REPORT_FORMAT      results report format (html, xml, console)
  -b BROWSER_TYPE       select webdriver (Firefox, Chrome, InternetExplorer,
                        etc)
  -m SHARED_MODULES     directory for shared modules
  -q                    output less debugging info during test run
  -s                    save screenshots on failures
  --failfast            stop test execution after first failure
  --debug               drop into debugger on test fail or error
  -p BROWSER_PLATFORM   desired platform (XP, VISTA, LINUX, etc), when using a
                        remote Selenium RC
  -v BROWSER_VERSION    desired browser version, when using a remote Selenium
  -n SESSION_NAME       identifier for this test run session, when using a
                        remote Selenium RC
  -u WEBDRIVER_REMOTE_URL
                        url to WebDriver endpoint (eg:
                        http://host:port/wd/hub), when using a remote Selenium RC


