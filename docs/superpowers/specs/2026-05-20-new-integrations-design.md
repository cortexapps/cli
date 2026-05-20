# Add 32 New Integration Commands

**Date**: 2026-05-20
**Version target**: 1.17.0 (minor bump via `feat:` prefix)

## Summary

Add CLI support for 32 integrations that have API endpoints but no CLI commands yet. Each integration gets its own command file following the existing patterns in `integrations_commands/`.

## Two Patterns

### Multi-config (alias-based) — 7 integrations

Commands: `add`, `add-multiple`, `get`, `list`, `get-default`, `update`, `delete`, `delete-all`, `validate`, `validate-all`

Modeled after existing `incidentio.py` / `pagerduty.py` pattern.

| Integration | CLI name | API path | Add fields |
|---|---|---|---|
| Apiiro | `apiiro` | `apiiro` | alias, apiKey, isDefault |
| ArgoCD | `argocd` | `argocd` | alias, host, isDefault, password, username |
| Bitbucket | `bitbucket` | `bitbucket` | alias, isDefault, type + auth fields (4 types) |
| Jenkins | `jenkins` | `jenkins` | alias, apiKey, host, isDefault, username |
| Jira | `jira` | `jira` | alias, isDefault, type + auth fields (3 types) |
| Rootly | `rootly` | `rootly` | alias, apiKey, isDefault |
| Semgrep | `semgrep` | `semgrep` | alias, apiKey, isDefault, organizationId, organizationSlug |

### Single-config — 25 integrations

Commands: `add`, `get`, `update`, `validate`, `delete`

No alias support. Simpler CRUD pattern.

| Integration | CLI name | API path | Add fields |
|---|---|---|---|
| Azure AD (Entra ID) | `azure-active-directory` | `active-directory` | clientId, clientSecret, tenantId |
| BambooHR | `bamboohr` | `bamboohr` | apiToken, subdomain |
| Bugsnag | `bugsnag` | `bugsnag` | authToken, organizationId |
| Buildkite | `buildkite` | `buildkite` | apiToken, organizationSlug |
| Checkmarx SAST | `checkmarx-sast` | `checkmarx/sast` | username, password |
| ClickUp | `clickup` | `clickup` | personalApiToken |
| Codecov | `codecov` | `codecov` | apiToken |
| Dynatrace | `dynatrace` | `dynatrace` | apiKey, domain |
| Firehydrant | `firehydrant` | `firehydrant` | apiToken |
| Instana | `instana` | `instana` | apiToken, endpoint |
| Mend SAST | `mend-sast` | `mend/sast` | apiKey |
| Mend SCA | `mend-sca` | `mend/sca` | orgKey, userKey, orgType, urlType |
| Okta | `okta` | `okta` | apiToken, domain |
| Opsgenie | `opsgenie` | `opsgenie` | apiToken, isEu, subdomain |
| Rollbar | `rollbar` | `rollbar` | accessToken, organizationSlug |
| Sentry | `sentry` | `sentry` | authToken, organizationSlug, host (optional) |
| ServiceNow | `servicenow` | `servicenow` | instanceName, password, username |
| ServiceNow Cloud Obs | `servicenow-cloud-observability` | `lightstep` | authToken, organizationId, projectId |
| Snyk | `snyk` | `snyk` | authToken, region (enum: USA/US2/EU/AUS) |
| Splunk Obs Cloud | `splunk-observability-cloud` | `signalfx` | accessToken, realm |
| Splunk On Call | `splunk-on-call` | `victorops` | apiId, apiKey, organization |
| Sumo Logic | `sumo-logic` | `sumologic` | accessId, accessKey, deployment |
| Veracode | `veracode` | `veracode` | apiKey, keyId, region |
| Wiz | `wiz` | `wiz` | clientId, clientSecret, dataCenter, identityProvider |
| Workday | `workday` | `workday` | username, password, ownershipReportUrl |
| xMatters | `xmatters` | `xmatters` | organizationSlug, password, username |

## Single-config command details

- **`add`**: POST `/api/v1/{path}/configuration`. Accepts `--file/-f` for JSON input OR individual flags. Raises `BadParameter` if both provided.
- **`get`**: GET `/api/v1/{path}/default-configuration`
- **`update`**: PUT `/api/v1/{path}/configuration`. Same flags as add.
- **`validate`**: POST `/api/v1/{path}/configuration/validate`
- **`delete`**: DELETE `/api/v1/{path}/configurations`

## Multi-config command details

Same as existing multi-config integrations (incidentio, pagerduty, coralogix pattern):
- **`add`**: POST `/api/v1/{path}/configuration` with `--alias/-a`, `--is-default/-i`, integration-specific flags, or `--file/-f`
- **`add-multiple`**: POST `/api/v1/{path}/configurations` from `--file/-f`
- **`get`**: GET `/api/v1/{path}/configuration/{alias}` with `--alias/-a`
- **`list`**: GET `/api/v1/{path}/configurations`
- **`get-default`**: GET `/api/v1/{path}/default-configuration`
- **`update`**: PUT `/api/v1/{path}/configuration/{alias}` with `--alias/-a`, `--is-default/-i`
- **`delete`**: DELETE `/api/v1/{path}/configuration/{alias}` with `--alias/-a`
- **`delete-all`**: DELETE `/api/v1/{path}/configurations`
- **`validate`**: POST `/api/v1/{path}/configuration/validate/{alias}` with `--alias/-a`
- **`validate-all`**: POST `/api/v1/{path}/configuration/validate`

## Special cases

- **Bitbucket**: 4 auth types (cloud-atlassian, cloud-personal, on-prem-basic, workspace-token). Use `--file/-f` for add; CLI flags not practical for polymorphic types.
- **Jira**: 3 auth types (cloud-basic, cloud-scoped, on-prem-basic). Same approach — `--file/-f` for add.
- **Snyk**: Region enum (USA, US2, EU, AUS)
- **Veracode**: Region field (string, not enum — passed through)
- **Opsgenie**: `--is-eu` boolean flag
- **Mend**: Two separate sub-integrations (SAST and SCA) each get their own command file

## File changes

1. **32 new files** in `cortexapps_cli/commands/integrations_commands/`
2. **Update** `cortexapps_cli/commands/integrations.py` — add 32 imports and `add_typer()` calls
3. **32 new test files** in `tests/` following existing `test_integrations_*.py` pattern with `responses` mocking

## Testing

Each integration gets a test file with mocked HTTP responses (using `responses` library). Tests verify CLI invocation reaches the correct API endpoints with correct HTTP methods. No real API calls needed.
