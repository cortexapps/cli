from common import *

def test(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli(["catalog", "list", "-z", "1001"])
        out, err = capsys.readouterr()

        assert "Page size must be set between 1 and 1000; requested value: 1005" in out, "Should get error text about invalid page parameter"
        assert excinfo.value.code == 400, "Page size greater than 100 should result in a Bad Request error, http code 400"
