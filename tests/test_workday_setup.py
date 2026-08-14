import json
from pathlib import Path

DATA_DIR = Path("cortexapps_cli/solutions/workday/data")
REPORT_URL = "https://jeff-test-org.github.io/workday-mocks/pied-piper-supervisory-org"


def test_hierarchy_json_is_valid():
    data = json.loads((DATA_DIR / "pied-piper-supervisory-org.json").read_text())
    assert "Report_Entry" in data
    assert len(data["Report_Entry"]) == 7


def test_hierarchy_has_root_team():
    data = json.loads((DATA_DIR / "pied-piper-supervisory-org.json").read_text())
    all_teams = [team for entry in data["Report_Entry"] for team in entry["Workteam_Group"]]
    root_teams = {team["teamName"] for team in all_teams if team["parentTeamId"] == "NONE"}
    assert len(root_teams) == 1
    assert "PP: Pied Piper" in root_teams


def test_hierarchy_parent_child_links():
    data = json.loads((DATA_DIR / "pied-piper-supervisory-org.json").read_text())
    all_teams = [team for entry in data["Report_Entry"] for team in entry["Workteam_Group"]]
    team_names = {team["teamName"] for team in all_teams}
    for team in all_teams:
        if team["parentTeamId"] != "NONE":
            assert team["parentTeamId"] in team_names, (
                f"{team['teamName']}.parentTeamId={team['parentTeamId']!r} not found in any teamName"
            )


def test_hierarchy_required_fields():
    data = json.loads((DATA_DIR / "pied-piper-supervisory-org.json").read_text())
    required_top = {"Email", "Employee_ID", "First_Name", "Last_Name", "Workteam_Group"}
    required_team = {"teamName", "teamDisplayName", "parentTeamId"}
    for entry in data["Report_Entry"]:
        assert required_top <= entry.keys(), f"Missing top-level fields in entry: {entry}"
        assert isinstance(entry["Workteam_Group"], list), f"Workteam_Group must be a list in: {entry}"
        for team in entry["Workteam_Group"]:
            assert required_team <= team.keys(), f"Missing team fields in: {team}"


def test_configuration_json_is_valid():
    config = json.loads((DATA_DIR / "configuration.json").read_text())
    assert config["ownershipReportUrl"] == REPORT_URL
    assert config["reportMappingV2"]["type"] == "ONE_EMPLOYEE_MULTIPLE_TEAMS"
    assert "password" in config
    assert "username" in config


def test_configuration_mapping_fields():
    config = json.loads((DATA_DIR / "configuration.json").read_text())
    mapping = config["reportMappingV2"]
    assert mapping["email"]["columnName"] == "Email"
    assert mapping["employeeId"]["columnName"] == "Employee_ID"
    tlf = mapping["teamListFields"]
    assert tlf["teamListKey"]["columnName"] == "Workteam_Group"
    assert tlf["teamId"]["columnName"] == "teamName"
    assert tlf["hierarchy"]["fieldOnParentNode"]["columnName"] == "teamName"
    assert tlf["hierarchy"]["fieldOnChildNode"]["columnName"] == "parentTeamId"


import importlib.util
import pytest
from unittest.mock import patch, MagicMock


def load_setup_module():
    spec = importlib.util.spec_from_file_location(
        "workday_setup",
        "cortexapps_cli/solutions/workday/setup.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return load_setup_module()


@pytest.fixture
def setup(mod, tmp_path):
    return mod.WorkdayIntegrationSetup(
        cortex_api_key="crt_test",
        cortex_base_url="https://api.getcortexapp.com",
        state_dir=tmp_path,
    )


def test_solution_tag(mod):
    assert mod.WorkdayIntegrationSetup.solution_tag == "workday"


def test_setup_description(mod):
    assert "Workday" in mod.SETUP_DESCRIPTION


def test_collect_prompts_is_noop(setup):
    with patch("builtins.input", side_effect=AssertionError("should not prompt")):
        setup.collect_prompts()


def test_check_existing_no_config_proceeds(setup):
    resp_404 = MagicMock(status_code=404)
    resp_404.raise_for_status = MagicMock()
    setup.mark_done("configure")  # simulate stale cached state
    with patch("requests.get", return_value=resp_404):
        setup._check_and_replace_existing()
    assert not setup.already_done("configure")


def test_check_existing_user_declines_exits(setup):
    resp_200 = MagicMock(status_code=200)
    resp_200.raise_for_status = MagicMock()
    resp_200.json.return_value = {"username": "ISU_Cortex"}
    with patch("requests.get", return_value=resp_200), \
         patch("builtins.input", return_value="n"):
        with pytest.raises(SystemExit) as exc_info:
            setup._check_and_replace_existing()
        assert exc_info.value.code == 0


def test_check_existing_user_accepts_backs_up_and_deletes(setup, tmp_path):
    existing = {"username": "ISU_Cortex", "ownershipReportUrl": "https://old.example.com"}
    resp_200 = MagicMock(status_code=200)
    resp_200.raise_for_status = MagicMock()
    resp_200.json.return_value = existing
    resp_del = MagicMock(status_code=204)
    resp_del.raise_for_status = MagicMock()

    setup.mark_done("configure")
    assert setup.already_done("configure")

    with patch("requests.get", return_value=resp_200), \
         patch("requests.delete", return_value=resp_del) as mock_delete, \
         patch("builtins.input", return_value="y"), \
         patch("pathlib.Path.home", return_value=tmp_path):
        setup._check_and_replace_existing()

    mock_delete.assert_called_once()
    assert "configurations" in mock_delete.call_args.args[0]
    assert not setup.already_done("configure")

    backup_file = tmp_path / ".cortex" / "solutions" / "workday" / "backup-config.json"
    assert backup_file.exists()
    assert json.loads(backup_file.read_text()) == existing


def test_configure_integration_posts_correct_payload(setup):
    resp = MagicMock(ok=True, status_code=200)
    with patch("requests.post", return_value=resp) as mock_post:
        setup._configure_integration()

    mock_post.assert_called_once()
    url = mock_post.call_args.args[0]
    assert url.endswith("/api/v1/workday/configuration")

    payload = mock_post.call_args.kwargs["json"]
    assert payload["reportMappingV2"]["type"] == "ONE_EMPLOYEE_MULTIPLE_TEAMS"
    assert "pied-piper-supervisory-org" in payload["ownershipReportUrl"]


def test_configure_integration_raises_on_failure(setup):
    resp = MagicMock(ok=False, status_code=400, text="Bad Request")
    with patch("requests.post", return_value=resp):
        with pytest.raises(RuntimeError, match="Failed to configure"):
            setup._configure_integration()


def test_configure_integration_idempotent(setup, tmp_path):
    setup.mark_done("configure")
    with patch("requests.post") as mock_post:
        setup._configure_integration()
    mock_post.assert_not_called()


def test_validate_integration_success(setup, capsys):
    resp = MagicMock(ok=True, status_code=200)
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"configurations": [{"isValid": True, "alias": "default"}]}
    with patch("requests.post", return_value=resp):
        setup._validate_integration()
    assert "validated successfully" in capsys.readouterr().out


def test_validate_integration_raises_on_invalid(setup):
    resp = MagicMock(ok=True, status_code=200)
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"configurations": [{"isValid": False, "message": "404 from URL", "alias": "default"}]}
    with patch("requests.post", return_value=resp):
        with pytest.raises(RuntimeError, match="Validation failed: 404 from URL"):
            setup._validate_integration()


def test_validate_integration_raises_on_empty_result(setup):
    resp = MagicMock(ok=True, status_code=200)
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"configurations": []}
    with patch("requests.post", return_value=resp):
        with pytest.raises(RuntimeError, match="no results"):
            setup._validate_integration()


def test_steps_includes_validate(setup):
    labels = [s[0] for s in setup.steps()]
    assert "Validate Workday integration" in labels


def test_main_callable(mod):
    assert callable(mod.main)
