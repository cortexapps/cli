from tests.helpers.utils import *

# Too brittle if we assume only one entity has group 'include-metadata-test'?
def test():
    response = cli(["catalog", "list", "-g", "include-metadata-test"])
    assert (len(response['entities'][0]['metadata']) == 0)
    response = cli(["catalog", "list", "-g", "include-metadata-test", "-m"])
    assert (len(response['entities'][0]['metadata']) > 0)
