from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list-descriptors", "-t", "service", "-p", "0", "-z", "1"])

    # YAML descriptor has single quotes, so cannot read it as valid JSON.  First convert to double quotes.
    json_data = json.loads(str(response).replace("'", "\""))
    assert len(json_data['descriptors']) == 1, "exactly one descriptor is returned"
