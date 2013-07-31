SST Packaging Recipes

Bootstrapping
-------------

The following steps describe how a packaging branch can be first created for
an unreleased development version. Packaging released versions can be built
on top of that and is then simpler.

* setup an incomplete first packaging branch

  # Install pre-requisites
  $ sudo apt-get install python-stdeb

  # Start with the 0.2.3 release
  $ mkdir packaging
  $ cd packaging
  $ bzr branch lp:selenium-simple-test -r379 raring
  $ cd raring
  $ bzr tag upstream-0.2.3
  $ python setup.py sdist
  # Generate a debian dir with python-stdeb
  py2dsc dist/sst-0.2.3.tar.gz
  mv deb_dist/sst-0.2.3/debian .
  bzr add debian
  bzr commit -m 'source package automatically created by stdeb'

* merge upstream from branch

The tip of trunk is then merged into the packaging branch allowing the
creation of the package.

  $ bzr merge-upstream ../../trunk --version 0.2.4~bzr382
  $ debchange -i # s/UNRELEASED/raring/
  $ debcommit
  $ bzr bd -S # Alternatively, 'debuild -S' can also be used

* merge upstream from branch for a release

  $ bzr merge-upstream --version 0.2.4 ../../trunk -rtag:sst-0.2.4
  $ debchange -i # s/UNRELEASED/saucy/
  $ debcommit
  $ bzr bd -S

* upload the new version to a ppa

  # Replace 'vila/selenium' with your targeted ppa below
  dput ppa:vila/selenium ../sst_0.2.4~bzr382-1ubuntu4_source.changes
  bzr mark-uploaded


Packaging selenium itself
-------------------------

While selenium has been packaged up to 2.25, following upstream releases
were not. The following steps describe how 2.32 has been packaged in a ppa.

* merge upstream releases into the packaging branch

  $ bzr branch lp:ubuntu/python-selenium raring
  $ cd raring
  $ bzr merge-upstream
  $ debchange -i # s/UNRELEASED/raring/ and document the new upstream release
  $ debcommit
  $ bzr bd -S

* upload the new version to a ppa

  # Replace 'vila/selenium' with your targeted ppa below
  dput ppa:vila/selenium ../python-selenium_2.32.0-0ubuntu3_source.changes
  bzr mark-uploaded
