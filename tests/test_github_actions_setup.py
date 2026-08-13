import base64
import importlib.util
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def load_setup_module():
    spec = importlib.util.spec_from_file_location(
        "github_actions_setup",
        "cortexapps_cli/solutions/github-actions-deploy/setup.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return load_setup_module()


@pytest.fixture
def setup(mod, tmp_path):
    instance = mod.GitHubActionsSetup(state_dir=tmp_path)
    instance._answers = {
        "github_token": "ghp_test",
        "github_owner": "test-org",
        "repo_name": "cortex-deploy-demo",
        "cortex_api_key": "crt_testkey",
        "cortex_base_url": "https://api.getcortexapp.com",
    }
    return instance


def test_get_authenticated_user(setup):
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"login": "test-user"}
    with patch("requests.get", return_value=resp):
        assert setup._get_authenticated_user() == "test-user"


def test_create_repo_skips_if_exists(setup):
    resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=resp) as mock_get, \
         patch("requests.post") as mock_post:
        setup._create_repo()
    mock_get.assert_called_once()
    mock_post.assert_not_called()


def test_create_repo_creates_when_missing(setup):
    user_resp = MagicMock(status_code=200)
    user_resp.json.return_value = {"login": "test-org"}
    check_resp = MagicMock(status_code=404)
    post_resp = MagicMock(status_code=201)
    post_resp.json.return_value = {"html_url": "https://github.com/test-org/cortex-deploy-demo"}

    get_responses = [check_resp, user_resp]
    with patch("requests.get", side_effect=get_responses), \
         patch("requests.post", return_value=post_resp) as mock_post:
        setup._create_repo()
    mock_post.assert_called_once()


def test_create_repo_raises_on_unexpected_status(setup):
    resp = MagicMock(status_code=403)
    resp.text = "Forbidden"
    with patch("requests.get", return_value=resp), \
         patch("requests.post") as mock_post:
        with pytest.raises(RuntimeError, match="Unexpected status checking repo existence: 403"):
            setup._create_repo()
    mock_post.assert_not_called()


def test_seed_workflow_skips_if_unchanged(setup, tmp_path):
    # Read the actual template to simulate matching content
    template_path = Path("cortexapps_cli/solutions/github-actions-deploy/_templates/cortex-deploy.yml")
    content = template_path.read_text()
    content_b64 = base64.b64encode(content.encode()).decode()

    resp = MagicMock(status_code=200)
    resp.json.return_value = {"content": content_b64, "sha": "abc123"}

    with patch("requests.get", return_value=resp), \
         patch("requests.put") as mock_put:
        setup._seed_workflow()
    mock_put.assert_not_called()


def test_seed_workflow_creates_when_missing(setup):
    get_resp = MagicMock(status_code=404)
    put_resp = MagicMock(status_code=201)
    put_resp.json.return_value = {"content": {"sha": "abc123"}}

    with patch("requests.get", return_value=get_resp), \
         patch("requests.put", return_value=put_resp) as mock_put:
        setup._seed_workflow()
    mock_put.assert_called_once()


def test_set_secret(setup):
    # Valid Curve25519 public key (generated via nacl.public.PrivateKey.generate())
    from nacl.public import PrivateKey
    dummy_key = base64.b64encode(bytes(PrivateKey.generate().public_key)).decode()
    key_resp = MagicMock(status_code=200)
    key_resp.json.return_value = {"key_id": "key123", "key": dummy_key}
    key_resp.raise_for_status = MagicMock()

    put_resp = MagicMock(status_code=204)

    with patch("requests.get", return_value=key_resp), \
         patch("requests.put", return_value=put_resp) as mock_put:
        setup._set_secret("CORTEX_API_KEY", "crt_testkey")

    mock_put.assert_called_once()
    call_json = mock_put.call_args.kwargs["json"]
    assert "encrypted_value" in call_json
    assert call_json["key_id"] == "key123"


def test_trigger_workflow(setup):
    resp = MagicMock(status_code=204)
    with patch("requests.post", return_value=resp) as mock_post:
        setup._trigger_workflow()
    url = mock_post.call_args.args[0]
    assert "dispatches" in url
    assert mock_post.call_args.kwargs["json"] == {"ref": "main"}


def test_main_callable(mod):
    assert callable(mod.main)
