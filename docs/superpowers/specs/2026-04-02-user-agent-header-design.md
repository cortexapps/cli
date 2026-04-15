# User-Agent Header for CLI API Requests

## Problem

There is no way to distinguish CLI-originated API traffic from other sources (direct API calls, SDKs, UI) in DataDog logs.

## Solution

Add a `User-Agent` header to all HTTP requests made by `CortexClient`.

**Format:** `cortexapps-cli/<version>` (e.g., `cortexapps-cli/1.9.1`)

## Implementation

### Version Resolution

Use `importlib.metadata.version('cortexapps_cli')` in `CortexClient.__init__()`. This returns the installed package version. Fall back to `unknown` if resolution fails.

- Released installs (PyPI, Homebrew, Docker): returns the release version (e.g., `1.9.1`)
- Local dev / PR testing: returns `0.0.0` (the default in `pyproject.toml`)

### Header Injection

Add `User-Agent` to `req_headers` in `CortexClient.request()`:

```python
req_headers = {
    'Authorization': f'Bearer {self.api_key}',
    'Content-Type': content_type,
    'User-Agent': f'cortexapps-cli/{self.version}',
    **headers
}
```

Placing `User-Agent` before `**headers` allows callers to override it if needed.

### Files Changed

- `cortexapps_cli/cortex_client.py` — add version resolution in `__init__()`, add header in `request()`
- `tests/test_user_agent.py` — unit test verifying the header is sent

### Testing

Unit test using the `responses` library (already a dev dependency) to mock HTTP and assert the `User-Agent` header value on outgoing requests.

### DataDog Usage

- Filter CLI traffic: `@user-agent:cortexapps-cli*`
- Group by version: facet on `@user-agent`
- Distinguish dev from production: version `0.0.0` = dev/PR testing

## What This Does NOT Include

- No custom headers (`X-Cortex-Command`, etc.) — the API endpoint path already identifies the operation
- No configuration to disable the header — it is always sent
- No command-level tracking — can be added later if needed
