import json
import os
import tempfile
import pytest
from tests.helpers.utils import cli, ReturnType

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _period_payload(name="CLI Test Verification Period"):
    """Minimal valid verification period JSON payload."""
    return {
        "name": name,
        "startDate": "2026-09-14T00:00:00",
        "endDate": "2026-12-31T00:00:00",
        "scope": {
            "entityGroups": [],
            "excludedEntityGroups": [],
            "types": ["service"]
        },
        "requiredRoles": [],
        "requiredCustomRoleTags": [],
        "requiredTeamRoleTags": [],
        "reasonRequired": False,
    }


def _create_period(name="CLI Test Verification Period"):
    """Create a verification period and return the response dict."""
    payload = _period_payload(name)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        tmp_path = f.name
    try:
        return cli(["verifications", "periods", "create", "-f", tmp_path])
    finally:
        os.unlink(tmp_path)


def _delete_period(period_cid):
    """Delete a verification period by CID (force, no interactive prompt)."""
    result = cli(
        ["verifications", "periods", "delete", "--period-cid", period_cid, "--force"],
        return_type=ReturnType.RAW,
    )
    assert result.exit_code == 0, f"Delete failed: {result.output}"


# ---------------------------------------------------------------------------
# Help / structure tests (no API calls)
# ---------------------------------------------------------------------------

def test_verifications_help():
    result = cli(["verifications", "--help"], return_type=ReturnType.RAW)
    assert result.exit_code == 0
    assert "verifications" in result.output.lower()


def test_verifications_periods_help():
    result = cli(["verifications", "periods", "--help"], return_type=ReturnType.RAW)
    assert result.exit_code == 0
    assert "periods" in result.output.lower()


def test_verifications_entity_help():
    result = cli(["verifications", "entity", "--help"], return_type=ReturnType.RAW)
    assert result.exit_code == 0
    assert "entity" in result.output.lower()


# ---------------------------------------------------------------------------
# Periods CRUD
# ---------------------------------------------------------------------------

@pytest.mark.serial
def test_verifications_periods_create_and_delete():
    response = _create_period()
    assert "cid" in response, f"Expected 'cid' in response: {response}"
    period_cid = response["cid"]
    _delete_period(period_cid)


@pytest.mark.serial
def test_verifications_periods_list():
    period = _create_period("CLI Test List Period")
    period_cid = period["cid"]
    try:
        response = cli(["verifications", "periods", "list"])
        # client.fetch returns {"total": N, "periods": [...], ...}
        assert "periods" in response, f"Expected 'periods' key in response: {response.keys()}"
        cids = [p["cid"] for p in response["periods"]]
        assert period_cid in cids, f"Created period {period_cid} not in list"
    finally:
        _delete_period(period_cid)


@pytest.mark.serial
def test_verifications_periods_get():
    period = _create_period("CLI Test Get Period")
    period_cid = period["cid"]
    try:
        response = cli(["verifications", "periods", "get", "--period-cid", period_cid])
        assert response["cid"] == period_cid
        assert response["name"] == "CLI Test Get Period"
    finally:
        _delete_period(period_cid)


@pytest.mark.serial
def test_verifications_periods_update():
    period = _create_period("CLI Test Update Period")
    period_cid = period["cid"]
    try:
        updated_payload = _period_payload("CLI Test Updated Period")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(updated_payload, f)
            tmp_path = f.name
        try:
            response = cli(
                ["verifications", "periods", "update", "--period-cid", period_cid, "-f", tmp_path]
            )
            assert response["cid"] == period_cid
            assert response["name"] == "CLI Test Updated Period"
        finally:
            os.unlink(tmp_path)
    finally:
        _delete_period(period_cid)


# ---------------------------------------------------------------------------
# Verifications list (bulk)
# ---------------------------------------------------------------------------

@pytest.mark.serial
def test_verifications_list():
    period = _create_period("CLI Test Verifications List")
    period_cid = period["cid"]
    try:
        response = cli(["verifications", "list", "--period-cid", period_cid])
        # client.fetch returns {"total": N, "verifications": [...], ...}
        assert "verifications" in response, f"Expected 'verifications' key in response: {response.keys()}"
    finally:
        _delete_period(period_cid)


# ---------------------------------------------------------------------------
# Entity-level verifications
# ---------------------------------------------------------------------------

@pytest.mark.serial
def test_verifications_entity_list():
    result = cli(
        ["verifications", "entity", "list", "--tag", "cli-test-service"],
        return_type=ReturnType.RAW,
    )
    assert result.exit_code == 0, result.output


@pytest.mark.serial
def test_verifications_entity_verify_and_list():
    # Note: entity verify requires "Verify any entity" permission on the API key.
    # This test validates command structure and entity list behaviour only.
    period = _create_period("CLI Test Entity Verify")
    period_cid = period["cid"]
    try:
        # Entity list should succeed and include the period (entity is in scope as a service)
        result = cli(
            ["verifications", "entity", "list", "--tag", "cli-test-service"],
            return_type=ReturnType.RAW,
        )
        assert result.exit_code == 0, result.output
    finally:
        _delete_period(period_cid)


# ---------------------------------------------------------------------------
# Table / CSV output smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.serial
def test_verifications_periods_list_table():
    period = _create_period("CLI Test Table Output")
    period_cid = period["cid"]
    try:
        result = cli(["verifications", "periods", "list", "--table"], return_type=ReturnType.RAW)
        assert result.exit_code == 0, result.output
        # Rich wraps long cell values across rows; check for partial name fragments
        assert "CLI Test" in result.output
        assert "Table" in result.output
        assert "Output" in result.output
    finally:
        _delete_period(period_cid)
