"""
Post-install setup script for the github-actions-deploy solution.
Creates and seeds a GitHub repo with the Cortex deploy workflow.
Run via: cortex solutions post-install -s github-actions-deploy
"""

SETUP_DESCRIPTION = (
    "This solution includes a post-install setup script that will create a GitHub "
    "repository, seed it with the Cortex deploy workflow, and configure the required secrets."
)
import base64
import os
import sys
from pathlib import Path
import requests
from nacl import encoding, public

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

GITHUB_API = "https://api.github.com"
TEMPLATE_PATH = Path(__file__).parent / "_templates" / "cortex-deploy.yml"
WORKFLOW_TEMPLATE_PATH = Path(__file__).parent / "_templates" / "github-actions-deploy.yaml"


def _hyperlink(url: str, text: str = None) -> str:
    """Return an OSC 8 hyperlink for terminals that support it (iTerm2, etc.)."""
    label = text if text is not None else url
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"


def _encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    """Encrypt a secret using the repo's libsodium public key."""
    pk = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


class GitHubActionsSetup(SolutionSetup):
    solution_tag = "github-actions-deploy"

    def __init__(self, cortex_api_key: str = None, cortex_base_url: str = None, no_prompt: bool = False, **kwargs):
        super().__init__(no_prompt=no_prompt, **kwargs)
        self._session_api_key = cortex_api_key
        self._session_base_url = cortex_base_url

    def _gh_headers(self) -> dict:
        token = self._answers.get("github_token") or os.environ.get("GITHUB_TOKEN", "")
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_authenticated_user(self) -> str:
        resp = requests.get(f"{GITHUB_API}/user", headers=self._gh_headers())
        resp.raise_for_status()
        return resp.json()["login"]

    def _fetch_github_integrations(self) -> list:
        """Fetch GitHub integrations configured in Cortex."""
        if not (self._session_api_key and self._session_base_url):
            return []
        try:
            resp = requests.get(
                f"{self._session_base_url.rstrip('/')}/api/v1/github/configurations",
                headers={"Authorization": f"Bearer {self._session_api_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("configurations", [])
        except Exception:
            pass
        return []

    def _select_github_integration(self, integrations: list) -> str:
        """Present a numbered list and return the chosen alias."""
        integrations = sorted(integrations, key=lambda c: c.get("alias", "").lower())
        saved_alias = self._answers.get("github_integration_alias")
        default_idx = next(
            (i for i, c in enumerate(integrations) if c.get("alias") == saved_alias),
            None,
        ) or next(
            (i for i, c in enumerate(integrations) if c.get("isDefault")), 0
        )
        print("\nGitHub integrations configured in Cortex:")
        for i, cfg in enumerate(integrations):
            marker = " *" if cfg.get("isDefault") else "  "
            type_label = cfg.get("type", "").replace("_", " ").title()
            print(f"  {marker}{i + 1}. {cfg['alias']} [{type_label}]")
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
        # 1. Check for GitHub integrations — prefer those over a raw token
        integrations = self._fetch_github_integrations()

        if integrations:
            alias = self._select_github_integration(integrations)
            self._answers["github_integration_alias"] = alias
            # Token still needed for the setup steps (create repo, seed, set secrets).
            # Pull from env var silently; no prompt when integration is configured.
            env_token = os.environ.get("GITHUB_TOKEN", "")
            if env_token:
                self._answers["github_token"] = env_token
            # If GITHUB_TOKEN is not set the setup steps will fail with a clear
            # error — user can export GITHUB_TOKEN and re-run post-install.
        else:
            # No integrations configured
            if self._session_api_key and self._session_base_url:
                print("\nNo GitHub integration is configured in Cortex.")
                if self.confirm("Set up a Personal Access Token (PAT) integration now?", default=True):
                    self.prompt("github_token", "GitHub Personal Access Token", env_var="GITHUB_TOKEN", secret=True)
                    self.prompt("github_integration_alias", "Integration alias", default="github-pat")
                    try:
                        self._create_github_pat_integration()
                        print(f"  Integration '{self._answers['github_integration_alias']}' created \u2713")
                    except Exception as e:
                        print(f"  Could not create integration: {e}", file=sys.stderr)
                        print("  Continuing without Cortex integration.", file=sys.stderr)
                        self._answers.pop("github_integration_alias", None)
                else:
                    self.prompt("github_token", "GitHub token", env_var="GITHUB_TOKEN", secret=True)
            else:
                self.prompt("github_token", "GitHub token", env_var="GITHUB_TOKEN", secret=True)

        # 2. GitHub owner (derived from auth if token is available)
        try:
            default_owner = self._get_authenticated_user()
        except Exception:
            default_owner = None

        self.prompt("github_owner", "GitHub org or username", default=default_owner)
        self.prompt("repo_name", "Repository name", default="cortex-deploy-demo")

        # 3. Cortex credentials from CLI session
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
        steps = [
            ("Creating GitHub repository", self._create_repo),
            ("Seeding Cortex deploy workflow", self._seed_workflow),
            ("Setting CORTEX_API_KEY secret", lambda: self._set_secret("CORTEX_API_KEY", self._answers["cortex_api_key"])),
            ("Setting CORTEX_BASE_URL secret", lambda: self._set_secret("CORTEX_BASE_URL", self._answers["cortex_base_url"])),
            ("Linking GitHub repository to entity", self._link_github_repo),
        ]
        if self._answers.get("github_integration_alias"):
            steps.append(("Creating Cortex deploy workflow", self._import_cortex_workflow))
        return steps

    def post_steps(self) -> None:
        print()
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        base_url = self._answers["cortex_base_url"].rstrip("/")
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        cortex_url = f"{app_url}/admin/resources?tag=github-actions-demo"
        gh_url = f"https://github.com/{owner}/{repo}"

        workflow_tag = "github-actions-deploy"
        entity_url = f"{app_url}/admin/resources?tag=github-actions-demo"
        workflows_url = f"{app_url}/admin/workflows?activeTab=runs"

        if self._answers.get("github_integration_alias"):
            print(f"\nTo trigger a deploy manually later:")
            print(f"  CLI: cortex workflows runs create -t {workflow_tag} --entity github-actions-demo")
            print(f"  UI:  {_hyperlink(entity_url, 'Open github-actions-demo')} → Workflows tab → Deploy from Entity → Run")

        if self.confirm("\nTrigger a workflow run now?", default=True):
            if self._answers.get("github_integration_alias"):
                # Use Cortex async workflow — waits for GitHub Actions callback
                print(f"  Running: POST /api/v1/workflows/{workflow_tag}/runs")
                try:
                    result = self._trigger_via_cortex_workflow()
                    status = result.get("status", "").upper()
                    run_id = result.get("_run_id", "")
                    if status == "COMPLETED":
                        gh_actions_url = f"https://github.com/{owner}/{repo}/actions"
                        print(f"  Deploy complete \u2713")
                        if run_id:
                            print(f"  Run ID: {run_id}")
                            print(f"  {_hyperlink(workflows_url, 'View workflow runs in Cortex')}")
                        print(f"  {_hyperlink(gh_actions_url, 'View GitHub Actions runs')}")
                        self.mark_done("first_deploy")
                    else:
                        print(f"  Workflow ended with status: {status}", file=sys.stderr)
                        if run_id:
                            print(f"  Run ID: {run_id}", file=sys.stderr)
                            print(f"  {_hyperlink(workflows_url, 'View workflow runs in Cortex')}", file=sys.stderr)
                except Exception as e:
                    print(f"  Trigger failed: {e}", file=sys.stderr)
                    print(f"  Re-trigger via: cortex solutions post-install -s {self.solution_tag}", file=sys.stderr)
            else:
                # No integration — trigger GitHub Actions directly
                gh_dispatch_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/cortex-deploy.yml/dispatches"
                print(f"  Running: POST {gh_dispatch_url}")
                try:
                    self._trigger_direct()
                    print(f"  GitHub Actions workflow triggered \u2713")
                    print(f"  {_hyperlink(f'https://github.com/{owner}/{repo}/actions', 'View GitHub Actions runs')}")
                except Exception as e:
                    print(f"  Trigger failed: {e}", file=sys.stderr)

        print(f"\nDone! Watch your deploy appear at:")
        print(f"  {_hyperlink(cortex_url)}")
        print(f"\nGitHub repo: {_hyperlink(gh_url)}")

    def _create_repo(self) -> str:
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        gh_url = f"https://github.com/{owner}/{repo}"

        check = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=self._gh_headers())
        if check.status_code == 200:
            return f"Already exists: {_hyperlink(gh_url)}"
        if check.status_code != 404:
            raise RuntimeError(f"Unexpected status checking repo existence: {check.status_code} {check.text}")

        user_login = self._get_authenticated_user()
        url = f"{GITHUB_API}/user/repos" if owner == user_login else f"{GITHUB_API}/orgs/{owner}/repos"

        resp = requests.post(
            url,
            headers=self._gh_headers(),
            json={
                "name": repo,
                "description": "Cortex deploy tracking demo — created by cortex solutions post-install",
                "private": False,
                "auto_init": True,
            },
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to create repo: {resp.status_code} {resp.text}")
        return f"Created: {_hyperlink(gh_url)}"

    def _seed_workflow(self) -> str:
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        path = ".github/workflows/cortex-deploy.yml"
        content = TEMPLATE_PATH.read_text()
        content_b64 = base64.b64encode(content.encode()).decode()
        file_url = f"https://github.com/{owner}/{repo}/blob/main/{path}"

        check = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
            headers=self._gh_headers(),
        )

        payload = {"message": "Add Cortex deploy notification workflow", "content": content_b64}

        if check.status_code == 200:
            existing = check.json()
            existing_content = base64.b64decode(existing["content"].replace("\n", "")).decode()
            if existing_content == content:
                return f"Already up to date: {_hyperlink(file_url)}"
            payload["sha"] = existing["sha"]
            action = "Updated"
        else:
            action = "Added"

        resp = requests.put(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
            headers=self._gh_headers(),
            json=payload,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to seed workflow: {resp.status_code} {resp.text}")
        return f"{action}: {_hyperlink(file_url)}"

    def _set_secret(self, secret_name: str, secret_value: str) -> str:
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        secrets_url = f"https://github.com/{owner}/{repo}/settings/secrets/actions"

        key_resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/actions/secrets/public-key",
            headers=self._gh_headers(),
        )
        key_resp.raise_for_status()
        key_data = key_resp.json()

        resp = requests.put(
            f"{GITHUB_API}/repos/{owner}/{repo}/actions/secrets/{secret_name}",
            headers=self._gh_headers(),
            json={
                "encrypted_value": _encrypt_secret(key_data["key"], secret_value),
                "key_id": key_data["key_id"],
            },
        )
        if resp.status_code not in (201, 204):
            raise RuntimeError(f"Failed to set secret {secret_name}: {resp.status_code} {resp.text}")
        action = "Created" if resp.status_code == 201 else "Updated"
        return f"{action} GitHub Actions secret {secret_name}: {_hyperlink(secrets_url, 'View secrets')}"

    def _trigger_direct(self) -> None:
        """Trigger the GitHub Actions workflow directly via the GitHub API."""
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        resp = requests.post(
            f"{GITHUB_API}/repos/{owner}/{repo}/actions/workflows/cortex-deploy.yml/dispatches",
            headers=self._gh_headers(),
            json={"ref": "main"},
        )
        if resp.status_code != 204:
            raise RuntimeError(f"Failed to trigger workflow: {resp.status_code} {resp.text}")

    def _create_github_pat_integration(self) -> None:
        """Create a GitHub PAT integration in Cortex."""
        resp = requests.post(
            f"{self._session_base_url.rstrip('/')}/api/v1/github/configurations/personal",
            json={
                "alias": self._answers["github_integration_alias"],
                "accessToken": self._answers["github_token"],
                "isDefault": True,
            },
            headers={"Authorization": f"Bearer {self._session_api_key}"},
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"{resp.status_code} {resp.text}")

    def _link_github_repo(self) -> list:
        """PATCH the Cortex entity to link the GitHub repository so workflows are discovered."""
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        base_url = self._answers["cortex_base_url"].rstrip("/")
        api_key = self._answers["cortex_api_key"]
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        entity_url = f"{app_url}/admin/resources?tag=github-actions-demo"

        yaml_content = f"""\
openapi: "3.0.0"
info:
  title: GitHub Actions Demo
  x-cortex-tag: github-actions-demo
  x-cortex-type: service
  x-cortex-description: Sample service for demonstrating deploy tracking via GitHub Actions.
  x-cortex-definition: {{}}
  x-cortex-groups:
    - demo-github-actions-deploys
  x-cortex-git:
    github:
      repository: "{owner}/{repo}"
"""
        resp = requests.patch(
            f"{base_url}/api/v1/open-api",
            data=yaml_content.encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/openapi;charset=UTF-8",
            },
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to link GitHub repo to entity: {resp.status_code} {resp.text}")
        return [
            f"Patched entity github-actions-demo with:",
            f"  x-cortex-git:",
            f"    github:",
            f'      repository: "{owner}/{repo}"',
            f"View entity: {_hyperlink(entity_url)}",
        ]

    def _import_cortex_workflow(self) -> str:
        """Import the Cortex trigger workflow with the selected GitHub integration alias."""
        base_url = self._answers["cortex_base_url"].rstrip("/")
        api_key = self._answers["cortex_api_key"]
        alias = self._answers["github_integration_alias"]
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        workflows_url = f"{app_url}/admin/workflows?activeTab=runs"

        yaml_content = WORKFLOW_TEMPLATE_PATH.read_text().replace(
            "PLACEHOLDER_INTEGRATION_ALIAS", alias
        ).replace(
            "https://api.getcortexapp.com", base_url
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
        action = "Created" if resp.status_code == 201 else "Updated"
        return f"{action} workflow 'github-actions-deploy': {_hyperlink(workflows_url, 'View workflows')}"

    def _trigger_via_cortex_workflow(self) -> dict:
        """Trigger the GitHub deploy via the Cortex async workflow and poll for completion."""
        import time

        base_url = self._answers["cortex_base_url"].rstrip("/")
        api_key = self._answers["cortex_api_key"]
        cortex_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        workflow_tag = "github-actions-deploy"

        # Entity-scoped runs require entityId (not entityTag) — look it up first
        entity_resp = requests.get(
            f"{base_url}/api/v1/catalog/github-actions-demo",
            headers=cortex_headers,
            timeout=10,
        )
        if entity_resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch entity: {entity_resp.status_code} {entity_resp.text}")
        entity_id = entity_resp.json().get("id")
        if not entity_id:
            raise RuntimeError("Entity 'github-actions-demo' has no id field in catalog response")

        body = {
            "scope": {"type": "ENTITY", "entityId": entity_id},
        }
        resp = requests.post(
            f"{base_url}/api/v1/workflows/{workflow_tag}/runs",
            json=body,
            headers=cortex_headers,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to start workflow run: {resp.status_code} {resp.text}")

        run_data = resp.json()
        run_id = run_data.get("id")
        if not run_id:
            raise RuntimeError("No run ID returned from workflow start")
        workflow_cid = run_data.get("workflow", {}).get("cid", "")

        terminal = {"COMPLETED", "FAILED", "CANCELLED"}
        start = time.time()
        dots = 0
        while time.time() - start < 300:
            time.sleep(5)
            r = requests.get(
                f"{base_url}/api/v1/workflows/{workflow_tag}/runs/{run_id}",
                headers=cortex_headers,
            )
            r.raise_for_status()
            status = r.json().get("status", "").upper()
            dots += 1
            print(f"\r  Waiting for GitHub Actions{'.' * (dots % 4)}   ", end="", flush=True)
            if status in terminal:
                print()  # newline after dots
                result = r.json()
                result["_run_id"] = run_id
                result["_workflow_cid"] = workflow_cid
                return result

        raise TimeoutError("Timed out waiting for workflow to complete (5 min)")


def main(**kwargs):
    GitHubActionsSetup(**kwargs).run()


if __name__ == "__main__":
    main()
