"""
Post-install setup script for the harness-deploy solution.
Wires up Harness credentials, creates the pipeline and secret in Harness,
imports the Cortex async workflow, and optionally triggers a test run.
Run via: cortex solutions post-install -s harness-deploy
"""

SETUP_DESCRIPTION = (
    "This solution includes a setup script that will configure your Harness "
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
RECORD_DEPLOY_TEMPLATE_PATH = Path(__file__).parent / "_templates" / "cortex-record-deploy-template.yaml"
CALLBACK_TEMPLATE_PATH = Path(__file__).parent / "_templates" / "cortex-async-callback-template.yaml"

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
            hidden=True,
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
        if self._no_prompt and self._answers.get("harness_integration_alias"):
            pass  # use saved alias — no need to re-fetch or re-select
        else:
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
                hidden=True,
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

        # 6. Cortex credentials — use CLI session silently; only prompt when running standalone
        self._secret_keys.add("cortex_api_key")
        if self._session_api_key:
            self._answers["cortex_api_key"] = self._session_api_key
        else:
            self.prompt("cortex_api_key", "Cortex API key", env_var="CORTEX_API_KEY", secret=True)

        if self._session_base_url:
            self._answers["cortex_base_url"] = self._session_base_url
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
            ("Creating Cortex Record Deploy stage template", self._create_record_deploy_template),
            ("Creating Cortex Async Callback stage template", self._create_async_callback_template),
            ("Creating Harness pipeline", self._create_harness_pipeline),
            ("Creating cortex_api_key secret in Harness", self._create_harness_secret),
            ("Writing Harness config to entity custom metadata", self._write_entity_custom_metadata),
            ("Importing Cortex trigger workflow", self._import_cortex_workflow),
        ]

    def post_steps(self) -> None:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        entity_tag = self._answers["entity_tag"]
        cortex_url = f"{app_url}/admin/service/{entity_tag}"

        harness_pipeline_url = (
            f"{self._harness_base()}/ng/account/{self._harness_account()}"
            f"/cd/orgs/{self._answers['harness_org']}"
            f"/projects/{self._answers['harness_project']}"
            f"/pipelines/{self._answers['harness_pipeline']}/executions"
        )

        workflow_tag = "harness-trigger-deploy"
        workflows_url = f"{app_url}/admin/workflows"
        entity_url = cortex_url

        print(f"\nTo trigger a deploy manually later:")
        print(f"  CLI: cortex workflows run -t {workflow_tag} --scope ENTITY --entity {entity_tag}")
        print(f"  UI:  {_hyperlink(entity_url, entity_tag)} \u2192 Workflows tab \u2192 Solution: Trigger Harness Deploy \u2192 Run")

        print(f"\n{_hyperlink(workflows_url, 'View workflows in Cortex')}")
        if self.confirm("Trigger a test workflow run now?", default=True):
            print("  Starting Cortex workflow run (waiting for Harness pipeline to complete)...")
            try:
                result = self._trigger_via_cortex_workflow()
                status = result.get("status", "").upper()
                if status == "COMPLETED":
                    print(f"  Workflow run complete \u2713")
                    print(f"  {_hyperlink(harness_pipeline_url, 'View pipeline runs in Harness')}")
                    self._confirm_deploy_recorded(base_url, entity_tag, cortex_url)
                    self.mark_done("first_deploy")
                else:
                    print(f"  Workflow run ended with status: {status}", file=sys.stderr)
                    print(f"  Check {_hyperlink(workflows_url, 'Cortex Workflow runs')} to investigate the cause of the failure.", file=sys.stderr)
            except Exception as e:
                print(f"  Trigger failed: {e}", file=sys.stderr)
                print(f"  Re-trigger via: cortex solutions post-install -s {self.solution_tag}", file=sys.stderr)

        print(f"\nDone! Watch your deploy appear at:")
        print(f"  {_hyperlink(cortex_url)}")
        print(f"\nHarness pipeline: {_hyperlink(harness_pipeline_url)}")

    def _confirm_deploy_recorded(self, base_url: str, entity_tag: str, entity_url: str) -> None:
        """Verify the deploy was written to Cortex and print a confirmation hyperlink."""
        api_key = self._answers["cortex_api_key"]
        try:
            resp = requests.get(
                f"{base_url}/api/v1/catalog/{entity_tag}/deploys",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"pageSize": 1},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                deploys = data if isinstance(data, list) else data.get("deploys", [])
                if deploys:
                    print(f"  Deploy recorded on entity \u2713  {_hyperlink(entity_url, entity_tag)}")
                    return
        except Exception:
            pass
        print(f"  Deploy may still be indexing — check {_hyperlink(entity_url, entity_tag)}")

    # ── Harness pipeline creation ──────────────────────────────────────────

    def _create_stage_template(self, identifier: str, name: str, template_path) -> None:
        org = self._answers["harness_org"]
        project = self._answers["harness_project"]
        base = self._harness_base()
        headers = {**self._harness_headers(), "Content-Type": "application/json"}

        template_yaml = (
            template_path.read_text()
            .replace("orgIdentifier: default", f"orgIdentifier: {org}")
            .replace("projectIdentifier: default_project", f"projectIdentifier: {project}")
        )
        body = {
            "identifier": identifier,
            "name": name,
            "version_label": "1.0",
            "template_yaml": template_yaml,
        }
        url_base = f"{base}/v1/orgs/{org}/projects/{project}/templates"

        exists = requests.get(
            f"{url_base}/{identifier}",
            params={"version_label": "1.0"},
            headers=self._harness_headers(),
            timeout=10,
        )
        if exists.status_code == 200:
            return  # already exists — leave it alone
        resp = requests.post(url_base, headers=headers, json=body, timeout=15)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to create stage template '{name}': {resp.status_code} {resp.text}")

    def _create_record_deploy_template(self) -> None:
        self._create_stage_template("cortex_record_deploy", "Cortex Record Deploy", RECORD_DEPLOY_TEMPLATE_PATH)

    def _create_async_callback_template(self) -> None:
        self._create_stage_template("cortex_async_callback", "Cortex Async Callback", CALLBACK_TEMPLATE_PATH)

    def _create_harness_pipeline(self) -> None:
        org = self._answers["harness_org"]
        project = self._answers["harness_project"]
        pipeline_id = self._answers["harness_pipeline"]
        base = self._harness_base()

        pipeline_name = "Cortex Deploy"
        pipeline_yaml = (
            PIPELINE_TEMPLATE_PATH.read_text()
            .replace("identifier: cortex_deploy", f"identifier: {pipeline_id}")
            .replace("name: Cortex Deploy\n", f"name: {pipeline_name}\n")
        )
        body = {"identifier": pipeline_id, "name": pipeline_name, "pipeline_yaml": pipeline_yaml}
        headers = {**self._harness_headers(), "Content-Type": "application/json"}
        url_base = f"{base}/v1/orgs/{org}/projects/{project}/pipelines"

        exists = requests.get(f"{url_base}/{pipeline_id}", headers=self._harness_headers(), timeout=10)
        if exists.status_code == 200:
            resp = requests.put(f"{url_base}/{pipeline_id}", headers=headers, json=body, timeout=15)
            if resp.status_code not in (200, 201):
                raise RuntimeError(f"Failed to update Harness pipeline: {resp.status_code} {resp.text}")
        else:
            resp = requests.post(url_base, headers=headers, json=body, timeout=15)
            if resp.status_code not in (200, 201):
                raise RuntimeError(f"Failed to create Harness pipeline: {resp.status_code} {resp.text}")

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

    # ── Cortex entity custom metadata ─────────────────────────────────────

    def _write_entity_custom_metadata(self) -> None:
        """Patch the entity YAML with Harness coordinates in x-cortex-custom-metadata."""
        base_url = self._answers["cortex_base_url"].rstrip("/")
        entity_tag = self._answers["entity_tag"]
        yaml_content = f"""\
openapi: "3.0.0"
info:
  title: Harness Demo
  x-cortex-tag: {entity_tag}
  x-cortex-custom-metadata:
    harness:
      org: "{self._answers['harness_org']}"
      project: "{self._answers['harness_project']}"
      pipeline: "{self._answers['harness_pipeline']}"
"""
        resp = requests.patch(
            f"{base_url}/api/v1/open-api",
            data=yaml_content.encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._answers['cortex_api_key']}",
                "Content-Type": "application/openapi;charset=UTF-8",
            },
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to write entity custom metadata: {resp.status_code} {resp.text}")

    # ── Cortex workflow import ─────────────────────────────────────────────

    def _import_cortex_workflow(self) -> None:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        api_key = self._answers["cortex_api_key"]
        alias = self._answers["harness_integration_alias"]

        yaml_content = (
            WORKFLOW_TEMPLATE_PATH.read_text()
            .replace("PLACEHOLDER_INTEGRATION_ALIAS", alias)
            .replace("PLACEHOLDER_HARNESS_ACCOUNT_ID", self._answers.get("harness_account_id", ""))
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
            "scope": {"type": "ENTITY", "entityId": self._answers["entity_tag"]},
            "initialContext": {},
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
