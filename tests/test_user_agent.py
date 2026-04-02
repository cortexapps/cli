from tests.helpers.utils import *

@responses.activate
def test_user_agent_header_is_set():
    """Verify that all API requests include a User-Agent header identifying the CLI."""
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/catalog", json={"entities": [], "total": 0, "page": 0, "totalPages": 0}, status=200)
    cli(["catalog", "list", "-p", "0"])
    assert len(responses.calls) == 1
    user_agent = responses.calls[0].request.headers.get("User-Agent", "")
    assert user_agent.startswith("cortexapps-cli/")

@responses.activate
def test_user_agent_header_contains_version():
    """Verify that the User-Agent header contains the package version."""
    import importlib.metadata
    expected_version = importlib.metadata.version('cortexapps_cli')
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/catalog", json={"entities": [], "total": 0, "page": 0, "totalPages": 0}, status=200)
    cli(["catalog", "list", "-p", "0"])
    user_agent = responses.calls[0].request.headers.get("User-Agent", "")
    assert user_agent == f"cortexapps-cli/{expected_version}"
