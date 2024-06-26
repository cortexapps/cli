from common import *

@pytest.mark.skipif(enable_cql_v2() == False, reason="Account flag ENABLE_CQL_V2 is not not set.")
def test(capsys):
    cli_command(capsys, ["scorecards", "create", "-f", "data/run-time/scorecard_drafts.yaml"])

    response = cli_command(capsys, ["scorecards", "list", "-s"])
    assert any(scorecard['tag'] == 'public-api-test-draft-scorecard' for scorecard in response['scorecards']), "Draft scorecards are returned with showDrafts query parameter"

    response = cli_command(capsys, ["scorecards", "list"])
    assert not any(scorecard['tag'] == 'public-api-test-draft-scorecard' for scorecard in response['scorecards']), "Draft scorecards are not returned without showDrafts query parameter"
