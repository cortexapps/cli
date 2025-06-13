from tests.helpers.utils import *

@pytest.mark.setup
def test():
    response = cli(["backup", "import", "-d", "data/import"], return_type=ReturnType.STDOUT)
    print(response)
