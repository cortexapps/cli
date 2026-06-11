# Users Roles Command Design

## Summary

Add a `cortex users roles list` command to support the `GET /api/v1/users/roles` endpoint. The command is structured as a subcommand group (`users` > `roles` > `list`) to accommodate future user and role management endpoints.

## API Endpoint

**`GET /api/v1/users/roles`**

Query parameters:
- `email` (optional): Comma-separated email addresses, case-insensitive
- `pageSize` (optional): 1-1000, defaults to 250
- `page` (optional): Zero-indexed, defaults to 0

Response:
```json
{
  "page": 0,
  "total": 100,
  "totalPages": 1,
  "users": [
    {
      "email": "user@example.com",
      "name": "User Name",
      "roles": [
        { "type": "BASIC", "role": "ADMIN" },
        { "type": "CUSTOM", "name": "My Role", "tag": "my-role" }
      ]
    }
  ]
}
```

Requires Bearer token with "View Roles" permission.

## File Structure

```
cortexapps_cli/commands/
  users.py                     # Top-level users Typer app, imports roles subcommand
  users_commands/
    __init__.py
    roles.py                   # roles subcommand with `list` command
```

Registration in `cli.py`:
```python
import cortexapps_cli.commands.users as users
app.add_typer(users.app, name="users")
```

Follows the existing `scorecards` / `scorecards_commands/exemptions` pattern.

## Command: `cortex users roles list`

### Options

Standard `ListCommandOptions`:
- `--page, -p`: Page number (omit to fetch all pages)
- `--page-size, -z`: Results per page (default 250)
- `--table`: Table output
- `--csv`: CSV output
- `--columns, -C`: Column selection
- `--no-headers`: Suppress table/CSV headers
- `--filter, -F`: Row filtering
- `--sort, -S`: Row sorting

Custom:
- `--email, -e`: Repeatable option to filter by email address(es). Multiple values joined comma-separated for the API.

### Default Table Columns

When `--table` or `--csv` is used without explicit `--columns`:
- `Email=email`
- `Name=name`
- `Roles=roles`

### Behavior

- No `--page`: calls `client.fetch()` for all pages
- With `--page`: calls `client.get()` for a single page
- Output via `print_output_with_context()`

## Future Extensibility

- `users.py` will host top-level user commands (e.g., `users get`, `users create`)
- `users_commands/roles.py` will host additional role commands (e.g., `roles create`, `roles update`)

## Testing

Integration tests against jeff-sandbox tenant with Okta SCIM provisioned users. Test file: `tests/test_users.py`.

Tests:
- `test_users_roles_list`: List all user role assignments
- `test_users_roles_list_with_email_filter`: Filter by one or more emails
- `test_users_roles_list_table_output`: Verify table formatting
- `test_users_roles_list_pagination`: Single page retrieval
