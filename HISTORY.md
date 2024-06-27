Release History
===============

0.26.4 (2024-06-26)
------------------

**Improvements**
- Test modifications for better coverage of Cortex public API.

0.26.3 (2024-05-20)
------------------

**Bugfixes**
- fix JSON payload formatting for docs update subcommand

0.26.2 (2024-05-08)
------------------

**Bugfixes**
- change includeHierarchyFields for catalog API to be string, not boolean

0.26.1 (2024-05-06)
------------------

**Improvements**
- Upgrade GH Actions from Node.js 16 to Node.js 20.

0.26.0 (2024-05-06)
------------------

**Improvements**
- Improve backup export time.

0.25.0 (2024-05-05)
------------------

**Improvements**
- Add catalog pagination parameters

0.24.3 (2024-04-26)
------------------

**Bugfixes**
- Fix ip-allowlist validate

**Improvements**
- Add quiet option to suppress warning messages

0.24.2 (2024-02-28)
------------------
- Don't fail imports on Duplicate

0.24.1 (2024-02-14)
------------------

**Bugfixes**
- Homebrew SHA calculation fix.

0.24.0 (2024-02-13)
------------------

**Bugfixes**
- Clean up default cortex config file

0.22.0 (2024-02-05)
------------------

**Improvements**
- Add Mac homebrew tap

0.21.0 (2024-01-25)
------------------

**Improvements**
- Add showDrafts option to scorecards list

0.20.0 (2024-01-22)
------------------

**Breaking Changes**
- catalog list: change -wo to -io for include owners in preparation for adding -in for include nested fields

**Bugfixes**
- Entity tag should be an optional parameter for scorecards scores.

0.19.0 (2023-12-21)
------------------

**Improvements**
- publish docker image to cortexapp/cli

0.18.0 (2023-12-15)
------------------

**Improvements**
- add gitops-log command
- ensure API errors get displayed on the terminal

0.16.0 (2023-12-06)
------------------

**Improvements**
- add integrations azure-resources

0.15.0 (2023-12-05)
------------------

**Improvements**
- use cortexapps CLI docker image for writing Cortex deploy events
- tag docker image with latest and version tag 

0.14.0 (2023-12-01)
------------------

**Improvements**
- Environment variable support for CORTEX_API_KEY, CORTEX_BASE_URL.

0.13.0 (2023-11-30)
------------------

**Improvements**
- Add incident.io integration

0.12.0 (2023-11-27)
------------------

**Improvements**
- Add deploys update-by-uuid
- Add deploys delete-by-uuid
- Add includeLinks and includeOwners options in catalog list
- Add catalog list-descriptors
- Add catalog gitops-logs
- Add catalog scorecard-scores

0.11.0 (2023-11-27)
------------------

**Improvements**
- Add support for docker image builds.

0.10.0 (2023-11-21)
------------------

**Improvements**
- For exports, add the cortex tenant - the value in the .cortex/config file that identifies the tenant.

0.9.0 (2023-11-21)
------------------

**Improvements**
- Better API key handling -- strip quotes from keys; add better error messages.

0.8.0 (2023-11-19)
------------------

**Improvements**
- Add coralogix, launchdarkly integrations.

0.7.0 (2023-11-17)
------------------

**Improvements**
- Add pagerduty integration.

0.5.0 (2023-11-16)
------------------

**Improvements**
- Dev improvements to run all tests in parallel.

**Bugfixes**
- Delete existing teams and resource definitions when running import.
- Fix for publishing deploy event to Cortex's production Cortex instance.

0.4.0 (2023-11-13)
------------------

**Improvements**
- Add --wait and --timeout for queries run.
- Add option to supply query input as text.

**Bugfixes**
- Change backup of catalog entries to be in yaml format.

0.3.0 (2023-11-07)
------------------

**Bugfixes**
- Fix backup.

0.2.0 (2023-11-07)
------------------

**Bugfixes**
- Command line validation.

**Improvements**
- Test coverage improvements.
- Post publish results to Cortex.

0.0.5-alpha (2023-11-04)
------------------------

**Improvements**
- Version logic now pulls from importlib.metadata.

0.0.4 (2023-10-29)
------------------

**Bugfixes**
- Fix export command to deal with entity types that may not exist.
