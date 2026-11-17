from tests.helpers.utils import *
from urllib.parse import parse_qs, urlparse

# Responses are mocked: listing exemptions needs exemptions in a known state,
# which the shared test tenants cannot guarantee (see test_scorecards.py).

EXEMPTIONS_URL = os.getenv("CORTEX_BASE_URL") + "/api/v1/scorecards/exemptions"

def _exemption(id, status="APPROVED"):
    return {
        "id": id,
        "scorecardTag": "cli-test-scorecard",
        "scorecardName": "CLI Test Scorecard",
        "ruleIdentifier": "rule-" + str(id),
        "ruleTitle": "Has Custom Data",
        "ruleExpression": "custom(\"foo\") != null",
        "entityTag": "cli-test-service",
        "entityName": "CLI Test Service",
        "requestingReason": "test",
        "requestedBy": {"type": "USER", "name": "Jane", "email": "jane@example.com"},
        "requestedDate": "2026-10-01T00:00:00",
        "endDate": None,
        "exemptionStatus": {"status": status, "handledBy": None, "date": None},
        "requestedApprovers": [],
    }

def _page(exemptions, page, total_pages, total):
    return {"total": total, "page": page, "totalPages": total_pages, "exemptions": exemptions}

def _query(call):
    return {k: v[0] for k, v in parse_qs(urlparse(call.request.url).query).items()}

def test_exemptions_help_lists_list_command():
    response = cli(["scorecards", "exemptions", "--help"], return_type=ReturnType.STDOUT)
    assert "List Scorecard rule exemptions" in response

@responses.activate
def test_exemptions_list_fetches_all_pages():
    responses.add(responses.GET, EXEMPTIONS_URL, json=_page([_exemption(1), _exemption(2)], 0, 2, 3), status=200)
    responses.add(responses.GET, EXEMPTIONS_URL, json=_page([_exemption(3)], 1, 2, 3), status=200)

    response = cli(["scorecards", "exemptions", "list"])

    assert [e["id"] for e in response["exemptions"]] == [1, 2, 3]
    assert [_query(c)["page"] for c in responses.calls] == ["0", "1"]

FILTER_QUERY = {
    "scorecardTag": "cli-test-scorecard",
    "entityTag": "cli-test-service",
    "ruleIdentifier": "rule-1",
    "status": "PENDING",
    "requesterEmail": "jane@example.com",
    "approverEmail": "john@example.com",
    "onlyActive": "true",
    "page": "0",
    "pageSize": "250",
}

@responses.activate
def test_exemptions_list_sends_filters():
    responses.add(responses.GET, EXEMPTIONS_URL, json=_page([], 0, 0, 0), status=200)

    cli([
        "scorecards", "exemptions", "list",
        "--scorecard-tag", "cli-test-scorecard",
        "--entity-tag", "cli-test-service",
        "--rule-id", "rule-1",
        "--status", "PENDING",
        "--requester-email", "jane@example.com",
        "--approver-email", "john@example.com",
        "--only-active",
    ])

    assert _query(responses.calls[0]) == FILTER_QUERY

@responses.activate
def test_exemptions_list_short_flags():
    responses.add(responses.GET, EXEMPTIONS_URL, json=_page([], 0, 0, 0), status=200)

    cli([
        "scorecards", "exemptions", "list",
        "-s", "cli-test-scorecard", "-e", "cli-test-service", "-ri", "rule-1",
        "-st", "PENDING", "-re", "jane@example.com", "-ae", "john@example.com", "-a",
    ])

    assert _query(responses.calls[0]) == FILTER_QUERY

@responses.activate
def test_exemptions_list_omits_unset_filters():
    responses.add(responses.GET, EXEMPTIONS_URL, json=_page([], 0, 0, 0), status=200)

    cli(["scorecards", "exemptions", "list"])

    assert _query(responses.calls[0]) == {"page": "0", "pageSize": "250"}

def test_exemptions_list_rejects_unknown_status():
    result = cli(["scorecards", "exemptions", "list", "--status", "BOGUS"], return_type=ReturnType.RAW)
    assert result.exit_code != 0

@responses.activate
def test_exemptions_list_single_page():
    responses.add(responses.GET, EXEMPTIONS_URL, json=_page([_exemption(3)], 1, 2, 3), status=200)

    response = cli(["scorecards", "exemptions", "list", "--page", "1", "--page-size", "2"])

    assert len(responses.calls) == 1
    assert _query(responses.calls[0]) == {"page": "1", "pageSize": "2"}
    assert response == _page([_exemption(3)], 1, 2, 3)

@responses.activate
def test_exemptions_list_table():
    responses.add(responses.GET, EXEMPTIONS_URL, json=_page([_exemption(7, "PENDING")], 0, 1, 1), status=200)

    # wide terminal so rich doesn't truncate cells
    with mock.patch.dict(os.environ, {"COLUMNS": "200"}):
        response = cli(["scorecards", "exemptions", "list", "--table"], return_type=ReturnType.STDOUT)

    for header in ("ID", "Scorecard", "Rule", "Entity", "Status", "Requester", "EndDate"):
        assert header in response
    assert "rule-7" in response
    assert "PENDING" in response
    assert "jane@example.com" in response

@responses.activate
def test_exemptions_list_table_blank_requester_for_api_key():
    exemption = _exemption(9)
    exemption["requestedBy"] = {"type": "API", "apiKeyLast4": "a1b2"}
    responses.add(responses.GET, EXEMPTIONS_URL, json=_page([exemption], 0, 1, 1), status=200)

    with mock.patch.dict(os.environ, {"COLUMNS": "200"}):
        result = cli(["scorecards", "exemptions", "list", "--table"], return_type=ReturnType.RAW)

    assert result.exit_code == 0
    row = next(line for line in result.stdout.splitlines() if "rule-9" in line)
    cells = [cell.strip() for cell in row.strip("│").split("│")]
    assert cells[5] == "", "Requester cell should be blank when an API key requested the exemption"
