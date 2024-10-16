cortex_cli := 'poetry run cortex2'
cortex_cli_orig := 'poetry run cortex -q'

help:
   @just -l

# Run all tests
test-all:
   poetry run pytest -rA -n auto --cov=cortexapps_cli --cov-append --cov-report term-missing tests

# Run a single test, ie: just test tests/test_catalog.py
test testname:
   poetry run pytest {{testname}}

# Load data from 'data' directory into Cortex
load-data:
   #!/bin/bash
   if [[ -f .load-data-done ]]
   then 
      echo "Not loading test data since .load-data-done file exists"
      exit
   fi

   # Delete existing entity definitions and any entities to prevent getting a conflict error.
   # TODO: modify cli import to add a flag to manage this
   for resource_file in `ls data/resource-definitions`; do
      resource=$(basename ${resource_file} .json)
      {{cortex_cli_orig}} catalog delete-by-type -t ${resource}
      ({{cortex_cli_orig}} resource-definitions get -t ${resource} && {{cortex_cli_orig}} resource-definitions delete -t ${resource}) || :
      {{cortex_cli_orig}} resource-definitions create -f data/resource-definitions/${resource_file}
   done

   {{cortex_cli_orig}} backup import -d data

   # Archive a couple of entities in order to test commands that include or exclude archived entities
   {{cortex_cli_orig}} catalog archive -t robot-item-sorter
   {{cortex_cli_orig}} catalog archive -t inventory-scraper

   @touch .load-data-done
