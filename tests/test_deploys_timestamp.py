import time

from tests.helpers.utils import *

# Fixed-offset zone (UTC-5, no DST) so the local->UTC conversion is deterministic
# regardless of the machine/CI timezone.
_TZ = "Etc/GMT+5"


def _with_fixed_tz(fn):
    old_tz = os.environ.get("TZ")
    os.environ["TZ"] = _TZ
    time.tzset()
    try:
        fn()
    finally:
        if old_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old_tz
        time.tzset()


def _posted_timestamp(cli_args):
    responses.add(
        responses.POST,
        os.getenv("CORTEX_BASE_URL") + "/api/v1/catalog/cli-test-service/deploys",
        json={},
        status=200,
    )
    cli(cli_args)
    return json.loads(responses.calls[0].request.body)["timestamp"]


@responses.activate
def test_add_converts_local_timestamp_to_utc():
    """An explicit local --timestamp is converted to UTC before being sent with a Z suffix"""
    def check():
        ts = _posted_timestamp([
            "deploys", "add", "-t", "cli-test-service",
            "--title", "my title", "--type", "DEPLOY",
            "--timestamp", "2020-01-15T10:30:00",
        ])
        # 10:30 in UTC-5 is 15:30 UTC
        assert ts == "2020-01-15T15:30:00Z"

    _with_fixed_tz(check)
