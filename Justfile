cortex_cli := 'poetry run cortex'

export CORTEX_API_KEY := env('CORTEX_API_KEY')
export CORTEX_BASE_URL := env('CORTEX_BASE_URL', "https://api.getcortexapp.com")
export CORTEX_API_KEY_VIEWER := env('CORTEX_API_KEY_VIEWER')

help:
   @just -l

# Run all tests
test-all: test-parallel test-serial

# Run tests that can run in parallel
test-parallel: 
   PYTHONPATH=. poetry run pytest -rA -n auto -m "not serial" --html=report.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing tests

# Run all tests serially - helpful to see if any tests seem to be hanging
_test-all-serial: 
   PYTHONPATH=. poetry run pytest -rA -m "not serial" --html=report.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing tests

# Run tests that have to run sequentially
test-serial:
   @if [ -f .coverage ]; then rm .coverage; fi
   PYTHONPATH=. poetry run pytest -rA -n auto -m "serial" --html=report.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing tests

# Run a single test, ie: just test tests/test_catalog.py
test testname:
   poetry run pytest {{testname}}

_load-data:
   #!/bin/bash
   if [[ -f .load-data-done ]]
   then 
      echo "Not loading test data since .load-data-done file exists."
      exit
   fi

   # Delete existing entity definitions and any entities to prevent getting a conflict error.
   # TODO: modify cli import to add a flag to manage this
   for entity_type_file in `ls -1 data/entity-types/*`; do
      entity_type=$(basename ${entity_type_file} .json)
      echo "Deleting entity type: ${entity_type}"
      # Delete all instances of this type
      {{cortex_cli}} catalog delete-by-type -t ${entity_type} 
      # Now delete the type if it exists
      ({{cortex_cli}} entity-types get -t ${entity_type} && {{cortex_cli}} entity-types delete -t ${entity_type}) || :
   done

   {{cortex_cli}} backup import -d data

   # Archive a couple of entities in order to test commands that include or exclude archived entities
   {{cortex_cli}} catalog archive -t robot-item-sorter
   {{cortex_cli}} catalog archive -t inventory-scraper

   touch .load-data-done
