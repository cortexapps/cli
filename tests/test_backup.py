from tests.helpers.utils import *
import os
import tempfile
import json

def test_backup_import_custom_metrics_invalid_api_key(monkeypatch):
    """
    Test that backup import of custom-metrics fails cleanly with invalid API key.
    """
    monkeypatch.setenv("CORTEX_API_KEY", "invalidKey")

    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_dir = os.path.join(tmpdir, "custom-metrics")
        os.makedirs(metrics_dir)

        metric_file = os.path.join(metrics_dir, "ai-spend.json")
        with open(metric_file, "w") as f:
            json.dump({
                "values": [
                    {
                        "entityTag": "employee-alice-chen",
                        "timestamp": "2026-07-28T00:00:00",
                        "value": 142.50
                    }
                ]
            }, f)

        result = cli(["backup", "import", "-d", tmpdir], return_type=ReturnType.RAW)
        assert result.exit_code != 0, (
            f"backup import should exit with non-zero code on failure, "
            f"got exit_code={result.exit_code}"
        )

def test_backup_import_invalid_api_key(monkeypatch):
    """
    Test that backup import exits with non-zero return code when API calls fail.
    """
    monkeypatch.setenv("CORTEX_API_KEY", "invalidKey")

    # Create a temp directory with a catalog subdirectory and a simple yaml file
    with tempfile.TemporaryDirectory() as tmpdir:
        catalog_dir = os.path.join(tmpdir, "catalog")
        os.makedirs(catalog_dir)

        # Create a minimal catalog entity file
        entity_file = os.path.join(catalog_dir, "test-entity.yaml")
        with open(entity_file, "w") as f:
            f.write("""
info:
  x-cortex-tag: test-entity
  title: Test Entity
  x-cortex-type: service
""")

        result = cli(["backup", "import", "-d", tmpdir], return_type=ReturnType.RAW)
        assert result.exit_code != 0, f"backup import should exit with non-zero code on failure, got exit_code={result.exit_code}"


def test_backup_export_invalid_api_key(monkeypatch):
    """
    Test that backup export exits with non-zero return code and clean error message when API calls fail.
    """
    monkeypatch.setenv("CORTEX_API_KEY", "invalidKey")

    with tempfile.TemporaryDirectory() as tmpdir:
        result = cli(["backup", "export", "-d", tmpdir], return_type=ReturnType.RAW)
        assert result.exit_code != 0, f"backup export should exit with non-zero code on failure, got exit_code={result.exit_code}"
        assert "HTTP Error 401" in result.stdout, "Should show HTTP 401 error message"
        assert "Traceback" not in result.stdout, "Should not show Python traceback"
