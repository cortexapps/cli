---
name: cortex-app-urls
description: Use when generating or displaying URLs to the Cortex web application — entity pages, scorecard pages, or any link to the Cortex UI. Covers the correct URL patterns for app.getcortexapp.com and how to derive the app URL from an API base URL.
---

# Cortex App URL Patterns

## STOP — memorize this before writing any URL or user-facing text

The entity page URL is `/admin/resources?tag=<tag>` — **NOT** `/admin/service/<tag>` and **NOT** `/admin/catalog/<tag>`.

Do not guess. Use the table below.

## Terminology

The correct term is **entity** (or **entities**). The word **resource** / **resources** is retired and must not appear in user-facing output, CLI messages, or documentation. The URL path `/admin/resources` is a legacy route but is the correct one to use for entity pages.

## API vs App domains

| Purpose | Domain |
|---------|--------|
| API calls | `api.getcortexapp.com` |
| Web UI links | `app.getcortexapp.com` |

When you have an API base URL (e.g. from `CORTEX_BASE_URL` or the CLI session), derive the app URL by replacing `api.` with `app.`:

```python
app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
```

## Entity page URL

```
https://app.getcortexapp.com/admin/resources?tag=<entity-tag>
```

Example: `https://app.getcortexapp.com/admin/resources?tag=phoenix`

**NOT** `/admin/service/<tag>` — type-specific path; teams and domains return "No entity".
**NOT** `/admin/catalog/<tag>` — that path does not exist.

## Deploys page URL (entity subpage — requires numeric ID, not tag)

```
https://app.getcortexapp.com/admin/service/<numeric-entity-id>/deploys
```

Use `GET /api/v1/catalog/<tag>` → `.id` to get the numeric ID.

## Scorecard page URL

```
https://app.getcortexapp.com/admin/scorecards/<scorecard-tag>
```

## Other common pages

| Page | URL pattern |
|------|-------------|
| Entity | `https://app.getcortexapp.com/admin/resources?tag=<tag>` |
| Scorecard | `https://app.getcortexapp.com/admin/scorecards/<tag>` |
| Catalogs | `https://app.getcortexapp.com/admin/catalogs` |
| Initiatives | `https://app.getcortexapp.com/admin/initiatives` |

## In code

When generating clickable links in terminal output, use OSC 8 hyperlinks for iTerm2/compatible terminals:

```python
def _hyperlink(url: str, text: str = None) -> str:
    label = text if text is not None else url
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"
```
