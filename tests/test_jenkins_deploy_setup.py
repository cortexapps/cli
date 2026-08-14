import importlib.util
import pytest
from pathlib import Path


def load_setup_module():
    spec = importlib.util.spec_from_file_location(
        "jenkins_deploy_setup",
        "cortexapps_cli/solutions/jenkins-deploy/setup.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_yaml_is_valid():
    import yaml
    path = Path("cortexapps_cli/solutions/jenkins-deploy/catalog/jenkins-demo.yaml")
    data = yaml.safe_load(path.read_text())
    assert data["info"]["x-cortex-tag"] == "jenkins-demo"
    meta = data["info"]["x-cortex-custom-metadata"]["jenkins"]
    assert "url" in meta
    assert "job" in meta
    assert "username" in meta
    assert "token" in meta


def test_scorecard_yaml_is_valid():
    import yaml
    path = Path("cortexapps_cli/solutions/jenkins-deploy/scorecards/deploy-health.yaml")
    data = yaml.safe_load(path.read_text())
    assert data["tag"] == "jenkins-deploy-health"
    assert len(data["rules"]) == 3
    levels = {r["level"] for r in data["rules"]}
    assert levels == {"Bronze", "Silver", "Gold"}
