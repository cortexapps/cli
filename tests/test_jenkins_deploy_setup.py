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


@pytest.fixture
def mod():
    return load_setup_module()


@pytest.fixture
def setup(mod, tmp_path):
    instance = mod.JenkinsDeploySetup(state_dir=tmp_path)
    instance._answers = {
        "github_pat": "ghp_test",
        "jenkins_url": "http://jenkins.example.com:8080",
        "jenkins_username": "admin",
        "jenkins_token": "cortex-demo",
        "jenkins_job": "cortex-deploy",
        "entity_tag": "jenkins-demo",
        "cortex_api_key": "crt_testkey",
        "cortex_base_url": "https://api.getcortexapp.com",
    }
    return instance


def test_create_codespace_returns_name(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=201)
    resp.json.return_value = {"name": "cortexapps-cli-abc123"}
    with patch("requests.post", return_value=resp):
        name = setup._create_codespace()
    assert name == "cortexapps-cli-abc123"


def test_create_codespace_raises_on_failure(setup):
    from unittest.mock import patch, MagicMock
    import pytest
    resp = MagicMock(status_code=422)
    resp.text = "Unprocessable Entity"
    with patch("requests.post", return_value=resp):
        with pytest.raises(RuntimeError, match="Failed to create Codespace"):
            setup._create_codespace()


def test_expose_jenkins_port_returns_url(setup):
    from unittest.mock import patch, MagicMock
    post_resp = MagicMock(status_code=201)
    patch_resp = MagicMock(status_code=200)
    with patch("requests.post", return_value=post_resp), \
         patch("requests.patch", return_value=patch_resp):
        url = setup._expose_jenkins_port("my-codespace-abc")
    assert url == "https://my-codespace-abc-8080.app.github.dev"


def test_codespace_exists_returns_true_on_200(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=resp):
        assert setup._codespace_exists("my-cs") is True


def test_codespace_exists_returns_false_on_404(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=404)
    with patch("requests.get", return_value=resp):
        assert setup._codespace_exists("my-cs") is False


def test_wait_for_codespace_polls_until_available(setup):
    from unittest.mock import patch, MagicMock
    pending = MagicMock(status_code=200)
    pending.json.return_value = {"state": "Starting"}
    ready = MagicMock(status_code=200)
    ready.json.return_value = {"state": "Available"}
    with patch("requests.get", side_effect=[pending, ready]), \
         patch("time.sleep"):
        setup._wait_for_codespace("my-codespace-abc")  # should not raise


def test_jenkins_auth(setup):
    assert setup._jenkins_auth() == ("admin", "cortex-demo")


def test_wait_for_jenkins_polls_until_200(setup):
    from unittest.mock import patch, MagicMock
    fail = MagicMock(status_code=503)
    ok = MagicMock(status_code=200)
    with patch("requests.get", side_effect=[fail, ok]), \
         patch("time.sleep"):
        setup._wait_for_jenkins()  # should not raise


def test_create_jenkins_job_skips_if_exists(setup):
    from unittest.mock import patch, MagicMock
    exists_resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=exists_resp) as mock_get, \
         patch("requests.post") as mock_post:
        setup._create_jenkins_job()
    mock_get.assert_called_once()
    mock_post.assert_not_called()


def test_create_jenkins_job_creates_when_missing(setup):
    from unittest.mock import patch, MagicMock
    missing_resp = MagicMock(status_code=404)
    created_resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=missing_resp), \
         patch("requests.post", return_value=created_resp) as mock_post:
        setup._create_jenkins_job()
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "application/xml" in call_kwargs.kwargs.get("headers", {}).get("Content-Type", "")


def test_add_jenkins_credential_skips_if_exists(setup):
    from unittest.mock import patch, MagicMock
    exists_resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=exists_resp) as mock_get, \
         patch("requests.post") as mock_post:
        setup._add_jenkins_credential("CORTEX_API_KEY", "secret", "Cortex API key")
    mock_get.assert_called_once()
    mock_post.assert_not_called()


def test_add_jenkins_credential_creates_when_missing(setup):
    from unittest.mock import patch, MagicMock
    missing_resp = MagicMock(status_code=404)
    created_resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=missing_resp), \
         patch("requests.post", return_value=created_resp) as mock_post:
        setup._add_jenkins_credential("CORTEX_API_KEY", "secret", "Cortex API key")
    mock_post.assert_called_once()


def test_write_entity_custom_metadata(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=200)
    with patch("requests.patch", return_value=resp) as mock_patch:
        setup._write_entity_custom_metadata()
    mock_patch.assert_called_once()
    call_kwargs = mock_patch.call_args
    assert "open-api" in call_kwargs.args[0]
    body = call_kwargs.kwargs["data"].decode()
    assert "jenkins-demo" in body
    assert "jenkins_url" not in body  # the value, not the key
    assert "http://jenkins.example.com:8080" in body
    assert "cortex-deploy" in body


def test_import_cortex_workflow(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=201)
    with patch("requests.post", return_value=resp) as mock_post:
        setup._import_cortex_workflow()
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "workflows" in call_kwargs.args[0]
    assert call_kwargs.kwargs["headers"]["Content-Type"] == "application/yaml"


def test_steps_returns_expected_list(setup):
    setup._answers["use_codespace"] = False
    step_labels = [label for label, _ in setup.steps()]
    assert "Creating Jenkins deploy job" in step_labels
    assert "Adding CORTEX_API_KEY credential to Jenkins" in step_labels
    assert "Adding CORTEX_BASE_URL credential to Jenkins" in step_labels
    assert "Writing Jenkins config to entity custom metadata" in step_labels
    assert "Importing Cortex trigger workflow" in step_labels


def test_steps_includes_codespace_when_enabled(setup):
    setup._answers["use_codespace"] = True
    step_labels = [label for label, _ in setup.steps()]
    assert "Provisioning Jenkins in GitHub Codespaces" in step_labels


def test_main_callable(mod):
    assert callable(mod.main)


def test_delete_codespace_succeeds(setup):
    from unittest.mock import patch, MagicMock
    setup._state["codespace_name"] = "my-cs-abc"
    resp = MagicMock(status_code=204)
    with patch("requests.delete", return_value=resp):
        setup._delete_codespace("my-cs-abc")
    assert "codespace_name" not in setup._state


def test_delete_codespace_raises_on_failure(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=422)
    resp.text = "Error"
    with patch("requests.delete", return_value=resp):
        with pytest.raises(RuntimeError, match="Failed to delete Codespace"):
            setup._delete_codespace("my-cs-abc")


def test_provision_codespace_stores_name_in_state(setup):
    from unittest.mock import patch, MagicMock
    create_resp = MagicMock(status_code=201)
    create_resp.json.return_value = {"name": "my-cs-abc"}
    patch_resp = MagicMock(status_code=200)
    with patch("requests.post", return_value=create_resp), \
         patch("requests.get", return_value=MagicMock(status_code=200, json=lambda: {"state": "Available"})), \
         patch("requests.patch", return_value=patch_resp), \
         patch("time.sleep"):
        setup._provision_codespace()
    assert setup._state.get("codespace_name") == "my-cs-abc"
