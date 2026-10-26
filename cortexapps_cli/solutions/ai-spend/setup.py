"""
Post-install setup script for the ai-spend solution.
Run via: cortex solutions post-install -s ai-spend
"""

SETUP_DESCRIPTION = (
    "The ai-spend solution installs custom metric definitions automatically. "
    "This post-install script confirms the setup is complete."
)

import sys
from pathlib import Path

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup


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

    def collect_prompts(self) -> None:
        pass

    def steps(self) -> list:
        return []

    def post_steps(self) -> None:
        print("\n✓ ai-spend solution is ready.\n")


def main(cortex_api_key=None, cortex_base_url=None, no_prompt=False, **kwargs):
    AiSpendSetup(
        cortex_api_key=cortex_api_key,
        cortex_base_url=cortex_base_url,
        no_prompt=no_prompt,
    ).run()


if __name__ == "__main__":
    main()
