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

import secrets
import subprocess
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

_PASSPHRASE_WORDS = [
    "amber", "anchor", "apple", "arrow", "atlas", "azure", "badge", "banjo",
    "baron", "beach", "birch", "blade", "blaze", "bloom", "brace", "brine",
    "brook", "cedar", "chain", "chalk", "chart", "chase", "chief", "chime",
    "civic", "clamp", "cliff", "cloak", "cloud", "clove", "cobra", "comet",
    "coral", "crane", "crisp", "crown", "curve", "cycle", "daisy", "delta",
    "depot", "derby", "digit", "diver", "dowel", "draft", "drake", "drift",
    "drill", "drums", "dunes", "eagle", "ebony", "ember", "envoy", "fable",
    "flair", "flank", "flare", "flask", "fleet", "flint", "flock", "flute",
    "forge", "frond", "frost", "gavel", "geyser", "glide", "glint", "globe",
    "gloss", "glove", "golem", "grace", "grain", "grand", "grasp", "grove",
    "guild", "gusto", "hatch", "haven", "hazel", "helix", "heron", "hinge",
    "holly", "honey", "honor", "hound", "hover", "igloo", "inlet", "ivory",
    "jade", "jaguar", "jazz", "jewel", "joust", "judge", "jumbo", "karma",
    "kayak", "kelp", "knoll", "lance", "lapis", "laser", "latch", "lemon",
    "lemur", "level", "light", "lilac", "linen", "lodge", "lotus", "lucid",
    "lunar", "lyric", "magma", "mango", "manor", "maple", "marsh", "mason",
    "maxim", "merit", "micro", "mirth", "molar", "moose", "mossy", "mount",
    "mural", "niche", "noble", "notch", "novel", "oaken", "ocean", "ochre",
    "olive", "onyx", "optic", "orbit", "otter", "oxide", "ozone", "panda",
    "panel", "patch", "pearl", "pedal", "perch", "phase", "pilot", "pinch",
    "pixel", "plaza", "plumb", "plume", "polar", "poppy", "prism", "probe",
    "prowl", "proxy", "pulse", "quail", "quest", "quota", "radar", "radix",
    "rally", "raven", "realm", "relay", "ridge", "rivet", "robin", "rocky",
    "rogue", "rouge", "rover", "royal", "rustic", "sable", "salvo", "sandy",
    "sauce", "scale", "scout", "serum", "shade", "shaft", "shark", "sheen",
    "shell", "shift", "sigma", "silky", "silver", "slate", "sleek", "sleet",
    "slope", "snowy", "solar", "solid", "sonic", "spark", "spear", "spire",
    "spore", "spray", "squad", "stalk", "stamp", "stark", "steam", "steel",
    "stern", "stoic", "stone", "storm", "stout", "strut", "suede", "sugar",
    "surge", "swamp", "sword", "syrup", "talon", "taper", "tapir", "tempo",
    "terra", "thorn", "tiger", "titan", "tonic", "topaz", "torch", "totem",
    "trawl", "trend", "trout", "truce", "tunic", "turbo", "twine", "ultra",
    "umber", "unity", "upper", "valor", "valve", "vapor", "vault", "venom",
    "verge", "vigor", "viola", "viper", "visor", "vista", "vocal", "vogue",
    "walnut", "wedge", "wheat", "whirl", "wield", "winch", "witty", "woven",
    "xenon", "yacht", "yield", "zebra", "zephyr", "zippy",
]


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
        """Ensure the Jenkins port is publicly accessible and return its URL.

        Port visibility is set at build time via devcontainer.json portsAttributes.
        For reused Codespaces this may need to be set explicitly via gh CLI.
        """
        try:
            subprocess.run(
                ["gh", "codespace", "ports", "visibility",
                 f"{JENKINS_PORT}:public", "-c", name],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # gh unavailable or failed; devcontainer.json visibility applies for new Codespaces
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
            "  Y — provision Jenkins in GitHub Codespaces (recommended for demo).\n"
            "      Requires a GitHub PAT with 'codespace' scope. Jenkins will be pre-configured\n"
            "      and its port made publicly accessible for Cortex to reach.\n"
            "      If a Codespace from a previous run of this command exists, it will be reused.\n"
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
<flow-definition>
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
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition">
    <script><![CDATA[{jenkinsfile}]]></script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""

    def _wait_for_jenkins(self, timeout_secs: int = 180) -> None:
        """Poll Jenkins until the UI is up AND the default credentials are accepted.

        Two-phase wait:
        1. /login returns 200 (Jenkins is up)
        2. /me/api/json with default credentials returns 200 (JCasC has applied)
        """
        base = self._jenkins_url()
        start = time.time()
        dots = 0

        # Phase 1: wait for /login
        while time.time() - start < timeout_secs:
            try:
                resp = requests.get(f"{base}/login", timeout=5)
                if resp.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(5)
            dots += 1
            print(f"\r  Waiting for Jenkins{'.' * (dots % 4)}   ", end="", flush=True)
        else:
            raise TimeoutError(f"Jenkins did not respond within {timeout_secs}s at {base}")

        # Phase 2: wait for Jenkins to finish initializing (init scripts applied).
        # /api/json returns 200 once Jenkins is fully up and accepting API requests.
        while time.time() - start < timeout_secs:
            try:
                resp = requests.get(f"{base}/api/json", timeout=5)
                if resp.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(5)
            dots += 1
            print(f"\r  Waiting for Jenkins config{'.' * (dots % 4)}   ", end="", flush=True)
        raise TimeoutError(f"Jenkins did not finish initializing within {timeout_secs}s")

    def _generate_passphrase(self) -> str:
        """Return a random 4-word hyphen-joined passphrase, e.g. 'coral-ember-ridge-titan'."""
        return "-".join(secrets.choice(_PASSPHRASE_WORDS) for _ in range(4))

    def _jenkins_session(self, auth: tuple = None) -> requests.Session:
        """Return an authenticated requests.Session with the Jenkins CSRF crumb pre-set."""
        session = requests.Session()
        session.auth = auth or self._jenkins_auth()
        crumb_resp = session.get(f"{self._jenkins_url()}/crumbIssuer/api/json", timeout=10)
        if crumb_resp.status_code == 200:
            try:
                data = crumb_resp.json()
                session.headers[data["crumbRequestField"]] = data["crumb"]
            except (ValueError, KeyError):
                pass
        return session

    def _run_groovy(self, session: requests.Session, script: str) -> str:
        """POST a Groovy script to Jenkins Script Console and return stdout. Raises on failure."""
        resp = session.post(
            f"{self._jenkins_url()}/scriptText",
            data={"script": script},
            timeout=15,
        )
        if resp.status_code != 200 or "Exception" in resp.text:
            raise RuntimeError(
                f"Jenkins Script Console error: {resp.status_code} {resp.text[:200]}"
            )
        return resp.text.strip()

    def _generate_api_token(self) -> str:
        """Generate a Jenkins API token via the REST API (no Script Console needed).

        Returns the token value on success, or the default password as fallback.
        """
        session = self._jenkins_session(auth=(JENKINS_DEFAULT_USERNAME, JENKINS_DEFAULT_TOKEN))
        resp = session.post(
            f"{self._jenkins_url()}/user/{JENKINS_DEFAULT_USERNAME}"
            "/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken",
            data={"newTokenName": "cortex"},
            timeout=15,
        )
        if resp.status_code == 200:
            try:
                token = resp.json()["data"]["tokenValue"]
                if token:
                    return token
            except (ValueError, KeyError):
                pass
        # Fallback: use the default password directly (works for Basic Auth too)
        return JENKINS_DEFAULT_TOKEN

    def _set_jenkins_admin_password(self) -> None:
        """Generate a Jenkins API token for Cortex to use.

        Uses the Jenkins REST API (not the Script Console) to create an API token
        for the admin user.  Falls back to the default password if token generation
        fails.  Skips if already done in a previous run for this Codespace.
        """
        saved = self._state.get("jenkins_api_token")
        if saved:
            self._answers["jenkins_token"] = saved
            print(f"  Jenkins API token already configured (from previous run)")
            return

        token = self._generate_api_token()
        self._answers["jenkins_token"] = token
        self._state["jenkins_api_token"] = token
        self._save_state()
        if token == JENKINS_DEFAULT_TOKEN:
            print(f"  Jenkins credentials: {JENKINS_DEFAULT_USERNAME} / {JENKINS_DEFAULT_TOKEN}")
        else:
            print(f"  Jenkins API token generated for Cortex")

    def _update_jenkins_job_script(self, session: requests.Session, job_name: str, base: str) -> None:
        """Patch the <script> CDATA block in the existing job's config.xml.

        Fetching the live config and replacing only the script preserves Jenkins'
        own plugin version attributes, avoiding the 500 that a full XML replace causes.
        """
        import re
        get_resp = session.get(f"{base}/job/{job_name}/config.xml", timeout=10)
        if get_resp.status_code != 200:
            print(
                f"  Warning: could not fetch existing job config ({get_resp.status_code}). "
                f"Delete '{job_name}' in Jenkins and re-run setup to apply the latest Jenkinsfile."
            )
            return
        jenkinsfile = JENKINSFILE_TEMPLATE_PATH.read_text()
        new_cdata = f"<script><![CDATA[{jenkinsfile}]]></script>"
        patched = re.sub(
            r"<script><!\[CDATA\[.*?\]\]></script>",
            new_cdata,
            get_resp.text,
            flags=re.DOTALL,
        )
        if patched == get_resp.text:
            return  # no change needed
        resp = session.post(
            f"{base}/job/{job_name}/config.xml",
            headers={"Content-Type": "application/xml"},
            data=patched.encode("utf-8"),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            print(
                f"  Warning: could not update Jenkinsfile ({resp.status_code}). "
                f"Delete '{job_name}' in Jenkins and re-run setup to apply the latest Jenkinsfile."
            )

    def _configure_jenkins_root_url(self) -> None:
        """Set Jenkins root URL via Script Console so env.BUILD_URL is populated in builds."""
        jenkins_url = self._jenkins_url()
        script = (
            "import jenkins.model.JenkinsLocationConfiguration\n"
            "def config = JenkinsLocationConfiguration.get()\n"
            f'config.setUrl("{jenkins_url}/")\n'
            "config.save()\n"
            'println "ok"\n'
        )
        session = self._jenkins_session()
        self._run_groovy(session, script)

    def _create_jenkins_job(self) -> None:
        """Create or update the cortex-deploy pipeline job in Jenkins."""
        job_name = self._answers["jenkins_job"]
        base = self._jenkins_url()
        session = self._jenkins_session()
        xml = self._get_job_xml()

        check = session.get(f"{base}/job/{job_name}/api/json", timeout=10)
        if check.status_code == 200:
            # Job exists — patch just the <script> CDATA in the existing config so
            # we preserve Jenkins' own plugin version attributes (full replace → 500).
            self._update_jenkins_job_script(session, job_name, base)
            return

        resp = session.post(
            f"{base}/createItem",
            params={"name": job_name},
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
        session = self._jenkins_session()

        check = session.get(
            f"{base}/credentials/store/system/domain/_/credential/{credential_id}/api/json",
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
        resp = session.post(
            f"{base}/credentials/store/system/domain/_/createCredentials",
            data={"json": _json.dumps(payload)},
            timeout=15,
        )
        # Jenkins returns 200 or 302 on success
        if resp.status_code not in (200, 201, 302):
            raise RuntimeError(
                f"Failed to create Jenkins credential '{credential_id}': {resp.status_code} {resp.text}"
            )

    # ── Codespace orchestration ────────────────────────────────────────────

    def _codespace_exists(self, name: str) -> bool:
        """Return True if the Codespace still exists in GitHub."""
        resp = requests.get(
            f"{GITHUB_API}/user/codespaces/{name}",
            headers=self._gh_headers(),
            timeout=15,
        )
        return resp.status_code != 404

    def _record_new_codespace(self, name: str) -> None:
        """Persist a newly created Codespace and reset all Jenkins state tied to the old one."""
        self._state["codespace_name"] = name
        for key in ("jenkins_passphrase", "jenkins_api_token"):
            self._state.pop(key, None)
        self._save_state()

    def _provision_codespace(self) -> str:
        """Create Codespace (or reuse one previously created by this script), set jenkins_url."""
        existing = self._state.get("codespace_name")
        if existing and self._codespace_exists(existing):
            if self.confirm(
                f"Reuse existing Codespace '{existing}'?",
                default=True,
            ):
                name = existing
            else:
                if self.confirm(f"Delete '{existing}'?", default=False):
                    try:
                        self._delete_codespace(existing)
                        print(f"  Codespace '{existing}' deleted ✓")
                    except Exception as e:
                        print(f"  Failed to delete Codespace: {e}", file=sys.stderr)
                name = self._create_codespace()
                self._record_new_codespace(name)
        else:
            if existing:
                print(f"  Saved Codespace '{existing}' no longer exists — creating a new one.")
                self._state.pop("codespace_name", None)
            name = self._create_codespace()
            self._record_new_codespace(name)

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
        jenkins_url = self._answers["jenkins_url"].rstrip("/")
        yaml_content = WORKFLOW_TEMPLATE_PATH.read_text().replace("JENKINS_BASE_URL", jenkins_url)

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
        while time.time() - start < 120:
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
        raise TimeoutError("Timed out waiting for workflow to complete (2 min)")

    # ── Steps ──────────────────────────────────────────────────────────────

    def steps(self) -> list[tuple[str, callable]]:
        step_list = []
        if self._answers.get("use_codespace"):
            step_list.append(("Provisioning Jenkins in GitHub Codespaces", self._provision_codespace))
            step_list.append(("Waiting for Jenkins to be ready", self._wait_for_jenkins))
            step_list.append(("Setting random Jenkins admin password", self._set_jenkins_admin_password))
            step_list.append(("Configuring Jenkins root URL", self._configure_jenkins_root_url))
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

        if self._answers.get("use_codespace") and jenkins_url:
            print(f"\nJenkins (browser login):")
            print(f"  URL:      {_hyperlink(jenkins_url)}")
            print(f"  Username: {JENKINS_DEFAULT_USERNAME}")
            print(f"  Password: {JENKINS_DEFAULT_TOKEN}")
            print(f"  Note: Jenkins is open for demo — no login required to trigger builds")

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
