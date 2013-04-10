#!/bin/bash

# Continuous Integration script for SST
#
#  Options:
#    --bootstrap, --flake8, --unit, ---acceptance=BROWSER
#
#  Example:
#    bootstrap environment, run static checks, run unit tests, run
#    acceptance tests with default browser:
#
#    $ ./ci.sh --bootstrap --flake8 --unit --acceptance
#
#    * BROWSER options are "Firefox/Chrome/PhantomJS.  Default is "Firefox".
#
#  Instructions:
#   1. ensure you have Xvfb, Firefox or Chrome/Chromium installed
#   2. $ bzr branch lp:selenium-simple-test
#   3. cd selenium-simple-test
#   4. run this this script
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
        --unit)
            UNIT=1
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
    pip install *.tar.gz --no-deps
    cd ../..
else
    source ENV/bin/activate
fi

echo "setting path..."
PATH=sst-deps/bin:$PATH  # so bindings find chromedriver and phantomjs

echo "----------------------------------"
echo "environment info:"
python -V
python -c "import django; print 'Django %s' % django.get_version()"
python -c "import selenium; print 'Selenium %s' % selenium.__version__"
./sst-run -V

if [ -n "$FLAKE8" ]; then
    echo "----------------------------------"
    echo "running flake8 (pyflakes/pep8) checks..."
    flake8 src/ docs/ sst-* *.py > flake8.log
    cat flake8.log | grep -v ': W'  # print errors, but not warnings
fi

if [ -n "$UNIT" ]; then
    echo "----------------------------------"
    echo "running unit tests..."
    # this generates 'nosetests.xml' in top dir
    nosetests --verbosity=2 --with-xunit -m ^test_.* -e ENV -e testproject -e selftests
fi

if [ -n "$BROWSER" ]; then
    if [ "$BROWSER" == "Firefox" ]; then
        echo "----------------------------------"
        firefox -v
    fi
    echo "----------------------------------"
    echo "running acceptance tests..."
    ./sst-run --test -x -s -q -r xml -b $BROWSER --extended-tracebacks
fi
echo "----------------------------------"

echo "$0 done."
