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
                "ref": "worktree-jenkins-deploy",
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
        """Register port 8080 via the API, make it public, return the public URL."""
        # Debug: dump Codespace state and known ports before touching anything
        cs_resp = requests.get(
            f"{GITHUB_API}/user/codespaces/{name}",
            headers=self._gh_headers(), timeout=15,
        )
        print(f"\n  [debug] Codespace state: {cs_resp.json().get('state')} "
              f"machine={cs_resp.json().get('machine', {}).get('name')}")

        ports_resp = requests.get(
            f"{GITHUB_API}/user/codespaces/{name}/ports",
            headers=self._gh_headers(), timeout=15,
        )
        print(f"  [debug] GET /ports → {ports_resp.status_code}: {ports_resp.text[:300]}")

        # Register the port with GitHub's API (devcontainer forwardPorts only activates
        # when a client connects; the REST API needs an explicit POST first).
        post_url = f"{GITHUB_API}/user/codespaces/{name}/ports"
        print(f"  [debug] POST {post_url} {{port: {JENKINS_PORT}}}")
        post_resp = requests.post(
            post_url,
            headers=self._gh_headers(),
            json={"port": JENKINS_PORT},
            timeout=15,
        )
        print(f"  [debug] POST /ports → {post_resp.status_code}: {post_resp.text[:300]}")
        if post_resp.status_code not in (200, 201, 409):  # 409 = already registered
            raise RuntimeError(
                f"Failed to register Jenkins port: {post_resp.status_code} {post_resp.text}"
            )

        patch_url = f"{GITHUB_API}/user/codespaces/{name}/ports/{JENKINS_PORT}/visibility"
        print(f"  [debug] PATCH {patch_url}")
        resp = requests.patch(
            patch_url,
            headers=self._gh_headers(),
            json={"visibility": "public"},
            timeout=15,
        )
        print(f"  [debug] PATCH /visibility → {resp.status_code}: {resp.text[:300]}")
        if resp.status_code not in (200, 204):
            raise RuntimeError(
                f"Failed to expose Jenkins port: {resp.status_code} {resp.text}"
            )
        return f"https://{name}-{JENKINS_PORT}.app.github.dev"

    def _delete_codespace(self, name: str) -> None:
        """Delete a Codespace by name and clear it from state."""
        resp = requests.delete(
            f"{GITHUB_API}/user/codespaces/{name}",
            headers=self._gh_headers(),
            timeout=15,
        )
        if resp.status_code not in (200, 202, 204):
            raise RuntimeError(
                f"Failed to delete Codespace '{name}': {resp.status_code} {resp.text}"
            )
        self._state.pop("codespace_name", None)
        self._save_state()

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
        print(
            "\nJenkins source:\n"
            "  Y — provision a fresh Jenkins instance in GitHub Codespaces (recommended for demo).\n"
            "      Requires a GitHub PAT with 'codespace' scope. Jenkins will be pre-configured\n"
            "      and its port made publicly accessible for Cortex to reach.\n"
            "  N — use an existing Jenkins instance. You will be prompted for its URL and\n"
            "      credentials. The instance must be publicly reachable from the internet.\n"
        )
        use_codespace = self.confirm(
            "Spin up a Jenkins instance in GitHub Codespaces?", default=True
        )
        self._answers["use_codespace"] = use_codespace

        if use_codespace:
            self.prompt(
                "github_pat",
                "GitHub Personal Access Token (needs 'codespace' scope)",
                env_var="GITHUB_PAT",
                hidden=True,
            )
            # Jenkins URL is determined after Codespace creation (in steps)
            self._answers["jenkins_username"] = JENKINS_DEFAULT_USERNAME
            self._answers["jenkins_token"] = JENKINS_DEFAULT_TOKEN
            self._answers.setdefault("jenkins_job", "cortex-deploy")
        else:
            print(
                "\n⚠️  Your Jenkins instance must be publicly reachable from the internet.\n"
                "   Cortex will POST to Jenkins to trigger builds, and Jenkins will POST\n"
                "   back to Cortex when each build finishes. A Jenkins behind a firewall\n"
                "   or on localhost will not work with this workflow.\n"
            )
            self.prompt("jenkins_url", "Jenkins base URL (e.g. https://jenkins.example.com)")
            self.prompt("jenkins_username", "Jenkins username", default="admin")
            self.prompt("jenkins_token", "Jenkins API token or password", secret=True)
            self.prompt("jenkins_job", "Jenkins job name (will be created if missing)", default="cortex-deploy")

    # ── Jenkins API helpers ────────────────────────────────────────────────

    def _jenkins_url(self) -> str:
        return self._answers["jenkins_url"].rstrip("/")

    def _jenkins_auth(self) -> tuple:
        return (self._answers["jenkins_username"], self._answers["jenkins_token"])

    def _get_job_xml(self) -> str:
        """Return Jenkins job config.xml with the Jenkinsfile embedded in CDATA."""
        jenkinsfile = JENKINSFILE_TEMPLATE_PATH.read_text()
        return f"""\
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>Cortex Deploy Pipeline — records deploys in Cortex and posts async callback</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.StringParameterDefinition>
          <name>callback_url</name>
          <defaultValue></defaultValue>
          <description>Cortex async callback URL</description>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>cortex_entity_tag</name>
          <defaultValue></defaultValue>
          <description>Cortex entity tag</description>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script><![CDATA[{jenkinsfile}]]></script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""

    def _wait_for_jenkins(self, timeout_secs: int = 120) -> None:
        """Poll Jenkins /login until it returns HTTP 200."""
        url = f"{self._jenkins_url()}/login"
        start = time.time()
        dots = 0
        while time.time() - start < timeout_secs:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(5)
            dots += 1
            print(f"\r  Waiting for Jenkins{'.' * (dots % 4)}   ", end="", flush=True)
        raise TimeoutError(f"Jenkins did not respond within {timeout_secs}s at {url}")

    def _create_jenkins_job(self) -> None:
        """Create the cortex-deploy pipeline job in Jenkins. Skips if already exists."""
        job_name = self._answers["jenkins_job"]
        base = self._jenkins_url()
        auth = self._jenkins_auth()

        # Check if job exists
        check = requests.get(
            f"{base}/job/{job_name}/api/json",
            auth=auth,
            timeout=10,
        )
        if check.status_code == 200:
            return  # already exists — skip

        xml = self._get_job_xml()
        resp = requests.post(
            f"{base}/createItem",
            params={"name": job_name},
            auth=auth,
            headers={"Content-Type": "application/xml"},
            data=xml.encode("utf-8"),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Failed to create Jenkins job '{job_name}': {resp.status_code} {resp.text}"
            )

    def _add_jenkins_credential(self, credential_id: str, secret: str, description: str) -> None:
        """Add a secret-text credential to the Jenkins global credential store. Skips if exists."""
        import json as _json
        base = self._jenkins_url()
        auth = self._jenkins_auth()

        # Check if credential exists
        check = requests.get(
            f"{base}/credentials/store/system/domain/_/credential/{credential_id}/api/json",
            auth=auth,
            timeout=10,
        )
        if check.status_code == 200:
            return  # already exists

        payload = {
            "": "0",
            "credentials": {
                "scope": "GLOBAL",
                "id": credential_id,
                "secret": secret,
                "description": description,
                "$class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl",
            },
        }
        resp = requests.post(
            f"{base}/credentials/store/system/domain/_/createCredentials",
            auth=auth,
            data={"json": _json.dumps(payload)},
            timeout=15,
        )
        # Jenkins returns 200 or 302 on success
        if resp.status_code not in (200, 201, 302):
            raise RuntimeError(
                f"Failed to create Jenkins credential '{credential_id}': {resp.status_code} {resp.text}"
            )

    # ── Codespace orchestration ────────────────────────────────────────────

    def _verify_codespace_identity(self, name: str) -> bool:
        """Return True if the Codespace belongs to this solution (correct repo + devcontainer)."""
        resp = requests.get(
            f"{GITHUB_API}/user/codespaces/{name}",
            headers=self._gh_headers(),
            timeout=15,
        )
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        data = resp.json()
        repo_match = data.get("repository", {}).get("full_name") == CODESPACE_REPO
        container_match = data.get("devcontainer_path") == DEVCONTAINER_PATH
        return repo_match and container_match

    def _provision_codespace(self) -> str:
        """Create Codespace (or reuse existing), wait for it to be ready, expose port, set jenkins_url."""
        existing = self._state.get("codespace_name")
        if existing:
            if self._verify_codespace_identity(existing):
                print(f"  Reusing existing Codespace '{existing}'")
                name = existing
            else:
                print(
                    f"  ⚠️  Saved Codespace '{existing}' no longer exists or is not a Jenkins "
                    f"Codespace — creating a new one."
                )
                self._state.pop("codespace_name", None)
                name = self._create_codespace()
                self._state["codespace_name"] = name
                self._save_state()
        else:
            name = self._create_codespace()
            self._state["codespace_name"] = name
            self._save_state()
        self._wait_for_codespace(name)
        url = self._expose_jenkins_port(name)
        self._answers["jenkins_url"] = url
        return f"Jenkins URL: {_hyperlink(url)}"

    # ── Cortex entity custom metadata ─────────────────────────────────────

    def _write_entity_custom_metadata(self) -> None:
        """Patch the entity YAML with Jenkins coordinates in x-cortex-custom-metadata."""
        base_url = self._answers["cortex_base_url"].rstrip("/")
        entity_tag = self._answers["entity_tag"]
        yaml_content = f"""\
openapi: "3.0.0"
info:
  title: Jenkins Demo
  x-cortex-tag: {entity_tag}
  x-cortex-custom-metadata:
    jenkins:
      url: "{self._answers['jenkins_url']}"
      job: "{self._answers['jenkins_job']}"
      username: "{self._answers['jenkins_username']}"
      token: "{self._answers['jenkins_token']}"
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
            raise RuntimeError(
                f"Failed to write entity custom metadata: {resp.status_code} {resp.text}"
            )

    # ── Cortex workflow import ─────────────────────────────────────────────

    def _import_cortex_workflow(self) -> None:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        api_key = self._answers["cortex_api_key"]
        yaml_content = WORKFLOW_TEMPLATE_PATH.read_text()

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
        workflow_tag = "jenkins-trigger-deploy"
        cortex_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        body = {
            "scope": {"type": "ENTITY", "entityId": self._answers["entity_tag"]},
            "initialContext": {},
        }
        resp = requests.post(
            f"{base_url}/api/v1/workflows/{workflow_tag}/runs",
            json=body,
            headers=cortex_headers,
            timeout=15,
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
                timeout=10,
            )
            r.raise_for_status()
            status = r.json().get("status", "").upper()
            dots += 1
            print(f"\r  Waiting for Jenkins pipeline{'.' * (dots % 4)}   ", end="", flush=True)
            if status in terminal:
                print()
                return r.json()
        raise TimeoutError("Timed out waiting for workflow to complete (6 min)")

    # ── Steps ──────────────────────────────────────────────────────────────

    def steps(self) -> list[tuple[str, callable]]:
        step_list = []
        if self._answers.get("use_codespace"):
            step_list.append(("Provisioning Jenkins in GitHub Codespaces", self._provision_codespace))
            step_list.append(("Waiting for Jenkins to be ready", self._wait_for_jenkins))
        step_list += [
            ("Creating Jenkins deploy job", self._create_jenkins_job),
            ("Adding CORTEX_API_KEY credential to Jenkins", lambda: self._add_jenkins_credential(
                "CORTEX_API_KEY", self._answers["cortex_api_key"], "Cortex API key"
            )),
            ("Adding CORTEX_BASE_URL credential to Jenkins", lambda: self._add_jenkins_credential(
                "CORTEX_BASE_URL", self._answers["cortex_base_url"], "Cortex base URL"
            )),
            ("Writing Jenkins config to entity custom metadata", self._write_entity_custom_metadata),
            ("Importing Cortex trigger workflow", self._import_cortex_workflow),
        ]
        return step_list

    def post_steps(self) -> None:
        # Offer to clean up a Codespace left running from a previous setup run
        saved_codespace = self._state.get("codespace_name")
        if saved_codespace and not self._answers.get("use_codespace"):
            print(f"\nA Codespace from a previous run is still running ({saved_codespace}).")
            if self.confirm("Delete it?", default=True):
                try:
                    self._delete_codespace(saved_codespace)
                    print(f"  Codespace '{saved_codespace}' deleted ✓")
                except Exception as e:
                    print(f"  Failed to delete Codespace: {e}", file=sys.stderr)

        base_url = self._answers["cortex_base_url"].rstrip("/")
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        entity_tag = self._answers["entity_tag"]
        workflow_tag = "jenkins-trigger-deploy"

        entity_url = f"{app_url}/admin/resources?tag={entity_tag}"
        workflows_url = f"{app_url}/admin/workflows"
        jenkins_url = self._answers.get("jenkins_url", "")
        jenkins_job = self._answers.get("jenkins_job", "cortex-deploy")
        jenkins_job_url = f"{jenkins_url}/job/{jenkins_job}" if jenkins_url else ""

        print(f"\nTo trigger a deploy manually later:")
        print(f"  CLI: cortex workflows run -t {workflow_tag} --scope ENTITY --entity {entity_tag}")
        print(f"  UI:  {_hyperlink(entity_url, entity_tag)} → Workflows tab → Solution: Trigger Jenkins Deploy → Run")

        print(f"\n{_hyperlink(workflows_url, 'View workflows in Cortex')}")
        if jenkins_job_url:
            print(f"{_hyperlink(jenkins_job_url, 'View Jenkins job')}")

        if self.confirm("Trigger a test workflow run now?", default=True):
            print("  Starting Cortex workflow run (waiting for Jenkins pipeline to complete)...")
            try:
                result = self._trigger_via_cortex_workflow()
                status = result.get("status", "").upper()
                if status == "COMPLETED":
                    print("  Workflow run complete ✓")
                    self._confirm_deploy_recorded(base_url, entity_tag, entity_url)
                    self.mark_done("first_deploy")
                else:
                    print(f"  Workflow run ended with status: {status}", file=sys.stderr)
                    print(f"  Check {_hyperlink(workflows_url, 'Cortex Workflow runs')} to investigate.", file=sys.stderr)
            except Exception as e:
                print(f"  Trigger failed: {e}", file=sys.stderr)
                print(f"  Re-trigger via: cortex solutions post-install -s {self.solution_tag}", file=sys.stderr)

        print(f"\nDone! Watch your deploy appear at:")
        print(f"  {_hyperlink(entity_url)}")
        if jenkins_job_url:
            print(f"\nJenkins job: {_hyperlink(jenkins_job_url)}")

        # Codespace lifecycle: keep or delete
        if self._answers.get("use_codespace") and self._state.get("codespace_name"):
            codespace_name = self._state["codespace_name"]
            print()
            if not self.confirm("Keep the Codespace running?", default=False):
                print(f"  Deleting Codespace '{codespace_name}'...")
                try:
                    self._delete_codespace(codespace_name)
                    print("  Codespace deleted ✓")
                except Exception as e:
                    print(f"  Failed to delete Codespace: {e}", file=sys.stderr)
            else:
                print("""
⚠️  WARNING: Your Codespace is still running and will accrue compute charges
    (~$0.18/core-hour after your free monthly allowance of 120 core-hours).
    GitHub auto-stops after 30 min of inactivity, but does NOT delete it.

    To delete it later, run:
      cortex solutions post-install -s jenkins-deploy

    Or delete it directly at: https://github.com/codespaces
""")

    def _confirm_deploy_recorded(self, base_url: str, entity_tag: str, entity_url: str) -> None:
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
                    print(f"  Deploy recorded on entity ✓  {_hyperlink(entity_url, entity_tag)}")
                    return
        except Exception:
            pass
        print(f"  Deploy may still be indexing — check {_hyperlink(entity_url, entity_tag)}")


def main(**kwargs):
    JenkinsDeploySetup(**kwargs).run()


if __name__ == "__main__":
    main()
