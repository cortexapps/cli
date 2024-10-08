from tests.helpers.utils import *

def test():
    response = json_response(["catalog", "details", "-t", "backend-worker"])
    list = [metadata for metadata in response['metadata'] if metadata['key'] == "cicd"]
    assert list[0]['value'] == "circle-ci"
