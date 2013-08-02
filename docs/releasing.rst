============================
    SST Release Instructions
============================

---------------------------------------------------------------
    Instructions for releasing SST to PyPI from Launchpad Trunk
---------------------------------------------------------------

* get a branch of SST trunk:

    $ bzr branch lp:selenium-simple-test
    $ cd selenium-simple-test

* edit version number for release:

    change in: `src/sst/__init__.py`

* update changelog:

    edit: `docs/changelog.rst`

    change release date

* commit and tag the revision

  bzr commit -m 'Release 0.2.3'
  bzr tag sst-0.2.3

* update documentation and README (if necessary)

* push updates back to Launchpad (or create/land an MP):

    $ bzr push lp:selenium-simple-test

* generate HTML documentation:

    * install sphinx (`$ sudo apt-get install python-sphinx`)

    * generate `actions.rst` doc:

        under /docs, run:

        $ python make_actions_rst.py

    * go up to the main SST directory and run:

        $ sphinx-build -b html docs sst_docs

    * this will produce HTML documentation in the `sst_docs` directory. Open
      `index.html` with your browser to check the result.

* publish documentation on VPS:

    * grab `/sst_docs` that was just generated.

    * ssh to testutils.org vps:

    * go to `/var/www/sst/` and remove everything under this dir

    * sftp upload sst-docs contents insto sst/ directory.

    * chmod the dir and content to 0755

* get a clean branch of SST:

    $ rm -rf selenium-simple-test

    $ bzr branch lp:selenium-simple-test

* release to PyPI.  

    from main directory, run:

    $ python setup.py sdist

    (creates the source distribution tarball under dist/)

   

    $ python setup.py sdist register

    (registers the release with PyPI server)

   

    $ python setup.py sdist upload

    (uploads distribution to PyPI server)

* verify new docs are showing on website: http://testutils.org/sst/changelog.html

* verify new version is showing on PyPI website: http://pypi.python.org/pypi/sst

* mark all bugs as 'FixReleased' with launchpadlib:

  From an up-to-date lp:launchpadlib branch.

  $ launchpadlib/contrib/close-my-bugs.py selenium-simple-test 0.2.4

  replacing '0.2.4' with the appropriate milestone.

* release done!


Open trunk for development after a release
------------------------------------------

* edit version number for release:

    change in: `src/sst/__init__.py` by bumping the release number and
    appending 'dev'


* update changelog:

    edit: `docs/changelog.rst`

    create a new section replacing the date with question marks



