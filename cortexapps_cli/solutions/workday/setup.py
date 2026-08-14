"""
Post-install setup script for the workday solution.
Configures the Cortex Workday integration to sync the Pied Piper org hierarchy.
Run via: cortex solutions post-install -s workday
"""

SETUP_DESCRIPTION = (
    "This solution includes a setup script that will configure "
    "the Cortex Workday integration to sync the Pied Piper org hierarchy."
)

import json
import sys
from pathlib import Path
import requests

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

DATA_DIR = Path(__file__).parent / "data"
CONFIG_FILE = DATA_DIR / "configuration.json"


class WorkdayIntegrationSetup(SolutionSetup):
    solution_tag = "workday"

    def __init__(
        self,
        cortex_api_key: str = None,
        cortex_base_url: str = None,
        no_prompt: bool = False,
        **kwargs,
    ):
        super().__init__(no_prompt=no_prompt, **kwargs)
        self._api_key = cortex_api_key or ""
        self._base_url = (cortex_base_url or "https://api.getcortexapp.com").rstrip("/")

    def _cortex_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def collect_prompts(self) -> None:
        pass  # credentials come from CLI session

    def _check_and_replace_existing(self) -> None:
        """Check for an existing Workday config; backup and delete it if user confirms."""
        r = requests.get(
            f"{self._base_url}/api/v1/workday/default-configuration",
            headers=self._cortex_headers(),
        )
        if r.status_code == 404:
            return  # no existing config — proceed
        r.raise_for_status()

        if not self.confirm("Existing Workday integration found. Replace it?", default=False):
            print("Keeping existing Workday integration. Exiting.")
            raise SystemExit(0)

        # Back up the existing config
        backup_dir = Path.home() / ".cortex" / "solutions" / "workday"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / "backup-config.json"
        backup_file.write_text(json.dumps(r.json(), indent=2))
        print(f"  Backed up existing config to {backup_file}")

        # Delete the existing config
        del_r = requests.delete(
            f"{self._base_url}/api/v1/workday/configurations",
            headers=self._cortex_headers(),
        )
        del_r.raise_for_status()

    def _configure_integration(self) -> None:
        """POST the bundled Workday integration configuration."""
        if self.already_done("configure"):
            return "Already configured (skipped)"
        config = json.loads(CONFIG_FILE.read_text())
        print(f"  (cortex integrations workday add -f {CONFIG_FILE})")
        r = requests.post(
            f"{self._base_url}/api/v1/workday/configuration",
            headers=self._cortex_headers(),
            json=config,
        )
        if not r.ok:
            raise RuntimeError(
                f"Failed to configure Workday integration: {r.status_code} {r.text}"
            )
        self.mark_done("configure")

    def steps(self) -> list:
        return [
            ("Check for existing Workday integration", self._check_and_replace_existing),
            ("Configure Workday integration", self._configure_integration),
        ]

    def post_steps(self) -> None:
        print("\n✓ Workday integration configured with the Pied Piper org hierarchy.\n")
        print("Next: trigger the import in Cortex:")
        print("  Catalog → All Entities → Import Entities\n")
        print("Then check your team hierarchy to see the Pied Piper org chart.")


def main(cortex_api_key=None, cortex_base_url=None, no_prompt=False, **kwargs):
    WorkdayIntegrationSetup(
        cortex_api_key=cortex_api_key,
        cortex_base_url=cortex_base_url,
        no_prompt=no_prompt,
    ).run()


if __name__ == "__main__":
    main()
