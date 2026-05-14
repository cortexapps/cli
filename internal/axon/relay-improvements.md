# Axon Relay: Improvement Suggestions

## 1. Validate required environment variables at startup

**Problem**: When required env vars are missing or misconfigured, the relay starts successfully and connects to Cortex, but requests fail with cryptic HTTP errors (403, 401, 555). The user has no indication that their configuration is wrong until they try to use the integration and dig through relay logs.

**Example**: Running `-i jira` without `JIRA_USERNAME` produces no warning. The relay connects, Cortex shows the relay as online, but every request returns 403 because the Basic auth header is malformed.

**Suggestion**: Validate required env vars per integration at startup and fail fast with a clear message:

```
Error: Integration "jira" requires JIRA_USERNAME and JIRA_TOKEN.
  JIRA_API:      https://jeff-schnitter-proton.atlassian.net (set)
  JIRA_USERNAME: (not set)  <-- MISSING
  JIRA_TOKEN:    (set)

See: https://docs.cortex.io/axon-relay/configuration
```

Required vars by integration (from README.relay.md):

| Integration | Required vars |
|-------------|---------------|
| Jira        | `JIRA_API`, `JIRA_USERNAME`, `JIRA_TOKEN` |
| Jira Bearer | `JIRA_API`, `JIRA_TOKEN` |
| GitHub      | `GITHUB_TOKEN` |
| GitLab      | `GITLAB_TOKEN` |
| Bitbucket   | `BITBUCKET_API`, `BITBUCKET_USERNAME`, `BITBUCKET_PASSWORD` |
| SonarQube   | `SONAR_TOKEN` |
| Prometheus  | `PROMETHEUS_API` |

## 2. `auth` block in custom accept.json silently fails

**Problem**: The `auth` block in custom accept files (`-f`) does not work. The Snyk Broker layer injects a literal `authorization: ${AUTHORIZATION}` header that is never resolved, overriding whatever the auth block was supposed to set. The origin server receives the literal string and rejects it.

**Details**: See `jenkins/jenkins-bug.md` for full analysis with relay log evidence.

**Workaround**: Use the `headers` block instead of `auth`:

```json
{
  "private": [{
    "method": "any",
    "path": "/**",
    "origin": "http://my-server:8080",
    "headers": {
      "Authorization": "Basic ${MY_AUTH_TOKEN}"
    }
  }]
}
```

**Suggestion**: Either fix the `auth` block or log a warning when one is present in a custom accept file:

```
Warning: "auth" block in accept.json is not supported for custom relays.
Use "headers" block instead. See: https://docs.cortex.io/axon-relay/custom-relays
```

## 3. Preflight health check always fails for authenticated endpoints

**Problem**: The broker's preflight `rest-api-status` check always shows `error` because it hits the origin without authentication. This is expected behavior (the health check doesn't have credentials), but the error in startup logs is misleading — it looks like the relay is broken when it's actually fine.

**Suggestion**: Either skip the health check for integrations that require auth, or log it as a warning rather than an error:

```
Note: REST API health check skipped (integration requires authentication).
      The relay will authenticate requests at runtime.
```

## 4. `-s bearer` mode hits the same `${AUTHORIZATION}` bug

**Problem**: Using `-i jira -s bearer` triggers the same broken Snyk Broker auth code path as the `auth` block in custom accept files. The relay sends `authorization: ${AUTHORIZATION}` (literal) instead of `Authorization: Bearer <token>`.

**Workaround**: For Jira Cloud, use the non-bearer mode with `JIRA_USERNAME` + `JIRA_TOKEN` instead of `-s bearer`. Jira Cloud accepts Basic auth (`email:api-token`), so this works.

**Note**: This means `-s bearer` may be fundamentally broken for all integrations, not just Jira. Any integration that relies on the bearer subtype could hit this issue.
