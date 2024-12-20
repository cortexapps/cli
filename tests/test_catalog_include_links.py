from tests.helpers.utils import *

# Too brittle if we assume only one entity has group 'include-links-test'?
def test():
    response = cli(["catalog", "list", "-g", "include-links-test"])
    assert (len(response['entities'][0]['links']) == 0)
    response = cli(["catalog", "list", "-g", "include-links-test", "-l"])
    assert (len(response['entities'][0]['links']) > 0)
