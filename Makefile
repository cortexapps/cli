#
# Environment Variables
#
UNAME_S := $(shell uname -s)

ifeq ($(CORTEX_CLI),) ## Cortex CLI, defaults to CLI in the repository
export CORTEX_CLI := python3 ./cortexapps_cli/cortex.py -q
endif

ifeq ($(CORTEX_GH_ALIAS),) ## Github alias defined in Cortex GitHub integration, defaults to public-api-test
export CORTEX_GH_ALIAS := public-api-test
endif

# Change this once we can get WEBHOOK_URL via Cortex API
ifeq ($(CORTEX_GH_WEBHOOK_URL),) ## The GitHub webhook URL defined in Cortex
export CORTEX_GH_WEBHOOK_URL=https://api.getcortexapp.com/api/v1/github/manual-webhook/e0b77380-e7af-4e14-8563-8168651e307e/$(CORTEX_GH_ALIAS)
endif

# Should only need to change this if using enterprise GitHub.
ifeq ($(GH_URL),) ## GitHub URL, will be used to call the GitHub API to create a webhook
export GH_URL=https://api.github.com
endif

ifeq ($(GH_ORG),) ## GitHub organization used for GitHub tests
export GH_ORG=cortextests
endif

ifeq ($(GH_REPO),) ## GitHub repository used for GitHub tests
export GH_REPO=public-api-test-repo
endif

ifeq ($(CORTEX_API_KEY),) ## Required; Cortex API key with Admin permission
   $(error CORTEX_API_KEY is not set)
endif

ifeq ($(CORTEX_BASE_URL),) ## Required; Cortex base URL for API, ie for cloud this would be https://api.getcortexapp.com
   $(error CORTEX_BASE_URL is not set)
endif
ifeq ($(CORTEX_BASE_URL),http://api.local.getcortexapp.com:8080)
export CORTEX_GH_WEBHOOK_URL=$(shell ./scripts/ngrok.sh)/api/v1/github/manual-webhook/a4037bca-c83e-4058-8550-8393826ff642/$(CORTEX_GH_ALIAS)
   ifeq ($(NGROK_PORT),)
      export NGROK_PORT=8081
   endif
endif

ifeq ($(CORTEX_ENV),) ## Cortex environment, defaults to 'default'; used to distinguish make build targets between environments; if not set inferred from CORTEX_BASE_URL
   ifeq ($(CORTEX_BASE_URL),http://api.local.getcortexapp.com:8080)
      export CORTEX_ENV=local
	else ifeq ($(CORTEX_BASE_URL),https://api.staging.getcortexapp.com)
      export CORTEX_ENV=staging
	else ifeq ($(CORTEX_BASE_URL),https://api.getcortexapp.com)
      export CORTEX_ENV=prod
	else ifeq ($(CORTEX_BASE_URL),http://api.helm.getcortexapp.com)
      export CORTEX_ENV=helm
	else ifeq ($(CORTEX_ENV),)
      export CORTEX_ENV=default
   endif
endif

ifneq ($(CORTEX_TENANT),) ## Used with CORTEX_ENV, if set can help distinguish between different tenants in the same environment
   export BUILD_SUBDIR=$(CORTEX_ENV)-$(CORTEX_TENANT)
else
   export BUILD_SUBDIR=$(CORTEX_ENV)
endif

#
# Configuration variables
#
BUILD_DIR = build/$(BUILD_SUBDIR)
export FEATURE_FLAG_EXPORT=$(BUILD_DIR)/ff/feature-flags.json
DATA_DIR = data
ENTITIES := $(shell find $(DATA_DIR) -type f)

ARCHIVE_ENTITIES = robot-item-sorter inventory-scraper
ARCHIVE_TARGETS := $(ARCHIVE_ENTITIES:%=$(BUILD_DIR)/%.archive)

CATALOG_ENTITIES := $(wildcard data/catalog/*.yaml)
CATALOG_TARGETS := $(CATALOG_ENTITIES:data/catalog/%.yaml=$(BUILD_DIR)/%.yaml)

CUSTOM_RESOURCES := $(wildcard data/resource-definitions/*.json)
CUSTOM_RESOURCE_TARGETS := $(CUSTOM_RESOURCES:data/resource-definitions/%.json=$(BUILD_DIR)/%.json)

FEATURE_FLAG_VARS := $(shell env | grep CORTEX_FF | cut -d= -f1)
FEATURE_FLAGS = $(patsubst CORTEX_FF_%,%,$(FEATURE_FLAG_VARS))
FEATURE_FLAG_ENVSUBST := $(FEATURE_FLAGS:%=$(BUILD_DIR)/ff/envsubst/%)

PYTHON_VENV = ~/.venv/cortex-cli-test

all: info setup feature-flags-dump load-data github test-api ## Setup environment, load data and test

.PHONY: info
info:
	@echo "Running test for: $(BUILD_SUBDIR)"

.PHONY: setup
setup: tools venv ## Setup python virtual environment for testing

#
# 
# Tools setup
#
#
.PHONY: tools
tools: brew jq python3

.PHONY: brew
brew:
ifeq ($(UNAME_S),Darwin)
	@which brew > /dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
endif

.PHONY: jq
jq:
ifeq ($(UNAME_S),Darwin)
	@which jq > /dev/null || brew install jq
else
	@which jq > /dev/null || (echo "jq is not installed"; exit)
endif

.PHONY: python3
python3:
ifeq ($(UNAME_S),Darwin)
	@which python3 > /dev/null || brew install python3
else
	@which python3 > /dev/null || (echo "python3 is not installed"; exit 1)
endif

.PHONY: venv
venv: $(PYTHON_VENV)

$(PYTHON_VENV): requirements.txt
	python3 -m venv $@
	. $@/bin/activate; python3 -m pip install --upgrade -r $^
	touch $@

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | cut -d':' -f1- | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: vars
vars: ## Display variables used for testing
	@grep -E 'ifeq.*## .*$$' $(MAKEFILE_LIST) | grep -v grep | sort | sed 's/ifeq.*(//' | sed 's/).*)//' | awk 'BEGIN {FS = "## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: load-data
load-data: catalog-entities archive-entities resource-definitions ## Load data from 'data' directory into Cortex

.PHONY: archive-entities
archive-entities: $(ARCHIVE_TARGETS) | $(BUILD_DIR)

.PHONY: catalog-entities
catalog-entities: $(CATALOG_TARGETS) | $(BUILD_DIR)

$(BUILD_DIR)/%.archive: python3
	@$(CORTEX_CLI) catalog archive -t $(notdir $(basename $@))
	@touch $@

$(BUILD_DIR)/%.yaml: data/catalog/%.yaml $(CUSTOM_RESOURCE_TARGETS)
	$(CORTEX_CLI) catalog create -f $<
	@touch $@

.PHONY: resource-definitions
resource-definitions: $(CUSTOM_RESOURCE_TARGETS) | $(BUILD_DIR)

$(BUILD_DIR)/%.json: data/resource-definitions/%.json python3 | $(BUILD_DIR)
	$(CORTEX_CLI) catalog delete-by-type -t $(notdir $(basename $@))
	($(CORTEX_CLI) resource-definitions get -t $(notdir $(basename $@)) && $(CORTEX_CLI) resource-definitions delete -t $(notdir $(basename $@)) )  || :
	$(CORTEX_CLI) resource-definitions create -f $<
	@touch $@

#
# This target performs token replacement of files in the feature-flags directory and checks
# if the contents of the file have changed since the last time it was built.  If so, the 
# feature flag is updated in the environment.
# 
# This check is beneficial only in local test environments.  As of now, no intent to save
# state between runs of an automated build, so all flags would need to be set each test
# cycle.
#
# If these flags can be set all at once and time isn't a concern, this target can most
# likely be removed.
#
.PHONY: feature-flags
feature-flags: feature-flags-dump $(FEATURE_FLAG_ENVSUBST)

$(BUILD_DIR)/ff/envsubst/%: | $(BUILD_DIR)/ff/envsubst $(BUILD_DIR)/ff/source
	@echo "Checking if feature flag $* needs to be updated"
	@envsubst < feature-flags/$*.json > $@
	@diff $@ $(BUILD_DIR)/ff/source/$* 2> /dev/null || (. $(PYTHON_VENV)/bin/activate; python tests/feature_flag_set.py $*)
	@cp $@ $(BUILD_DIR)/ff/source
	@rm $@

test: test-api test-cli ## Run pytest for both API and CLI tests in the 'tests' directory

test-api: feature-flags ## Run pytest for API tests in the 'tests' directory
	@if [ -f .coverage ]; then rm .coverage; fi
ifeq ($(CORTEX_API_KEY_VIEWER),) ## Required; Cortex API key with Viewer permission, used in RBAC tests
   $(error CORTEX_API_KEY_VIEWER is not set)
endif

ifeq ($(GH_PAT),) ## GitHub Personal Access Token
   $(error GH_PAT is not set)
endif
 
ifeq ($(GH_WEBHOOK_SECRET),) ## GitHub webhook secret; defined in the Cortex GitHub configuration and used to create GitHub webhook
    $(error GH_WEBHOOK_SECRET is not set)
endif

	@. $(PYTHON_VENV)/bin/activate; PYTHONPATH=cortexapps_cli:tests pytest -rA -n auto -m "not serial" --html=report.html --self-contained-html --cov=cortexapps_cli --cov-append --cov-report term-missing $(PYTEST_PARMS)

test-cli: feature-flags test-api ## Run pytest for CLI-specific tests in the 'tests' directory
	@. $(PYTHON_VENV)/bin/activate; PYTHONPATH=cortexapps_cli:tests pytest -rA -n 0 -m " serial" --cov=cortexapps_cli --cov-append --cov-report term-missing $(PYTEST_PARMS)

.PHONY: clean
clean: clean-data
	@rm -rf $(BUILD_DIR)

clean-data: jq ${ENTITIES}
	for entity in $(shell $(CORTEX_CLI) catalog list -g public-api-test | jq -r '.entities[].tag'); do \
		$(CORTEX_CLI) catalog delete -t $$entity; echo "Deleted: $$entity";\
	done

.PHONY: feature-flags-dump
feature-flags-dump: $(FEATURE_FLAG_EXPORT)  ## Dump current feature flags to $(FEATURE_FLAG_EXPORT)

.PHONY: feature-flags-clean
feature-flags-clean:
	@rm -f $(FEATURE_FLAG_EXPORT)

$(FEATURE_FLAG_EXPORT): | $(BUILD_DIR)/ff
	. $(PYTHON_VENV)/bin/activate; python tests/feature_flag_dump.py $@

.PHONY: github
github: $(BUILD_DIR)/github ## Configure Cortex GitHub integration, create GitHub webhook

$(BUILD_DIR)/github: | $(BUILD_DIR)
	. $(PYTHON_VENV)/bin/activate; python tests/github_setup.py
	touch $@

$(BUILD_DIR):
	@mkdir -p $@

$(BUILD_DIR)/ff:
	@mkdir -p $@

$(BUILD_DIR)/ff/source:
	@mkdir -p $@

$(BUILD_DIR)/ff/envsubst:
	@mkdir -p $@
