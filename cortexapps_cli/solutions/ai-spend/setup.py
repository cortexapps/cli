"""
Post-install setup script for the ai-spend solution.
Creates the ai-spend custom metric definition in Cortex.
Run via: cortex solutions post-install -s ai-spend
"""

SETUP_DESCRIPTION = (
    "This solution includes a setup script that will create "
    "the 'ai-spend' custom metric definition in your Cortex instance."
)

import sys
from pathlib import Path
import requests

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

METRIC_PAYLOAD = {
    "key": "ai-spend",
    "name": "AI Spend",
    "valence": "POSITIVE",
    "category": "Cost",
    "description": "Weekly Claude AI spend per entity in USD",
}


class AiSpendSetup(SolutionSetup):
    solution_tag = "ai-spend"

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
        pass

    def _create_metric_definition(self) -> None:
        """Create the ai-spend metric definition via the Cortex API."""
        if self.already_done("create-definition"):
            return "Already created (skipped)"

        r = requests.post(
            f"{self._base_url}/api/v1/eng-intel/custom-metrics",
            headers=self._cortex_headers(),
            json=METRIC_PAYLOAD,
        )

        if r.status_code == 409:
            print("  ai-spend metric definition already exists, skipping")
            self.mark_done("create-definition")
            return

        r.raise_for_status()
        self.mark_done("create-definition")
        print("  ✓ Created ai-spend metric definition")

    def steps(self) -> list:
        return [
            ("Create ai-spend metric definition", self._create_metric_definition),
        ]

    def post_steps(self) -> None:
        print("\n✓ ai-spend metric definition is ready.\n")


def main(cortex_api_key=None, cortex_base_url=None, no_prompt=False, **kwargs):
    AiSpendSetup(
        cortex_api_key=cortex_api_key,
        cortex_base_url=cortex_base_url,
        no_prompt=no_prompt,
    ).run()


if __name__ == "__main__":
    main()
