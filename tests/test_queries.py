from tests.helpers.utils import *
from urllib.error import HTTPError

def test():
    try:
        response = cli(["queries", "run", "-f", "tests/test_queries.txt"])
    except HTTPError as e:
        status_code = e.response.status_code
        if status_code == "409":
            print("Query with same CQL is already running")
    except:
        print("Got an error for which I was not prepared.  It's me.  Not you.")
    else:
        job_id = response["jobId"]
        response = cli(["queries", "get", "-j", job_id])
        assert response["queryDetails"]['jobId'] == job_id, "Should return query with same jobId returned by queries run"
