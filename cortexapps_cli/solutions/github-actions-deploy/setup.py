"""
Post-install setup script for the github-actions-deploy solution.
Creates and seeds a GitHub repo with the Cortex deploy workflow.
Run via: cortex solutions post-install -s github-actions-deploy
"""
import base64
import sys
from pathlib import Path
from typing import Optional

import requests
from nacl import encoding, public

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

GITHUB_API = "https://api.github.com"
TEMPLATE_PATH = Path(__file__).parent / "_templates" / "cortex-deploy.yml"


def _encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    """Encrypt a secret using the repo's libsodium public key."""
    pk = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


class GitHubActionsSetup(SolutionSetup):
    solution_tag = "github-actions-deploy"

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
        self.prompt("cortex_api_key", "Cortex API key", env_var="CORTEX_API_KEY", secret=True)
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
        if self.confirm("Ready to trigger your first workflow run?", default=True):
            try:
                self._trigger_workflow()
                print(f"[5/5] Triggering workflow... \u2713")
            except Exception as e:
                print(f"Trigger failed: {e}", file=sys.stderr)
                raise SystemExit(1)

        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]
        base_url = self._answers["cortex_base_url"].rstrip("/")
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        print(f"\nDone! Watch your first deploy appear at:")
        print(f"  {app_url}/catalog/github-actions-demo")
        print(f"\nGitHub repo: https://github.com/{owner}/{repo}")

    def _create_repo(self) -> None:
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]

        check = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=self._gh_headers())
        if check.status_code == 200:
            return  # already exists

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

    def _trigger_workflow(self) -> None:
        owner = self._answers["github_owner"]
        repo = self._answers["repo_name"]

        resp = requests.post(
            f"{GITHUB_API}/repos/{owner}/{repo}/actions/workflows/cortex-deploy.yml/dispatches",
            headers=self._gh_headers(),
            json={"ref": "main"},
        )
        if resp.status_code != 204:
            raise RuntimeError(f"Failed to trigger workflow: {resp.status_code} {resp.text}")


def main():
    GitHubActionsSetup().run()


if __name__ == "__main__":
    main()
