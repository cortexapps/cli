from tests.helpers.utils import *
import yaml

# Get rule id to be used in exemption tests.  Need to revoke any existing rules.
def _get_rule(num):
    response =  cli(["scorecards", "get", "-s", "test-scorecard"])
    key = os.environ['CORTEX_API_KEY']
    print("here in _get_rule . . ., CORTEX_API_KEY = " + key)
    return response['scorecard']['rules'][num]['identifier']

def test_scorecards():
    cli(["scorecards", "create", "-f", "tests/test_scorecards.yaml"])

    response = cli(["scorecards", "list"])
    assert any(scorecard['tag'] == 'test-scorecard' for scorecard in response['scorecards']), "Should find scorecard with tag test-scorecard"

    response = cli(["scorecards", "shield", "-s", "test-scorecard", "-t", "test-service"])
    assert "img.shields.io" in response['value'], "shields url should be included in string"

    response =  cli(["scorecards", "get", "-s", "test-scorecard"])
    assert response['scorecard']['tag'] == "test-scorecard", "JSON response should have scorecard tag"


    response = cli(["scorecards", "descriptor", "-s", "test-scorecard"], return_type=ReturnType.STDOUT)
    assert "Used to test Cortex CLI" in response, "description of scorecard found in descriptor"

    # cannot rely on a scorecard evaluation being complete, so not performing any validation
    cli(["scorecards", "next-steps", "-s", "test-scorecard", "-t", "test-service"])
#
#    # Not sure if we can run this cli right away.  Newly-created Scorecard might not be evaluated yet.
#    # 2024-05-06, additionally now blocked by CET-8882
#    # cli(["scorecards", "scores", "-t", "test-scorecard", "-e", "test-service"])
#
#    cli(["scorecards", "scores", "-t", "test-scorecard"])
#
#def test_scorecards_drafts(capsys):
#    cli(["scorecards", "create", "-f", "tests/test_scorecards_draft.yaml"])
#
#    cli(["scorecards", "list", "-s"])
#    out, err = capsys.readouterr()
#
#    out = json.loads(out)
#    assert any(scorecard['tag'] == 'test-scorecard-draft' for scorecard in out['scorecards'])

@pytest.fixture(scope='session')
@mock.patch.dict(os.environ, {"CORTEX_API_KEY": os.environ['CORTEX_API_KEY_VIEWER']})
def test_exemption_that_will_be_approved():
    rule_id = _get_rule(0)
    print("rule_id = " + rule_id)
    response = cli(["scorecards", "exemptions", "request", "-s", "test-scorecard", "-t", "test-service", "-r", "test approve", "-ri", rule_id, "-d", "100"])

@pytest.mark.usefixtures('test_exemption_that_will_be_approved')
def test_approve_exemption():
    rule_id = _get_rule(0)
    print("rule_id = " + rule_id)
    response = cli(["scorecards", "exemptions", "approve", "-s", "test-scorecard", "-t", "test-service", "-ri", rule_id])
    response = cli(["scorecards", "exemptions", "revoke", "-s", "test-scorecard", "-t", "test-service", "-r", "I revoke you", "-ri", rule_id])

@pytest.fixture(scope='session')
@mock.patch.dict(os.environ, {"CORTEX_API_KEY": os.environ['CORTEX_API_KEY_VIEWER']})
def test_exemption_that_will_be_denied():
    rule_id = _get_rule(1)
    print("rule_id = " + rule_id)
    response = cli(["scorecards", "exemptions", "request", "-s", "test-scorecard", "-t", "test-service", "-r", "test deny", "-ri", rule_id, "-d", "100"])

@pytest.mark.usefixtures('test_exemption_that_will_be_denied')
def test_deny_exemption():
    rule_id = _get_rule(1)
    print("rule_id = " + rule_id)
    response = cli(["scorecards", "exemptions", "deny", "-s", "test-scorecard", "-t", "test-service", "-r", "I deny, therefore I am", "-ri", rule_id])
