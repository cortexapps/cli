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

    def __init__(self, cortex_api_key: str = None, cortex_base_url: str = None, **kwargs):
        super().__init__(**kwargs)
        self._session_api_key = cortex_api_key
        self._session_base_url = cortex_base_url

    def _gh_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._answers['github_token']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_authenticated_user(self) -> str:
        resp = requests.get(f"{GITHUB_API}/user", headers=self._gh_headers())
        resp.raise_for_status()
        return resp.json()["login"]

    def collect_prompts(self) -> None:
        self.prompt("github_token", "GitHub token", env_var="GITHUB_TOKEN", secret=True)

        try:
            default_owner = self._get_authenticated_user()
        except Exception:
            default_owner = None

        self.prompt("github_owner", "GitHub org or username", default=default_owner)
        self.prompt("repo_name", "Repository name", default="cortex-deploy-demo")

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
            ("Creating GitHub repository", self._create_repo),
            ("Seeding Cortex deploy workflow", self._seed_workflow),
            ("Setting CORTEX_API_KEY secret", lambda: self._set_secret("CORTEX_API_KEY", self._answers["cortex_api_key"])),
            ("Setting CORTEX_BASE_URL secret", lambda: self._set_secret("CORTEX_BASE_URL", self._answers["cortex_base_url"])),
        ]

    def post_steps(self) -> None:
        print()
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        base_url = self._answers["cortex_base_url"].rstrip("/")
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        cortex_url = f"{app_url}/admin/resources?tag=github-actions-demo"
        gh_url = f"https://github.com/{owner}/{repo}"

        if self.confirm("Ready to trigger your first workflow run?", default=True):
            print("  Starting Cortex workflow run (waiting for GitHub Actions to complete)...")
            try:
                result = self._trigger_via_cortex_workflow()
                status = result.get("status", "").upper()
                if status == "COMPLETED":
                    run_result = (
                        result.get("actions", {})
                        .get("trigger-deploy", {})
                        .get("outputs", {})
                        .get("result", {})
                        .get("output", {})
                    )
                    conclusion = run_result.get("conclusion", "success")
                    run_url = run_result.get("run_url", "")
                    print(f"[5/5] Deploy complete: {conclusion} \u2713")
                    if run_url:
                        print(f"  {_hyperlink(run_url, 'View GitHub Actions run')}")
                    self.mark_done("first_deploy")
                else:
                    print(f"[5/5] Workflow ended with status: {status}", file=sys.stderr)
            except Exception as e:
                print(f"[5/5] Trigger failed: {e}", file=sys.stderr)
                print(f"  You can re-trigger via: cortex solutions post-install -s {self.solution_tag}", file=sys.stderr)

        print(f"\nDone! Watch your first deploy appear at:")
        print(f"  {_hyperlink(cortex_url)}")
        print(f"\nGitHub repo: {_hyperlink(gh_url)}")

    def _create_repo(self) -> None:
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]

        check = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=self._gh_headers())
        if check.status_code == 200:
            return  # already exists
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

    def _seed_workflow(self) -> None:
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        path = ".github/workflows/cortex-deploy.yml"
        content = TEMPLATE_PATH.read_text()
        content_b64 = base64.b64encode(content.encode()).decode()

        check = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
            headers=self._gh_headers(),
        )

        payload = {"message": "Add Cortex deploy notification workflow", "content": content_b64}

        if check.status_code == 200:
            existing = check.json()
            existing_content = base64.b64decode(existing["content"].replace("\n", "")).decode()
            if existing_content == content:
                return  # unchanged
            payload["sha"] = existing["sha"]

        resp = requests.put(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
            headers=self._gh_headers(),
            json=payload,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to seed workflow: {resp.status_code} {resp.text}")

    def _set_secret(self, secret_name: str, secret_value: str) -> None:
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]

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

    def _trigger_via_cortex_workflow(self) -> dict:
        """Trigger the GitHub deploy via the Cortex async workflow and poll for completion."""
        import time

        base_url = self._answers["cortex_base_url"].rstrip("/")
        api_key = self._answers["cortex_api_key"]
        cortex_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        workflow_tag = "github-actions-trigger-deploy"

        body = {
            "scope": {"type": "GLOBAL"},
            "initialContext": {
                "variables": {
                    "github-token": self._answers["github_token"],
                    "github-owner": self._answers["github_owner"],
                    "repo-name": self._answers["repo_name"],
                }
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
                return r.json()

        raise TimeoutError("Timed out waiting for workflow to complete (5 min)")


def main(**kwargs):
    GitHubActionsSetup(**kwargs).run()


if __name__ == "__main__":
    main()
