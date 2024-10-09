from common import *

# Using a key with viewer role should be Forbidden.
@mock.patch.dict(os.environ, {"CORTEX_API_KEY": os.environ['CORTEX_API_KEY_VIEWER']})
def test(capsys):
    with pytest.raises(SystemExit) as excinfo:
       cli(["-q", "catalog", "create", "-f", "data/run-time/create-entity.yaml"])
       out, err = capsys.readouterr()

       assert out == "Forbidden"
       assert excinfo.value.code == 403
