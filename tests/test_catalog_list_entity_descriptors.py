from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list-descriptors", "-z", "5000"])
    list = [descriptor for descriptor in response['descriptors'] if descriptor['info']['x-cortex-tag'] == "autocomplete"]
    assert list[0]['info']['x-cortex-groups'][0] == "public-api-test"
