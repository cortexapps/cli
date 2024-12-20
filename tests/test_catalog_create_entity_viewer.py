from tests.helpers.utils import *

# Using a key with viewer role should be Forbidden.
@mock.patch.dict(os.environ, {"CORTEX_API_KEY": os.environ['CORTEX_API_KEY_VIEWER']})
def test(capsys):
    response = cli(["catalog", "create", "-f", "data/run-time/create-entity.yaml"], ReturnType.RAW)

    assert "HTTP Error 403:" in response.stdout, "command fails with 403 error"
