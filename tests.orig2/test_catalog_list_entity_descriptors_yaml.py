from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list-descriptors", "-y", "-t", "component"])
    list = [descriptor for descriptor in response['descriptors'] if yaml.safe_load(descriptor)['info']['x-cortex-tag'] == "backend-worker"]
    assert yaml.safe_load(list[0])['info']['x-cortex-custom-metadata']['cicd'] == "circle-ci"
