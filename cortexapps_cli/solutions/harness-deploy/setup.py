"""
Post-install setup script for the harness-deploy solution.
Wires up Harness credentials, creates the pipeline and secret in Harness,
imports the Cortex async workflow, and optionally triggers a test run.
Run via: cortex solutions post-install -s harness-deploy
"""

SETUP_DESCRIPTION = (
    "This solution includes a post-install setup script that will configure your Harness "
    "integration in Cortex, create the deploy pipeline and cortex_api_key secret in Harness, "
    "import the Cortex trigger workflow, and optionally fire a test deploy."
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

HARNESS_APP_HOST = "https://app.harness.io"


def _hyperlink(url: str, text: str = None) -> str:
    label = text if text is not None else url
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"


class HarnessDeploySetup(SolutionSetup):
    solution_tag = "harness-deploy"

    def __init__(self, cortex_api_key: str = None, cortex_base_url: str = None, **kwargs):
        super().__init__(**kwargs)
        self._session_api_key = cortex_api_key
        self._session_base_url = cortex_base_url

    # ── Harness API helpers ────────────────────────────────────────────────

    def _harness_headers(self) -> dict:
        return {"x-api-key": self._answers["harness_api_key"]}

    def _harness_base(self) -> str:
        return (self._answers.get("harness_host") or HARNESS_APP_HOST).rstrip("/")

    def _harness_account(self) -> str:
        return self._answers["harness_account_id"]

    def _fetch_harness_account_id(self) -> str | None:
        """Derive account ID from the first Harness configuration registered in Cortex."""
        integrations = self._fetch_harness_integrations()
        for cfg in integrations:
            acct = cfg.get("accountId") or cfg.get("account_id")
            if acct:
                return acct
        return None

    # ── Cortex API helpers ─────────────────────────────────────────────────

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
                if isinstance(data, list):
                    return data
                return data.get("configurations", data.get("items", []))
        except Exception:
            pass
        return []

    def _select_harness_integration(self, integrations: list) -> tuple[str, dict]:
        """Return (alias, config_dict) for the chosen integration."""
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
                idx = default_idx
            else:
                try:
                    idx = int(choice) - 1
                except ValueError:
                    idx = -1
            if 0 <= idx < len(integrations):
                cfg = integrations[idx]
                return cfg["alias"], cfg
            print(f"  Enter a number between 1 and {len(integrations)}")

    # ── Prompts ────────────────────────────────────────────────────────────

    def _create_cortex_harness_integration(self) -> str:
        """Prompt for Harness credentials and register them in Cortex. Returns the alias."""
        base_url = (self._session_base_url or "https://api.getcortexapp.com").rstrip("/")
        api_key = self._session_api_key or self._answers.get("cortex_api_key", "")

        print("\nNo Harness integration is configured in Cortex. Let's set one up.")
        self.prompt("harness_integration_alias", "Integration alias", default="default")
        self.prompt(
            "harness_api_key",
            "Harness API key",
            env_var="HARNESS_API_KEY",
            secret=True,
        )
        self.prompt("harness_account_id", "Harness account ID")
        self.prompt(
            "harness_host",
            "Harness host URL (leave blank for https://app.harness.io)",
            default="",
        )

        payload = {
            "alias": self._answers["harness_integration_alias"],
            "apiKey": self._answers["harness_api_key"],
            "accountId": self._answers["harness_account_id"],
            "isDefault": True,
        }
        if self._answers.get("harness_host"):
            payload["host"] = self._answers["harness_host"]

        resp = requests.post(
            f"{base_url}/api/v1/harness/configuration",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Failed to create Harness integration in Cortex: {resp.status_code} {resp.text}"
            )
        print(f"  Harness integration '{self._answers['harness_integration_alias']}' created \u2713")
        return self._answers["harness_integration_alias"]

    def collect_prompts(self) -> None:
        # 1. Harness integration alias (from Cortex config, or create one)
        integrations = self._fetch_harness_integrations()
        if integrations:
            alias, cfg = self._select_harness_integration(integrations)
            self._answers["harness_integration_alias"] = alias
            # Capture account ID and host if the config exposes them
            if cfg.get("accountId"):
                self._answers["harness_account_id"] = cfg["accountId"]
            if cfg.get("host"):
                self._answers["harness_host"] = cfg["host"].rstrip("/")
        else:
            alias = self._create_cortex_harness_integration()
            self._answers["harness_integration_alias"] = alias

        # 2. Harness API key — only prompt if we didn't already collect it above
        if not self._answers.get("harness_api_key"):
            self.prompt(
                "harness_api_key",
                "Harness API key (for creating the pipeline and secret in your project)",
                env_var="HARNESS_API_KEY",
                secret=True,
            )

        # 3. Account ID — only prompt if not already captured from the integration config
        if not self._answers.get("harness_account_id"):
            derived = self._fetch_harness_account_id()
            self.prompt("harness_account_id", "Harness account ID", default=derived)

        # 4. Pipeline coordinates
        self.prompt("harness_org", "Harness org identifier", default="default")
        self.prompt("harness_project", "Harness project identifier", default="default_project")
        self.prompt(
            "harness_pipeline",
            "Harness pipeline identifier (will be created if it doesn't exist)",
            default="cortex_deploy",
        )

        # 5. Cortex entity to record deploys against
        self.prompt("entity_tag", "Cortex entity tag to record deploys against", default="harness-demo")

        # 6. Cortex credentials
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

    # ── Steps ──────────────────────────────────────────────────────────────

    def steps(self) -> list[tuple[str, callable]]:
        return [
            ("Creating Harness pipeline", self._create_harness_pipeline),
            ("Creating cortex_api_key secret in Harness", self._create_harness_secret),
            ("Importing Cortex trigger workflow", self._import_cortex_workflow),
        ]

    def post_steps(self) -> None:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        entity_tag = self._answers["entity_tag"]
        cortex_url = f"{app_url}/admin/resources?tag={entity_tag}"

        harness_pipeline_url = (
            f"{self._harness_base()}/ng/account/{self._harness_account()}"
            f"/cd/orgs/{self._answers['harness_org']}"
            f"/projects/{self._answers['harness_project']}"
            f"/pipelines/{self._answers['harness_pipeline']}/executions"
        )

        print()
        if self.confirm("Trigger a test workflow run now?", default=True):
            print("  Starting Cortex workflow run (waiting for Harness pipeline to complete)...")
            try:
                result = self._trigger_via_cortex_workflow()
                status = result.get("status", "").upper()
                if status == "COMPLETED":
                    print("  Deploy complete \u2713")
                    print(f"  {_hyperlink(harness_pipeline_url, 'View pipeline runs in Harness')}")
                    self.mark_done("first_deploy")
                else:
                    print(f"  Workflow ended with status: {status}", file=sys.stderr)
            except Exception as e:
                print(f"  Trigger failed: {e}", file=sys.stderr)
                print(f"  Re-trigger via: cortex solutions post-install -s {self.solution_tag}", file=sys.stderr)

        print(f"\nDone! Watch your deploy appear at:")
        print(f"  {_hyperlink(cortex_url)}")
        print(f"\nHarness pipeline: {_hyperlink(harness_pipeline_url)}")

    # ── Harness pipeline creation ──────────────────────────────────────────

    def _create_harness_pipeline(self) -> None:
        org = self._answers["harness_org"]
        project = self._answers["harness_project"]
        pipeline_id = self._answers["harness_pipeline"]
        base = self._harness_base()

        # Check whether the pipeline already exists
        check = requests.get(
            f"{base}/v1/orgs/{org}/projects/{project}/pipelines/{pipeline_id}",
            headers=self._harness_headers(),
            timeout=10,
        )
        if check.status_code == 200:
            return  # already exists — leave it alone

        # Build pipeline YAML from template, substituting the pipeline identifier
        pipeline_yaml = (
            PIPELINE_TEMPLATE_PATH.read_text()
            .replace("identifier: cortex_deploy", f"identifier: {pipeline_id}")
            .replace("name: Cortex Deploy", f"name: Cortex Deploy")
        )

        resp = requests.post(
            f"{base}/v1/orgs/{org}/projects/{project}/pipelines",
            headers={**self._harness_headers(), "Content-Type": "application/yaml"},
            data=pipeline_yaml.encode("utf-8"),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Failed to create Harness pipeline: {resp.status_code} {resp.text}"
            )

    # ── Harness secret creation ────────────────────────────────────────────

    def _create_harness_secret(self) -> None:
        """Create a cortex_api_key text secret in the Harness project."""
        account_id = self._harness_account()
        org = self._answers["harness_org"]
        project = self._answers["harness_project"]
        base = self._harness_base()
        cortex_key = self._answers["cortex_api_key"]

        # Check if secret already exists
        check = requests.get(
            f"{base}/ng/api/v2/secrets/cortex_api_key",
            params={
                "accountIdentifier": account_id,
                "orgIdentifier": org,
                "projectIdentifier": project,
            },
            headers=self._harness_headers(),
            timeout=10,
        )
        if check.status_code == 200:
            return  # already exists

        payload = {
            "secret": {
                "type": "SecretText",
                "name": "cortex_api_key",
                "identifier": "cortex_api_key",
                "orgIdentifier": org,
                "projectIdentifier": project,
                "spec": {
                    "secretManagerIdentifier": "harnessSecretManager",
                    "valueType": "Inline",
                    "value": cortex_key,
                },
            }
        }
        resp = requests.post(
            f"{base}/ng/api/v2/secrets/text",
            params={
                "accountIdentifier": account_id,
                "orgIdentifier": org,
                "projectIdentifier": project,
            },
            headers=self._harness_headers(),
            json=payload,
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Failed to create Harness secret: {resp.status_code} {resp.text}"
            )

    # ── Cortex workflow import ─────────────────────────────────────────────

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

    # ── Cortex workflow trigger ────────────────────────────────────────────

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
