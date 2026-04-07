import pytest
from tests.helpers.utils import *

@pytest.mark.functional
def test_sample():
    """Sample functional test - replace with real tests."""
    response = cli(["catalog", "list"])
    assert response is not None
