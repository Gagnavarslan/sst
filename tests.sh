#!/bin/sh

echo $(pwd)
export PYTHONPATH=$(pwd)/src
# print version and exit
sst-run -V
# run sst unit tests
sst-test -r xml -s -x --extended-tracebacks -e ^sst.tests.test_django_devserver -e ^sst.tests.test_code_format -e ^sst.tests.test_sst_script_test_case -e ^sst.selftests -e ^sst.tests.test_results
