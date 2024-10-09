from common import *

# Too brittle if we assume only one entity has group 'include-links-test'?
def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-g", "include-links-test"])
    assert (len(response['entities'][0]['links']) == 0)
    response = cli_command(capsys, ["catalog", "list", "-g", "include-links-test", "-l"])
    assert (len(response['entities'][0]['links']) > 0)
