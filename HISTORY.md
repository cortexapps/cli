Release History
===============

0.8.0 (2023-11-19)
------------------

**Improvements**
- Add coralogx, launchdarkly integrations.

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

