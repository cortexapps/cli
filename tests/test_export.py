from tests.helpers.utils import *

def test():
    response = cli(["backup", "export", "-e", "workflows,scorecards"], ReturnType.STDOUT)
