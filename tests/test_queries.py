"""
Tests for queries commands.
"""
from cortexapps_cli.cortex import cli
import json
import sys
import time

@pytest.mark.skip(reason="Performance bad in production; disabling for now")
def test_queries_run(capsys):
    cli(["queries", "run", "-f", "tests/test_queries.json"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    jobId = out['jobId']
    #sys.stdout.write("jobId = " + jobId)
    # TODO: add while loop while query status is IN_PROGESS, wait until
    # status is SUCCCESS.
    max_attempts = 60
    for attempt in range(1, max_attempts):
        #print("check " + str(attempt) + " of " + str(max_attempts))
        cli(["queries", "get", "-i", jobId])
        out, err = capsys.readouterr()
        out = json.loads(out)
        status = out['status']
        if status == "DONE":
            break
        else:
            if attempt == max_attempts:
                print("failed to find job id " + jobId + " in DONE state")
                sys.exit(2)
            time.sleep(2)
