import io
import logging
import pytest
import responses
import typer

from cortexapps_cli.cortex_client import CortexClient

BASE_URL = "https://api.test.example.com"


def make_client():
    return CortexClient(
        api_key="test-key",
        tenant="default",
        numeric_level=logging.WARNING,
        base_url=BASE_URL,
        rate_limit=60000,
    )


# ---------------------------------------------------------------------------
# Task 6: Error handling paths (Lines 77-78, 162-173, 182-188)
# ---------------------------------------------------------------------------

def test_version_fallback_when_package_not_found():
    from unittest.mock import patch
    import importlib.metadata
    with patch("importlib.metadata.version", side_effect=importlib.metadata.PackageNotFoundError):
        client = CortexClient(
            api_key="test-key",
            tenant="default",
            numeric_level=logging.WARNING,
            base_url=BASE_URL,
            rate_limit=60000,
        )
    assert client.version == "unknown"


@responses.activate
def test_request_error_with_violations():
    client = make_client()
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/test",
        json={
            "violations": [
                {
                    "title": "Bad Field",
                    "description": "Field is invalid",
                    "violationType": "CONSTRAINT",
                    "pointer": "/field",
                },
                {
                    "title": "Missing Field",
                    "description": "Required field missing",
                },
            ]
        },
        status=400,
    )
    with pytest.raises(typer.Exit):
        client.get("api/v1/test")


@responses.activate
def test_request_error_with_violations_minimal_fields():
    client = make_client()
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/test",
        json={
            "violations": [
                {}
            ]
        },
        status=400,
    )
    with pytest.raises(typer.Exit):
        client.get("api/v1/test")


@responses.activate
def test_request_error_non_json_response():
    client = make_client()
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/test",
        body="<html>502 Bad Gateway</html>",
        status=502,
        content_type="text/html",
    )
    with pytest.raises(typer.Exit):
        client.get("api/v1/test")


# ---------------------------------------------------------------------------
# Task 7: Response fallbacks and read_file (Lines 198-201, 310)
# ---------------------------------------------------------------------------

@responses.activate
def test_request_ok_non_json_returns_text():
    client = make_client()
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/test",
        body="plain text response",
        status=200,
        content_type="text/plain",
    )
    result = client.get("api/v1/test")
    assert result == "plain text response"


def test_read_file():
    client = make_client()
    f = io.StringIO("file contents")
    assert client.read_file(f) == "file contents"


# ---------------------------------------------------------------------------
# Task 8: `fetch` edge cases (Lines 229, 238-240, 250)
# ---------------------------------------------------------------------------

@responses.activate
def test_fetch_non_dict_non_list_response_breaks():
    client = make_client()
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/test",
        body="not json at all",
        status=200,
        content_type="text/plain",
    )
    result = client.fetch("api/v1/test")
    # When response is not dict/list, fetch breaks immediately with data_key still None.
    # The return statement at line 252-257 creates {"total": 0, "page": 0, "totalPages": 0, None: []}
    assert result["total"] == 0
    assert result["page"] == 0
    assert result["totalPages"] == 0
    assert None in result
    assert result[None] == []


@responses.activate
def test_fetch_list_response_pagination():
    client = make_client()
    # First page returns items
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/test",
        json=[{"id": 1}, {"id": 2}],
        status=200,
    )
    # Second page returns empty list (signals end)
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/test",
        json=[],
        status=200,
    )
    result = client.fetch("api/v1/test")
    assert result == [{"id": 1}, {"id": 2}]


# ---------------------------------------------------------------------------
# Task 9: Entity helper methods with team type
# (Lines 270, 274-280, 283-289, 292-298, 301-307)
# ---------------------------------------------------------------------------

@responses.activate
def test_get_entity_team_type():
    client = make_client()
    responses.add(responses.GET, f"{BASE_URL}/api/v1/teams/my-team", json={"tag": "my-team"}, status=200)
    result = client.get_entity("my-team", entity_type="team")
    assert result["tag"] == "my-team"
    assert "/teams/" in responses.calls[0].request.url


@responses.activate
def test_get_entity_catalog_type():
    client = make_client()
    responses.add(responses.GET, f"{BASE_URL}/api/v1/catalog/my-service", json={"tag": "my-service"}, status=200)
    result = client.get_entity("my-service", entity_type="service")
    assert "/catalog/" in responses.calls[0].request.url


@responses.activate
def test_delete_entity_team_type():
    client = make_client()
    responses.add(responses.DELETE, f"{BASE_URL}/api/v1/teams/my-team", json={}, status=200)
    client.delete_entity("my-team", entity_type="teams")
    assert "/teams/" in responses.calls[0].request.url


@responses.activate
def test_delete_entity_catalog_type():
    client = make_client()
    responses.add(responses.DELETE, f"{BASE_URL}/api/v1/catalog/my-service", json={}, status=200)
    client.delete_entity("my-service", entity_type="service")
    assert "/catalog/" in responses.calls[0].request.url


@responses.activate
def test_archive_entity_team_type():
    client = make_client()
    responses.add(responses.PUT, f"{BASE_URL}/api/v1/teams/my-team/archive", json={}, status=200)
    client.archive_entity("my-team", entity_type="team")
    assert "/teams/" in responses.calls[0].request.url


@responses.activate
def test_archive_entity_catalog_type():
    client = make_client()
    responses.add(responses.PUT, f"{BASE_URL}/api/v1/catalog/my-service/archive", json={}, status=200)
    client.archive_entity("my-service", entity_type="service")
    assert "/catalog/" in responses.calls[0].request.url


@responses.activate
def test_unarchive_entity_team_type():
    client = make_client()
    responses.add(responses.PUT, f"{BASE_URL}/api/v1/teams/my-team/unarchive", json={}, status=200)
    client.unarchive_entity("my-team", entity_type="team")
    assert "/teams/" in responses.calls[0].request.url


@responses.activate
def test_unarchive_entity_catalog_type():
    client = make_client()
    responses.add(responses.PUT, f"{BASE_URL}/api/v1/catalog/my-service/unarchive", json={}, status=200)
    client.unarchive_entity("my-service", entity_type="service")
    assert "/catalog/" in responses.calls[0].request.url
