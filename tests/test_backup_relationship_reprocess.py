"""
Tests for the two-pass relationship reprocessing logic in backup import.

Background: catalog entities are imported in alphabetical order. An entity early
in the alphabet (e.g. aaa-source) may reference a relationship destination
(e.g. zzz-target) that hasn't been created yet when aaa-source is first processed.
Pass 2 detects all entities with x-cortex-relationships and re-creates them after
all entities exist in the DB.

Wave 2 handles multi-tier hierarchies: if aaa-source depends on bbb-middle, AND
bbb-middle was also recreated in wave 1, then aaa-source needs a second re-create
after bbb-middle is stable.
"""
from tests.helpers.utils import *
import os
import tempfile


# Minimal entity YAML with no relationships (alphabetically last — stable destination)
ZZZ_TARGET_YAML = """\
openapi: 3.0.1
info:
  title: ZZZ Target
  x-cortex-tag: zzz-target
  x-cortex-type: service
"""

# Entity with a relationship to zzz-target (alphabetically first — processed before zzz-target in pass 1)
AAA_SOURCE_YAML = """\
openapi: 3.0.1
info:
  title: AAA Source
  x-cortex-tag: aaa-source
  x-cortex-type: service
  x-cortex-relationships:
    - tag: rel-to-zzz
      destinations:
        - tag: zzz-target
"""

# Middle entity with relationship to zzz-target (also re-created in wave 1)
BBB_MIDDLE_YAML = """\
openapi: 3.0.1
info:
  title: BBB Middle
  x-cortex-tag: bbb-middle
  x-cortex-type: service
  x-cortex-relationships:
    - tag: rel-to-zzz
      destinations:
        - tag: zzz-target
"""

# Entity with relationship to bbb-middle (which is itself a pass-2 entity → triggers wave 2)
AAA_DEPENDENT_YAML = """\
openapi: 3.0.1
info:
  title: AAA Dependent
  x-cortex-tag: aaa-dependent
  x-cortex-type: service
  x-cortex-relationships:
    - tag: rel-to-bbb
      destinations:
        - tag: bbb-middle
"""


def _make_backup_dir(tmpdir, files):
    """Create a backup directory structure with the given catalog YAML files."""
    catalog_dir = os.path.join(tmpdir, "catalog")
    os.makedirs(catalog_dir)
    for filename, content in files.items():
        with open(os.path.join(catalog_dir, filename), "w") as f:
            f.write(content)
    return tmpdir


def test_backup_import_triggers_pass2_for_relationship_entities(monkeypatch):
    """
    Pass 2 should run when catalog entities with x-cortex-relationships are present.
    aaa-source (has relationships) is processed before zzz-target (no relationships)
    in pass 1. Pass 2 must re-import aaa-source so its relationship is resolved.
    """
    monkeypatch.setenv("CORTEX_API_KEY", "invalidKey")

    with tempfile.TemporaryDirectory() as tmpdir:
        _make_backup_dir(tmpdir, {
            "aaa-source.yaml": AAA_SOURCE_YAML,
            "zzz-target.yaml": ZZZ_TARGET_YAML,
        })

        result = cli(["backup", "import", "-d", tmpdir], return_type=ReturnType.RAW)

        assert "Re-importing 1 entities with relationships" in result.stdout, (
            "Pass 2 should log that it is re-importing relationship entities"
        )


def test_backup_import_no_pass2_when_no_relationships(monkeypatch):
    """
    Pass 2 should not run when no catalog entities have x-cortex-relationships.
    """
    monkeypatch.setenv("CORTEX_API_KEY", "invalidKey")

    with tempfile.TemporaryDirectory() as tmpdir:
        _make_backup_dir(tmpdir, {
            "zzz-target.yaml": ZZZ_TARGET_YAML,
        })

        result = cli(["backup", "import", "-d", tmpdir], return_type=ReturnType.RAW)

        assert "Re-importing" not in result.stdout, (
            "Pass 2 should not run when no entities have relationships"
        )


def test_backup_import_triggers_wave2_for_dependent_relationships(monkeypatch):
    """
    Wave 2 of pass 2 should run when an entity's relationship destination is itself
    being re-created in wave 1.

    aaa-dependent → bbb-middle → zzz-target

    bbb-middle is in wave 1 (has relationships). aaa-dependent's destination (bbb-middle)
    is also a pass-2 entity, so aaa-dependent must be re-created in wave 2 after
    bbb-middle is stable.
    """
    monkeypatch.setenv("CORTEX_API_KEY", "invalidKey")

    with tempfile.TemporaryDirectory() as tmpdir:
        _make_backup_dir(tmpdir, {
            "aaa-dependent.yaml": AAA_DEPENDENT_YAML,
            "bbb-middle.yaml": BBB_MIDDLE_YAML,
            "zzz-target.yaml": ZZZ_TARGET_YAML,
        })

        result = cli(["backup", "import", "-d", tmpdir], return_type=ReturnType.RAW)

        # Wave 1 re-creates bbb-middle (2 relationship entities total)
        assert "Re-importing 2 entities with relationships" in result.stdout, (
            "Wave 1 of pass 2 should re-import all entities with relationships"
        )
        # Wave 2 re-creates aaa-dependent (its destination bbb-middle was in wave 1)
        assert "Re-importing" in result.stdout, (
            "Wave 2 of pass 2 should re-import entities whose destinations were recreated in wave 1"
        )
