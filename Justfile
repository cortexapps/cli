cortex_cli := 'poetry run cortex'
pytest := 'PYTHONPATH=. poetry run pytest -rA'

export CORTEX_API_KEY := env('CORTEX_API_KEY')
export CORTEX_BASE_URL := env('CORTEX_BASE_URL', "https://api.getcortexapp.com")
export CORTEX_API_KEY_VIEWER := env('CORTEX_API_KEY_VIEWER')
export GITHUB_TEST_ORG := env('GITHUB_TEST_ORG', "")
export GITHUB_TEST_PAT := env('GITHUB_TEST_PAT', "")
export GITHUB_TEST_USERNAME := env('GITHUB_TEST_USERNAME', "")
export GITHUB_INTEGRATION_ALIAS := env('GITHUB_INTEGRATION_ALIAS', "")
export GITLAB_TOKEN := env('GITLAB_TOKEN', "")
export GITLAB_INTEGRATION_ALIAS := env('GITLAB_INTEGRATION_ALIAS', "")

help:
   @just -l

_setup:
   @if [ -f .coverage ]; then rm .coverage; fi

# Run all tests
test-all: _setup test-import
   {{pytest}} -n auto -m "not setup and not perf and not functional" --html=report.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing tests

# Run all tests serially - helpful to see if any tests seem to be hanging
_test-all-individual:  test-import
   {{pytest}} -m "not setup and not perf and not functional" --html=report-all-invidual.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing tests

# Run import test, a pre-requisite for any tests that rely on test data.
test-import:
   {{pytest}} tests/test_import.py --cov=cortexapps_cli --cov-report=

# Run a single test, ie: just test tests/test_catalog.py
test testname:
   {{pytest}} -n auto -m "" {{testname}}

# Import functional test data (workflows)
test-functional-import:
   {{pytest}} tests/functional/test_functional_import.py --cov=cortexapps_cli --cov-report=

# Run functional tests, ie: just test-functional tests/functional/test_gh_branches.py
test-functional *args:
   {{pytest}} -v -s -n auto -m functional --html=report-functional.html --self-contained-html {{args}}

# Clean up orphaned functional test resources from interrupted runs
test-functional-sweep:
   {{pytest}} -v -s tests/functional/test_gh_sweep.py

# Run performance tests (rate limiting, long-running tests)
test-perf:
   @echo "Running performance tests (this may take 60+ seconds)..."
   {{pytest}} -v -s -m perf tests/
