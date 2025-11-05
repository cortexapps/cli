cortex_cli := 'poetry run cortex'
pytest := 'PYTHONPATH=. poetry run pytest -rA'

export CORTEX_API_KEY := env('CORTEX_API_KEY')
export CORTEX_BASE_URL := env('CORTEX_BASE_URL', "https://api.getcortexapp.com")
export CORTEX_API_KEY_VIEWER := env('CORTEX_API_KEY_VIEWER')

help:
   @just -l

_setup:
   @if [ -f .coverage ]; then rm .coverage; fi

# Run all tests
test-all: _setup test-import
   {{pytest}} -n auto --dist loadfile -m "not setup" --html=report.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing tests

# Run all tests serially - helpful to see if any tests seem to be hanging
_test-all-individual:  test-import
   {{pytest}} --html=report-all-invidual.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing tests

# Run import test, a pre-requisite for any tests that rely on test data.
test-import:
   {{pytest}} tests/test_import.py --cov=cortexapps_cli --cov-report=

# Run a single test, ie: just test tests/test_catalog.py
test testname:
   {{pytest}} -n auto {{testname}}
