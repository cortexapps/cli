from tests.helpers.utils import *

@pytest.mark.skip(reason="Cannot rely on scorecard to have been evaluated.  Need FR to force evaluation?")
def test():
    response = cli(["catalog", "scorecard-scores", "-t", "backend-worker"])
    list = [scorecard for scorecard in response if scorecard['scorecardName'] == "Public API Test Production Readiness"]
    assert list[0]['score'] == 1
