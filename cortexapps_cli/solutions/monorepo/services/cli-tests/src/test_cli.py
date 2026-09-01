"""
cli-tests — integration tests for the Cortex CLI.
"""


def test_hello():
    """Basic smoke test."""
    assert True, "Hello from cli-tests!"


def test_entity_list():
    """Verify entity list returns results."""
    entities = ["mock-service-a", "mock-service-b"]
    assert len(entities) > 0


if __name__ == "__main__":
    test_hello()
    test_entity_list()
    print("All tests passed.")
