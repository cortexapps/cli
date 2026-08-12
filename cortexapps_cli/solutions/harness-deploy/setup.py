"""
Post-install setup script for the harness-deploy solution.
Wires up Harness credentials, imports the Cortex async workflow, and optionally triggers a test run.
Run via: cortex solutions post-install -s harness-deploy
"""

SETUP_DESCRIPTION = (
    "This solution includes a post-install setup script that will configure your Harness "
    "integration in Cortex, import the trigger workflow, and optionally fire a test deploy."
)

import sys
import time
from pathlib import Path

import requests

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

WORKFLOW_TEMPLATE_PATH = Path(__file__).parent / "_templates" / "trigger-harness-deploy.yaml"
PIPELINE_TEMPLATE_PATH = Path(__file__).parent / "_templates" / "cortex-deploy-pipeline.yaml"


def _hyperlink(url: str, text: str = None) -> str:
    label = text if text is not None else url
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"


class HarnessDeploySetup(SolutionSetup):
    solution_tag = "harness-deploy"

    def __init__(self, cortex_api_key: str = None, cortex_base_url: str = None, **kwargs):
        super().__init__(**kwargs)
        self._session_api_key = cortex_api_key
        self._session_base_url = cortex_base_url

    def _cortex_headers(self) -> dict:
        api_key = self._answers.get("cortex_api_key") or self._session_api_key or ""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _fetch_harness_integrations(self) -> list:
        if not (self._session_api_key and self._session_base_url):
            return []
        try:
            resp = requests.get(
                f"{self._session_base_url.rstrip('/')}/api/v1/harness/configurations",
                headers={"Authorization": f"Bearer {self._session_api_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                # Configurations may be a list or wrapped in a key
                if isinstance(data, list):
                    return data
                return data.get("configurations", data.get("items", []))
        except Exception:
            pass
        return []

    def _select_harness_integration(self, integrations: list) -> str:
        integrations = sorted(integrations, key=lambda c: c.get("alias", "").lower())
        default_idx = next(
            (i for i, c in enumerate(integrations) if c.get("isDefault")), 0
        )
        print("\nHarness integrations configured in Cortex:")
        for i, cfg in enumerate(integrations):
            marker = " *" if cfg.get("isDefault") else "  "
            print(f"  {marker}{i + 1}. {cfg['alias']}")
        print("   (* = default)")

        while True:
            choice = input(f"\nSelect integration [{default_idx + 1}]: ").strip()
            if not choice:
                return integrations[default_idx]["alias"]
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(integrations):
                    return integrations[idx]["alias"]
            except ValueError:
                pass
            print(f"  Enter a number between 1 and {len(integrations)}")

    def collect_prompts(self) -> None:
        # 1. Harness integration alias
        integrations = self._fetch_harness_integrations()
        if integrations:
            alias = self._select_harness_integration(integrations)
            self._answers["harness_integration_alias"] = alias
        else:
            if self._session_api_key and self._session_base_url:
                print("\nNo Harness integration is configured in Cortex.")
                print("Configure one at: Settings → Integrations → Harness")
                print("Then re-run: cortex solutions post-install -s harness-deploy")
                sys.exit(0)
            self.prompt("harness_integration_alias", "Harness integration alias", default="default")

        # 2. Harness pipeline coordinates
        self.prompt("harness_org", "Harness org identifier", default="default")
        self.prompt("harness_project", "Harness project identifier", default="default_project")
        self.prompt("harness_pipeline", "Harness pipeline identifier (the pipeline to trigger)")

        # 3. Cortex entity to record deploys against
        self.prompt("entity_tag", "Cortex entity tag to record deploys against", default="harness-demo")

        # 4. Cortex credentials
        if self._session_api_key:
            if self.confirm("Use current Cortex API key?", default=True):
                self._answers["cortex_api_key"] = self._session_api_key
            else:
                self.prompt("cortex_api_key", "Cortex API key", secret=True)
        else:
            self.prompt("cortex_api_key", "Cortex API key", env_var="CORTEX_API_KEY", secret=True)

        if self._session_base_url:
            if self.confirm(f"Use current Cortex base URL [{self._session_base_url}]?", default=True):
                self._answers["cortex_base_url"] = self._session_base_url
            else:
                self.prompt("cortex_base_url", "Cortex base URL", default=self._session_base_url)
        else:
            self.prompt(
                "cortex_base_url",
                "Cortex base URL",
                env_var="CORTEX_BASE_URL",
                default="https://api.getcortexapp.com",
            )

    def steps(self) -> list[tuple[str, callable]]:
        return [
            ("Importing Cortex trigger workflow", self._import_cortex_workflow),
        ]

    def post_steps(self) -> None:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        entity_tag = self._answers["entity_tag"]
        cortex_url = f"{app_url}/admin/resources?tag={entity_tag}"
        pipeline_template_path = PIPELINE_TEMPLATE_PATH

        print()
        print("Next step: import the Harness pipeline template into your Harness project.")
        print(f"  Pipeline YAML: {pipeline_template_path}")
        print()
        print("  In Harness: Pipelines → Import Pipeline → paste or upload the YAML above.")
        print("  Add a 'cortex_api_key' secret to your Harness project for the callback to authenticate.")
        print()

        if self.confirm("Trigger a test workflow run now?", default=True):
            print("  Starting Cortex workflow run (waiting for Harness pipeline to complete)...")
            try:
                result = self._trigger_via_cortex_workflow()
                status = result.get("status", "").upper()
                if status == "COMPLETED":
                    print("  Deploy complete \u2713")
                    print(f"  {_hyperlink(cortex_url, 'View entity in Cortex')}")
                    self.mark_done("first_deploy")
                else:
                    print(f"  Workflow ended with status: {status}", file=sys.stderr)
            except Exception as e:
                print(f"  Trigger failed: {e}", file=sys.stderr)
                print(f"  Re-trigger via: cortex solutions post-install -s {self.solution_tag}", file=sys.stderr)

        print(f"\nDone! Watch your deploy appear at:")
        print(f"  {_hyperlink(cortex_url)}")

    def _import_cortex_workflow(self) -> None:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        api_key = self._answers["cortex_api_key"]
        alias = self._answers["harness_integration_alias"]

        yaml_content = WORKFLOW_TEMPLATE_PATH.read_text().replace(
            "PLACEHOLDER_INTEGRATION_ALIAS", alias
        )

        resp = requests.post(
            f"{base_url}/api/v1/workflows",
            data=yaml_content.encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/yaml",
            },
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Failed to import Cortex workflow: {resp.status_code} {resp.text}"
            )

    def _trigger_via_cortex_workflow(self) -> dict:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        api_key = self._answers["cortex_api_key"]
        cortex_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        workflow_tag = "harness-trigger-deploy"

        body = {
            "scope": {"type": "GLOBAL"},
            "initialContext": {
                "harness-org": self._answers["harness_org"],
                "harness-project": self._answers["harness_project"],
                "harness-pipeline": self._answers["harness_pipeline"],
                "entity-tag": self._answers["entity_tag"],
            },
        }
        resp = requests.post(
            f"{base_url}/api/v1/workflows/{workflow_tag}/runs",
            json=body,
            headers=cortex_headers,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to start workflow run: {resp.status_code} {resp.text}")

        run_id = resp.json().get("id")
        if not run_id:
            raise RuntimeError("No run ID returned from workflow start")

        terminal = {"COMPLETED", "FAILED", "CANCELLED"}
        start = time.time()
        dots = 0
        while time.time() - start < 360:
            time.sleep(5)
            r = requests.get(
                f"{base_url}/api/v1/workflows/{workflow_tag}/runs/{run_id}",
                headers=cortex_headers,
            )
            r.raise_for_status()
            status = r.json().get("status", "").upper()
            dots += 1
            print(f"\r  Waiting for Harness pipeline{'.' * (dots % 4)}   ", end="", flush=True)
            if status in terminal:
                print()
                return r.json()

        raise TimeoutError("Timed out waiting for workflow to complete (6 min)")


def main(**kwargs):
    HarnessDeploySetup(**kwargs).run()


if __name__ == "__main__":
    main()
