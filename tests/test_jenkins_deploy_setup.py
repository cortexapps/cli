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


def test_jenkinsfile_has_required_elements():
    path = Path("cortexapps_cli/solutions/jenkins-deploy/_templates/Jenkinsfile")
    content = path.read_text()
    assert "callback_url" in content
    assert "cortex_entity_tag" in content
    assert "CORTEX_API_KEY" in content
    assert "CORTEX_BASE_URL" in content
    assert "/deploys" in content
    assert "post {" in content
    assert "always {" in content
    assert "CALLBACK_URL" in content


def test_workflow_yaml_is_valid():
    import yaml
    path = Path("cortexapps_cli/solutions/jenkins-deploy/_templates/trigger-jenkins-deploy.yaml")
    data = yaml.safe_load(path.read_text())
    assert data["tag"] == "jenkins-trigger-deploy"
    slugs = {a["slug"] for a in data["actions"]}
    assert slugs == {"get-jenkins-config", "parse-jenkins-config", "set-variables", "trigger-deploy"}
    root_actions = [a for a in data["actions"] if a["isRootAction"]]
    assert len(root_actions) == 1
    async_action = next(a for a in data["actions"] if a["slug"] == "trigger-deploy")
    assert async_action["schema"]["type"] == "HTTP_REQUEST_ASYNC"
    assert "buildWithParameters" in async_action["schema"]["url"]
    assert "@base64" in data["actions"][1]["schema"]["expression"]
