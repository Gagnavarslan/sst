#!/bin/bash

set -e


# Continuous Integration script for SST
#
#  Options:
#    --bootstrap, --flake8, --unit, --acceptance BROWSER
#
#  Example:
#    bootstrap environment, run static checks, run unit tests, run
#    acceptance tests with default browser:
#
#    $ ./ci.sh --bootstrap --flake8 --unit --acceptance
#
#    * BROWSER options are Firefox/Chrome/PhantomJS/etc.  Default is "Firefox".
#
#  Instructions:
#   1. ensure you have Xvfb, Firefox or other supported browser installed
#   2. $ bzr branch lp:selenium-simple-test
#   3. cd selenium-simple-test
#   4. run this script
#


# command line options
while [ $# -gt 0 ]; do  # until you run out of parameters
    case "$1" in
        --bootstrap)
            BOOTSTRAP=1
            ;;
        --flake8)
            FLAKE8=1
            ;;
        --acceptance)
            BROWSER="$2"
            if [[ "$BROWSER" == "Firefox" || "$BROWSER" == "Chrome" || "$BROWSER" == "PhantomJS" ]]; then
                shift
            elif [ -z "$BROWSER" ]; then
                BROWSER="Firefox"
            else
                echo "browser format $1 not recognized."
                echo "(try: $0 --acceptance Firefox, or: $0 --acceptance Chrome)"
                exit
            fi
            ;;
    esac
    shift  # check next set of parameters
done

if [ -n "$BOOTSTRAP" ]; then
    echo "cleaning up..."
    rm -rf ENV results *.log *.xml
    echo "getting dependencies..."
    if [ -d sst-deps ]; then
        cd sst-deps
        bzr pull
        cd ..
    else
        bzr branch lp:~ubuntuone-hackers/selenium-simple-test/sst-deps
    fi
    echo "creating virtualenv..."
    virtualenv ENV --quiet
    echo "activating virtualenv..."
    source ENV/bin/activate
    echo "installing modules from dependencies branch..."
    DEPS="sst-deps/pythonpackages/"
    cd $DEPS; ls *.tar.gz
    python "$(which pip)" install *.tar.gz --no-deps
    cd ../..
else
    source ENV/bin/activate
fi

echo "setting path..."
PWD=`pwd`
DEPS_DIR="$PWD/sst-deps/bin"  # webdrivers are in bin directory of branch we pulled in bootstrap
PATH=$DEPS_DIR:$PATH  # so bindings find chromedriver and phantomjs
echo "  added: '$DEPS_DIR' to PATH"

echo "----------------------------------"
echo "environment info:"
python -V
python -c "import django; print 'Django %s' % django.get_version()"
python -c "import selenium; print 'Selenium %s' % selenium.__version__"
./sst-run -V

if [ -n "$FLAKE8" ]; then
    echo "----------------------------------"
    echo "running flake8 (pyflakes/pep8) checks..."
    python "$(which flake8)" src/ docs/ sst-* *.py || false
fi

if [ -n "$BROWSER" ]; then
    if [ "$BROWSER" == "Firefox" ]; then
        echo "----------------------------------"
        firefox -v
    fi
    echo "----------------------------------"
    echo "running unit and acceptance tests..."
    ./sst-test -x -s -r xml -b $BROWSER --extended-tracebacks
fi
echo "----------------------------------"

echo "$0 done."
