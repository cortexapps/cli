# Axon Relay: `auth` block in accept.json doesn't work for custom relays

## Summary

When configuring a custom Axon relay with an `accept.json` file, using the documented `auth` block does not work for setting authentication on outbound requests to the origin server. The `headers` block works correctly.

## What the docs say

The Axon Beta Packet and internal examples show this pattern for custom relay auth:

```json
{
  "private": [{
    "method": "any",
    "path": "/**",
    "origin": "http://my-server:8080",
    "auth": {
      "scheme": "basic",
      "value": "username:api-token"
    }
  }]
}
```

## What actually happens

When an `auth` block is present, the Snyk Broker injects an `authorization: ${AUTHORIZATION}` header into the request. This header is meant to be resolved from the environment, but:

1. The `${AUTHORIZATION}` is NOT resolved by the broker — it arrives at the origin server as a literal string
2. This literal string overrides whatever the `auth` block was supposed to set
3. The origin server receives `Authorization: ${AUTHORIZATION}` (literally) and rejects it

Without an `auth` block, the phantom `authorization: ${AUTHORIZATION}` header is not injected at all.

### Evidence from relay logs

With `auth` block present — note `authorization: ${AUTHORIZATION}` in request headers and `authHeaderSetByRuleAuth: true`:

```json
{
  "requestHeaders": {
    "content-type": "application/json",
    "authorization": "${AUTHORIZATION}",
    ...
  },
  "authHeaderSetByRuleAuth": true,
  "responseStatus": 401
}
```

Without `auth` block — no authorization header, origin returns 403 (anonymous access denied):

```json
{
  "requestHeaders": {
    "content-type": "application/json",
    ...
  },
  "responseStatus": 403
}
```

## What works

Use the `headers` block instead. The Go relay-reflector resolves `${ENV_VAR}` references in headers via `os.ExpandEnv()` at request time:

```json
{
  "private": [{
    "method": "any",
    "path": "/**",
    "origin": "http://my-server:8080",
    "headers": {
      "Authorization": "Basic ${AUTHORIZATION_TOKEN}"
    }
  }]
}
```

With the `AUTHORIZATION_TOKEN` environment variable set on the relay container to the base64-encoded `username:password`.

This produces `responseStatus: 201` — confirmed working with Jenkins.

## Root cause

The Axon relay agent has two layers:

1. **Go relay-reflector** — handles HTTP proxying, header injection, and env var resolution
2. **Snyk Broker (Node.js)** — handles WebSocket tunneling, accept file rule matching, and auth block processing

The `auth` block is processed by the Snyk Broker (Node.js layer), which sets `authHeaderSetByRuleAuth: true` in logs but fails to produce a valid Authorization header. Instead, it injects a literal `${AUTHORIZATION}` template variable that is never resolved.

The `headers` block is processed by the Go relay-reflector, which correctly resolves environment variables via `os.ExpandEnv()` and injects headers on the outbound HTTP request.

### Additional notes

- Environment variable substitution (`${VAR}`) works in the `origin` field (Go layer) and `headers` field (Go layer), but NOT in the `auth.value` field (Node.js layer)
- The `auth` block with `username`/`password` fields (instead of `value`) is parsed by the Go layer but silently dropped — not forwarded to the broker
- Setting an `AUTHORIZATION` env var on the relay container does not help — the broker does not resolve `${AUTHORIZATION}` in incoming request headers

## Recommendation

1. **Update docs**: Replace `auth` block examples with `headers` block for custom relays
2. **Investigate**: Whether the `auth` block is supposed to work and is a bug in the broker layer, or if it's only supported for built-in integration relays (which use the `-i` flag, not `-f`)
3. **Consider**: Adding a warning log when an `auth` block is present in a custom accept file, since it silently fails

## Reproduction

From `internal/`:

```bash
# Start Jenkins + relay
just axon-test

# Trigger workflow
curl -s -H "Authorization: Bearer $CORTEX_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST "${CORTEX_BASE_URL}/api/v1/workflows/jenkins-axon-relay/runs" \
  -d '{"scope": {"type": "GLOBAL"}}'

# Check relay logs
docker compose -f axon/compose.yaml logs -f jenkins-relay
```
