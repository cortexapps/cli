from tests.helpers.utils import *

def test_users_roles_list():
    response = cli(["users", "roles", "list"])
    assert "users" in response, "Response should contain 'users' key"
    assert len(response["users"]) > 0, "Should have at least one user with role assignments"

    first_user = response["users"][0]
    assert "email" in first_user, "User should have an email field"
    assert "name" in first_user, "User should have a name field"
    assert "roles" in first_user, "User should have a roles field"

def test_users_roles_list_with_email_filter():
    # First, get a valid email from the full list
    response = cli(["users", "roles", "list"])
    email = response["users"][0]["email"]

    # Filter by that email
    response = cli(["users", "roles", "list", "-e", email])
    assert len(response["users"]) == 1, "Should return exactly one user"
    assert response["users"][0]["email"].lower() == email.lower(), "Returned user email should match filter"

def test_users_roles_list_with_multiple_email_filter():
    # Get two emails from the full list
    response = cli(["users", "roles", "list"])
    if len(response["users"]) < 2:
        pytest.skip("Need at least 2 users to test multiple email filter")

    email1 = response["users"][0]["email"]
    email2 = response["users"][1]["email"]

    response = cli(["users", "roles", "list", "-e", email1, "-e", email2])
    assert len(response["users"]) == 2, "Should return exactly two users"
    returned_emails = {u["email"].lower() for u in response["users"]}
    assert email1.lower() in returned_emails, "First filtered email should be in results"
    assert email2.lower() in returned_emails, "Second filtered email should be in results"

def test_users_roles_list_table_output():
    response = cli(["users", "roles", "list", "--table"], ReturnType.STDOUT)
    assert "Email" in response, "Table output should contain Email header"
    assert "Name" in response, "Table output should contain Name header"
    assert "Roles" in response, "Table output should contain Roles header"

def test_users_roles_list_pagination():
    response = cli(["users", "roles", "list", "-p", "0", "-z", "1"])
    assert "users" in response, "Response should contain 'users' key"
    assert len(response["users"]) <= 1, "Should return at most 1 user per page"
    assert "page" in response, "Response should contain 'page' field"
    assert "total" in response, "Response should contain 'total' field"
