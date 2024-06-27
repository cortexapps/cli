from common import *

# Using a key with viewer role should be Forbidden.
@mock.patch.dict(os.environ, {"CORTEX_API_KEY": os.environ['CORTEX_API_KEY_VIEWER']})
def test(capsys):
    with pytest.raises(SystemExit) as excinfo:
       cli(["-q", "plugins", "create", "-f", "data/run-time/test_plugins_manager.json"])
       out, err = capsys.readouterr()

       assert out == "Forbidden", "Attempt to create plugin as a VIEWER with minimumRole defined as MANAGER should be Forbidden"
       assert excinfo.value.code == 403, "VIEWER role cannot create plugin with minimumRole defined as MANAGER"

    with pytest.raises(SystemExit) as excinfo:
       cli(["-q", "plugins", "create", "-f", "data/run-time/test_plugins_invalid_role.json"])
       out, err = capsys.readouterr()

       assert out == "Bad Request", "Invalid minimumRole results in Bad Request"
       assert excinfo.value.code == 400, "Invalid minimumRole should result in 400 return code"
