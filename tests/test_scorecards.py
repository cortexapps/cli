from tests.helpers.utils import *
import yaml
import time

# Get rule id to be used in exemption tests.
# TODO: check for and revoke any PENDING exemptions.
@mock.patch.dict(os.environ, {"CORTEX_API_KEY": os.environ['CORTEX_API_KEY']})
def _get_rule(title):
    response =  cli(["scorecards", "get", "-s", "cli-test-scorecard"])
    rule_id = [rule['identifier'] for rule in response['scorecard']['rules'] if rule['title'] == title]
    return rule_id[0]

def test_scorecards():
    # Retry scorecard create in case there's an active evaluation
    # (can happen if test_import.py just triggered an evaluation)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            cli(["scorecards", "create", "-f", "data/import/scorecards/cli-test-scorecard.yaml"])
            break
        except Exception as e:
            if "500" in str(e) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s
                continue
            raise

    response = cli(["scorecards", "list"])
    assert any(scorecard['tag'] == 'cli-test-scorecard' for scorecard in response['scorecards']), "Should find scorecard with tag cli-test-scorecard"

    response = cli(["scorecards", "shield", "-s", "cli-test-scorecard", "-t", "cli-test-service"])
    assert "img.shields.io" in response['value'], "shields url should be included in string"

    response =  cli(["scorecards", "get", "-s", "cli-test-scorecard"])
    assert response['scorecard']['tag'] == "cli-test-scorecard", "JSON response should have scorecard tag"

    response = cli(["scorecards", "descriptor", "-s", "cli-test-scorecard"], return_type=ReturnType.STDOUT)
    assert "Used to test Cortex CLI" in response, "description of scorecard found in descriptor"

    # cannot rely on a scorecard evaluation being complete, so not performing any validation
    cli(["scorecards", "next-steps", "-s", "cli-test-scorecard", "-t", "cli-test-service"])

    # Test trigger-evaluation command (accepts both success and 409 Already evaluating)
    response = cli(["scorecards", "trigger-evaluation", "-s", "cli-test-scorecard", "-e", "cli-test-service"], return_type=ReturnType.STDOUT)
    assert ("Scorecard evaluation triggered successfully" in response or "Already evaluating scorecard" in response), \
        "Should receive success message or 409 Already evaluating error"

    # cannot rely on a scorecard evaluation being complete, so not performing any validation
    #response = cli(["scorecards", "scores", "-s", "cli-test-scorecard", "-t", "cli-test-service"])
    #assert response['scorecardTag'] == "cli-test-scorecard", "Should get valid response that include cli-test-scorecard"
 
#    # Not sure if we can run this cli right away.  Newly-created Scorecard might not be evaluated yet.
#    # 2024-05-06, additionally now blocked by CET-8882
#    # cli(["scorecards", "scores", "-t", "cli-test-scorecard", "-e", "cli-test-service"])
#
#    cli(["scorecards", "scores", "-t", "cli-test-scorecard"])
 
def test_scorecards_drafts():
    # Retry scorecard create in case there's an active evaluation
    max_retries = 3
    for attempt in range(max_retries):
        try:
            cli(["scorecards", "create", "-f", "data/import/scorecards/cli-test-draft-scorecard.yaml"])
            break
        except Exception as e:
            if "500" in str(e) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s
                continue
            raise

    response = cli(["scorecards", "list", "-s"])
    assert any(scorecard['tag'] == 'cli-test-draft-scorecard' for scorecard in response['scorecards'])

    cli(["scorecards", "delete", "-s", "cli-test-draft-scorecard"])
    response = cli(["scorecards", "list", "-s"])
    assert not(any(scorecard['tag'] == 'cli-test-draft-scorecard' for scorecard in response['scorecards'])), "should not find deleted scorecard"

# Challenges with testing exemptions:
#
# - exemptions require scorecards that have evaluated with failing rules;
#   testing assumes no tenanted data, so this condition needs to be created as part of the test
#
# - there is no public API to force evaluation of a scorecard; can look into possibility of using
#   an internal endpoint for this
#
# - could create a scorecard as part of the test and wait for it to complete, but completion time for
#   evaluating a scorecard is non-deterministic and, as experienced with query API tests, completion
#   time can be 15 minutes or more, which will increase the time to complete testing by a factor of 5x
#   or more
#
# - exemptions requested by an API key with the Cortex ADMIN role are auto-approved, so the exemption must
#   be requested with a key that has non-ADMIN privileges
#
#   This means there are dependencies on running a test using a VIEWER role to request the exemption and a
#   subsequent test using an ADMIN role to act on the exemption
#
# So this is how we'll roll for now . . .
# - Automated tests currently run in known tenants that have the 'cli-test-scorecard' in an evaluated state.
# - So we can semi-reliably count on an evaluated scorecard to exist.

@pytest.fixture(scope='session')
@mock.patch.dict(os.environ, {"CORTEX_API_KEY": os.environ['CORTEX_API_KEY_VIEWER']})
def test_exemption_that_will_be_approved():
    rule_id = _get_rule("Has Custom Data")
    print("rule_id = " + rule_id)

    response = cli(["scorecards", "exemptions", "request", "-s", "cli-test-scorecard", "-t", "cli-test-service", "-r", "test approve", "-ri", rule_id, "-d", "100"])
    assert response['exemptionStatus']['status'] == 'PENDING', "exemption state should be PENDING"

@pytest.mark.usefixtures('test_exemption_that_will_be_approved')
def test_approve_exemption():
    rule_id = _get_rule("Has Custom Data")
    print("rule_id = " + rule_id)

    response = cli(["scorecards", "exemptions", "approve", "-s", "cli-test-scorecard", "-t", "cli-test-service", "-ri", rule_id])
    assert response['exemptions'][0]['exemptionStatus']['status'] == 'APPROVED', "exemption state should be APPROVED"
    response = cli(["scorecards", "exemptions", "revoke", "-s", "cli-test-scorecard", "-t", "cli-test-service", "-r", "I revoke you", "-ri", rule_id])
    assert response['exemptions'][0]['exemptionStatus']['status'] == 'REJECTED', "exemption state should be REJECTED"

@pytest.fixture(scope='session')
@mock.patch.dict(os.environ, {"CORTEX_API_KEY": os.environ['CORTEX_API_KEY_VIEWER']})
def test_exemption_that_will_be_denied():
    rule_id = _get_rule("Is Definitely False")
    print("rule_id = " + rule_id)

    response = cli(["scorecards", "exemptions", "request", "-s", "cli-test-scorecard", "-t", "cli-test-service", "-r", "test deny", "-ri", rule_id, "-d", "100"])
    assert response['exemptionStatus']['status'] == 'PENDING', "exemption state should be PENDING"

@pytest.mark.usefixtures('test_exemption_that_will_be_denied')
def test_deny_exemption():
    rule_id = _get_rule("Is Definitely False")
    print("rule_id = " + rule_id)

    response = cli(["scorecards", "exemptions", "deny", "-s", "cli-test-scorecard", "-t", "cli-test-service", "-r", "I deny, therefore I am", "-ri", rule_id])
    assert response['exemptions'][0]['exemptionStatus']['status'] == 'REJECTED', "exemption state should be REJECTED"
