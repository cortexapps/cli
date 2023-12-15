ifndef CORTEX_BASE_URL
	export CORTEX_BASE_URL = https://api.getcortexapp.com
endif

test: setup test-all

setup:
	if [ -f .coverage ]; then rm .coverage; fi

test-all: test-not-serial test-serial

test-not-serial:
	poetry run pytest -n auto -m "not serial"

test-serial:
	poetry run pytest -n0 -m "serial"
