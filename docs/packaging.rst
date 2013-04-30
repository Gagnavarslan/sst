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

  $ bzr merge-upstream ../../trunk --version 0.2.4dev~bzr382
  $ debchange -i # s/UNRELEASED/raring/
  $ debcommit
  $ bzr bd -S # Alternatively, 'debuild -S' can also be used


* Upload the new version to a ppa

  # Replace 'vila/selenium' with your targeted ppa below
  dput ppa:vila/selenium ../sst_0.2.4dev~bzr382-1ubuntu4_source.changes
  bzr mark-uploaded
