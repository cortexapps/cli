import json
from pathlib import Path

DATA_DIR = Path("cortexapps_cli/solutions/workday-integration/data")
REPORT_URL = (
    "https://raw.githubusercontent.com/cortexapps/cli/main"
    "/cortexapps_cli/solutions/workday-integration/data/pied-piper-hierarchy.json"
)


def test_hierarchy_json_is_valid():
    data = json.loads((DATA_DIR / "pied-piper-hierarchy.json").read_text())
    assert "Report_Entry" in data
    assert len(data["Report_Entry"]) == 7


def test_hierarchy_has_root_employee():
    data = json.loads((DATA_DIR / "pied-piper-hierarchy.json").read_text())
    roots = [e for e in data["Report_Entry"] if e["managersEmail"] == e["email"]]
    assert len(roots) == 1
    assert roots[0]["email"] == "erlich.bachman@piedpiper.com"


def test_hierarchy_has_root_team():
    data = json.loads((DATA_DIR / "pied-piper-hierarchy.json").read_text())
    roots = [e for e in data["Report_Entry"] if e["parentTeamId"] == "NONE"]
    assert len(roots) == 1
    assert roots[0]["teamId"] == "WORKTEAM-1-000"


def test_hierarchy_required_fields():
    data = json.loads((DATA_DIR / "pied-piper-hierarchy.json").read_text())
    required = {"email", "employeeId", "firstName", "lastName", "managersEmail",
                "teamId", "teamName", "parentTeamId"}
    for entry in data["Report_Entry"]:
        assert required <= entry.keys(), f"Missing fields in entry: {entry}"


def test_configuration_json_is_valid():
    config = json.loads((DATA_DIR / "configuration.json").read_text())
    assert config["ownershipReportUrl"] == REPORT_URL
    assert config["reportMappingV2"]["type"] == "ONE_EMPLOYEE_ONE_TEAM"
    assert "password" in config
    assert "username" in config


def test_configuration_mapping_fields():
    config = json.loads((DATA_DIR / "configuration.json").read_text())
    mapping = config["reportMappingV2"]
    assert mapping["email"]["columnName"] == "email"
    assert mapping["managerEmail"]["columnName"] == "managersEmail"
    ff = mapping["fallbackFields"]
    assert ff["fieldOnParentNode"]["columnName"] == "teamId"
    assert ff["fieldOnChildNode"]["columnName"] == "parentTeamId"
