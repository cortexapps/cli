from common import *

@pytest.mark.skipif(enable_cql_v2() == False, reason="Account flag ENABLE_CQL_V2 is not not set.")
def test_scorecards(capsys):
    scorecardTag = "public-api-test-scorecard"
    entityTag = "user-profile-metadata-service"

    response = cli_command(capsys, ["scorecards", "create", "-f", "data/run-time/scorecard.yaml"])
    assert response['scorecard']['tag'] == scorecardTag, "Scorecard with tag public-api-test-scorecard should be created"

    response = cli_command(capsys, ["scorecards", "list"])
    assert any(scorecard['tag'] == scorecardTag for scorecard in response['scorecards']), scorecard + " should be in list of scorecards"

    response = cli_command(capsys, ["scorecards", "shield", "-s", scorecardTag, "-t", entityTag])
    # Dear future (hopefully smarter) self, feel free to enhance the regex to search for the correct brackets and parentheses in the regular expression.
    assert re.search(".*Public API Test Scorecard.*https://img.shields.io.*", response['value']), "Value includes scorecard name and shields URL"

    response = cli_command(capsys, ["scorecards", "get", "-t", scorecardTag])
    assert response['scorecard']['tag'] == scorecardTag, "Can retrieve tag of scorecard"
    assert response['scorecard']['levels'][0]['level']['name'] == 'Gold', "Can retrieve level name defined in scorecard"

    response = cli_command(capsys, ["scorecards", "descriptor", "-t", scorecardTag], "text")
    assert yaml.safe_load(response)['tag'] == scorecardTag, "Can get tag from YAML descriptor"
 
#    cli(["scorecards", "next-steps", "-t", "public-api-test-scorecard", "-e", "user-profile-metadata-service"])

#    # Not sure if we can run this cli right away.  Newly-created Scorecard might not be evaluated yet.
#    cli(["scorecards", "scores", "-t", "public-api-test-scorecard", "-e", "user-profile-metadata-service"])
 
#    cli(["scorecards", "scores", "-t", "public-api-test-scorecard"])
