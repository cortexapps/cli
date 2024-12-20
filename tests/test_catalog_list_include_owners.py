from tests.helpers.utils import *

def test(capsys):
    response = cli(["catalog", "list", "-g", "public-api-test", "-io"])
    assert not(response['entities'][0]['owners']['teams'] is None), "Teams array should be returned in result"