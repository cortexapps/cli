"""
Post-install setup script for the jenkins-deploy solution.
Wires up Jenkins credentials, creates the pipeline job in Jenkins,
imports the Cortex async workflow, and optionally triggers a test run.
Run via: cortex solutions post-install -s jenkins-deploy
"""

SETUP_DESCRIPTION = (
    "This solution includes a setup script that will configure your Jenkins "
    "job in Cortex, create the deploy pipeline in Jenkins, import the Cortex "
    "trigger workflow, and optionally fire a test deploy."
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

WORKFLOW_TEMPLATE_PATH = Path(__file__).parent / "_templates" / "trigger-jenkins-deploy.yaml"
JENKINSFILE_TEMPLATE_PATH = Path(__file__).parent / "_templates" / "Jenkinsfile"

GITHUB_API = "https://api.github.com"
CODESPACE_REPO = "cortexapps/cli"
DEVCONTAINER_PATH = ".devcontainer/jenkins/devcontainer.json"
JENKINS_PORT = 8080
JENKINS_DEFAULT_USERNAME = "admin"
JENKINS_DEFAULT_TOKEN = "cortex-demo"


def _hyperlink(url: str, text: str = None) -> str:
    label = text if text is not None else url
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"


class JenkinsDeploySetup(SolutionSetup):
    solution_tag = "jenkins-deploy"

    def __init__(self, cortex_api_key: str = None, cortex_base_url: str = None, **kwargs):
        super().__init__(**kwargs)
        self._session_api_key = cortex_api_key
        self._session_base_url = cortex_base_url

    # ── GitHub Codespaces API helpers ──────────────────────────────────────

    def _gh_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._answers['github_pat']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _create_codespace(self) -> str:
        """Create a Codespace from this repo's Jenkins devcontainer. Returns codespace name."""
        resp = requests.post(
            f"{GITHUB_API}/repos/{CODESPACE_REPO}/codespaces",
            headers=self._gh_headers(),
            json={
                "ref": "main",
                "devcontainer_path": DEVCONTAINER_PATH,
                "machine": "basicLinux32gb",
            },
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Failed to create Codespace: {resp.status_code} {resp.text}"
            )
        name = resp.json()["name"]
        print(f"  Codespace '{name}' provisioning...")
        return name

    def _wait_for_codespace(self, name: str, timeout_secs: int = 300) -> None:
        """Poll until the Codespace state is Available."""
        terminal_states = {"Available", "Failed", "Deleted"}
        start = time.time()
        dots = 0
        while time.time() - start < timeout_secs:
            time.sleep(10)
            resp = requests.get(
                f"{GITHUB_API}/user/codespaces/{name}",
                headers=self._gh_headers(),
                timeout=15,
            )
            resp.raise_for_status()
            state = resp.json().get("state", "")
            dots += 1
            print(f"\r  Waiting for Codespace{'.' * (dots % 4)}   ", end="", flush=True)
            if state == "Available":
                print()
                return
            if state in terminal_states:
                raise RuntimeError(f"Codespace ended in unexpected state: {state}")
        raise TimeoutError(f"Codespace did not become Available within {timeout_secs}s")

    def _expose_jenkins_port(self, name: str) -> str:
        """Make Codespace port 8080 public. Returns the public Jenkins URL."""
        resp = requests.patch(
            f"{GITHUB_API}/user/codespaces/{name}/ports/{JENKINS_PORT}/visibility",
            headers=self._gh_headers(),
            json={"visibility": "public"},
            timeout=15,
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(
                f"Failed to expose Jenkins port: {resp.status_code} {resp.text}"
            )
        return f"https://{name}-{JENKINS_PORT}.app.github.dev"

    # ── Prompts ────────────────────────────────────────────────────────────

    def collect_prompts(self) -> None:
        # Cortex entity
        self.prompt("entity_tag", "Cortex entity tag to record deploys against", default="jenkins-demo")

        # Cortex credentials
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

        # Jenkins source: Codespace or existing instance
        use_codespace = self.confirm(
            "Spin up a Jenkins instance in GitHub Codespaces?", default=True
        )
        self._answers["use_codespace"] = use_codespace

        if use_codespace:
            self.prompt(
                "github_pat",
                "GitHub Personal Access Token (needs 'codespace' scope)",
                env_var="GITHUB_PAT",
                secret=True,
            )
            # Jenkins URL is determined after Codespace creation (in steps)
            self._answers["jenkins_username"] = JENKINS_DEFAULT_USERNAME
            self._answers["jenkins_token"] = JENKINS_DEFAULT_TOKEN
            self._answers.setdefault("jenkins_job", "cortex-deploy")
        else:
            self.prompt("jenkins_url", "Jenkins base URL (e.g. https://jenkins.example.com)")
            self.prompt("jenkins_username", "Jenkins username", default="admin")
            self.prompt("jenkins_token", "Jenkins API token or password", secret=True)
            self.prompt("jenkins_job", "Jenkins job name (will be created if missing)", default="cortex-deploy")

    # ── Steps ──────────────────────────────────────────────────────────────

    def steps(self) -> list[tuple[str, callable]]:
        return []


def main(**kwargs):
    JenkinsDeploySetup(**kwargs).run()


if __name__ == "__main__":
    main()
