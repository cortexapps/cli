# Jenkins Deploy Solution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `jenkins-deploy` Cortex CLI solution that seeds a Jenkins pipeline, records deploys in Cortex via the deploys API, and optionally provisions a Jenkins instance in GitHub Codespaces via the GitHub REST API.

**Architecture:** Mirrors the `harness-deploy` solution structure — `setup.py` extends `SolutionSetup`, prompts for credentials, seeds a Jenkins job via the Jenkins REST API, writes Jenkins coordinates to entity custom metadata, and imports a Cortex workflow that triggers builds via HTTP. A `.devcontainer/jenkins/` directory in the repo root enables one-click Jenkins provisioning in GitHub Codespaces via `gh` or the GitHub API.

**Tech Stack:** Python 3.11+, `requests`, Jenkins REST API, GitHub Codespaces REST API, Jenkins Configuration as Code (JCasC), Groovy (Jenkinsfile), Cortex Workflows YAML

**Spec:** `docs/superpowers/specs/2026-08-14-jenkins-deploy-solution-design.md`

## Global Constraints

- Python 3.11+ (match project minimum from `pyproject.toml`)
- Follow `SolutionSetup` base class contract exactly: `solution_tag`, `collect_prompts()`, `steps()`, `post_steps()`
- All secrets use `secret=True` in `self.prompt()` — never persisted to JSON
- Jenkins admin credentials for demo: username `admin`, password `cortex-demo` (fixed in JCasC)
- Jenkins job name: `cortex-deploy` (default, user-overridable)
- Entity custom metadata key: `jenkins` with fields `url`, `job`, `username`, `token`
- Cortex workflow tag: `jenkins-trigger-deploy`
- Solution tag: `jenkins-deploy`
- Scorecard tag: `jenkins-deploy-health`, group filter: `demo-jenkins-deploys`
- No native Cortex Jenkins integration — Cortex workflow uses direct HTTP with Basic auth from custom metadata
- State file: `~/.cortex/solutions/jenkins-deploy.json` (handled by base class)
- Test pattern: `importlib.util.spec_from_file_location` to load `setup.py`, mock `requests.*`
- Test file: `tests/test_jenkins_deploy_setup.py`

---

## File Map

**Create:**
- `cortexapps_cli/solutions/jenkins-deploy/setup.py` — main setup class
- `cortexapps_cli/solutions/jenkins-deploy/README.md` — usage and adaptation guide
- `cortexapps_cli/solutions/jenkins-deploy/_templates/Jenkinsfile` — Groovy pipeline template
- `cortexapps_cli/solutions/jenkins-deploy/_templates/trigger-jenkins-deploy.yaml` — Cortex workflow
- `cortexapps_cli/solutions/jenkins-deploy/catalog/jenkins-demo.yaml` — sample entity
- `cortexapps_cli/solutions/jenkins-deploy/scorecards/deploy-health.yaml` — deploy health scorecard
- `.devcontainer/jenkins/devcontainer.json` — Codespaces devcontainer config
- `.devcontainer/jenkins/Dockerfile` — custom Jenkins image with pre-installed plugins
- `.devcontainer/jenkins/docker-compose.yml` — Jenkins + devcontainer services
- `.devcontainer/jenkins/jenkins.yaml` — JCasC config (no setup wizard, admin/cortex-demo)
- `tests/test_jenkins_deploy_setup.py` — unit tests

**Do not modify any existing files.**

---

### Task 1: Static solution files (catalog, scorecard, scaffold)

**Files:**
- Create: `cortexapps_cli/solutions/jenkins-deploy/catalog/jenkins-demo.yaml`
- Create: `cortexapps_cli/solutions/jenkins-deploy/scorecards/deploy-health.yaml`
- Test: `tests/test_jenkins_deploy_setup.py` (initial scaffold only)

**Interfaces:**
- Produces: `jenkins-demo` entity with `x-cortex-custom-metadata.jenkins` placeholder block; `jenkins-deploy-health` scorecard scoped to `demo-jenkins-deploys`

- [ ] **Step 1: Create the catalog entity**

```yaml
# cortexapps_cli/solutions/jenkins-deploy/catalog/jenkins-demo.yaml
openapi: "3.0.0"
info:
  title: Jenkins Demo
  x-cortex-tag: jenkins-demo
  x-cortex-type: service
  x-cortex-description: Sample service for demonstrating deploy tracking via Jenkins pipelines.
  x-cortex-definition: {}
  x-cortex-groups:
    - demo-jenkins-deploys
  x-cortex-custom-metadata:
    jenkins:
      url: PLACEHOLDER_JENKINS_URL
      job: cortex-deploy
      username: admin
      token: PLACEHOLDER_JENKINS_TOKEN
```

- [ ] **Step 2: Create the scorecard**

```yaml
# cortexapps_cli/solutions/jenkins-deploy/scorecards/deploy-health.yaml
tag: jenkins-deploy-health
name: Jenkins Deploy Health
description: Measures deployment cadence for services using Jenkins deploy tracking. Scoped to demo-jenkins-deploys group by default — remove the filter to apply to all services.
draft: false
notifications:
  enabled: true
  scoreDropNotificationsEnabled: true
exemptions:
  enabled: true
  autoApprove: false
evaluation:
  window: 24
filter:
  kind: GENERIC
  types:
    include:
      - service
  query: hasGroup("demo-jenkins-deploys")
ladder:
  name: Default Ladder
  levels:
    - name: Bronze
      rank: 1
      description: Service has at least one recorded deployment in the last year.
      color: "#CD7F32"
    - name: Silver
      rank: 2
      description: Service has deployed within the last 30 days.
      color: "#C0C0C0"
    - name: Gold
      rank: 3
      description: Service has deployed within the last 7 days.
      color: "#D7AC58"
rules:
  - title: Has at least one deploy
    description: At least one deployment has been recorded in the last year.
    expression: deploys(lookback=duration("P1Y")).length > 0
    weight: 1
    level: Bronze

  - title: Deployed in the last 30 days
    description: A deployment was recorded within the past 30 days.
    expression: deploys(lookback=duration("P30D")).length > 0
    weight: 1
    level: Silver

  - title: Deployed in the last 7 days
    description: A deployment was recorded within the past 7 days, indicating an active delivery cadence.
    expression: deploys(lookback=duration("P7D")).length > 0
    weight: 1
    level: Gold
```

- [ ] **Step 3: Write a minimal test scaffold and verify it runs**

```python
# tests/test_jenkins_deploy_setup.py
import importlib.util
import pytest
from pathlib import Path


def load_setup_module():
    spec = importlib.util.spec_from_file_location(
        "jenkins_deploy_setup",
        "cortexapps_cli/solutions/jenkins-deploy/setup.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_yaml_is_valid():
    import yaml
    path = Path("cortexapps_cli/solutions/jenkins-deploy/catalog/jenkins-demo.yaml")
    data = yaml.safe_load(path.read_text())
    assert data["info"]["x-cortex-tag"] == "jenkins-demo"
    meta = data["info"]["x-cortex-custom-metadata"]["jenkins"]
    assert "url" in meta
    assert "job" in meta
    assert "username" in meta
    assert "token" in meta


def test_scorecard_yaml_is_valid():
    import yaml
    path = Path("cortexapps_cli/solutions/jenkins-deploy/scorecards/deploy-health.yaml")
    data = yaml.safe_load(path.read_text())
    assert data["tag"] == "jenkins-deploy-health"
    assert len(data["rules"]) == 3
    levels = {r["level"] for r in data["rules"]}
    assert levels == {"Bronze", "Silver", "Gold"}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /path/to/worktree
poetry run pytest tests/test_jenkins_deploy_setup.py::test_catalog_yaml_is_valid tests/test_jenkins_deploy_setup.py::test_scorecard_yaml_is_valid -v
```

Expected: PASS (the setup.py import will fail — that's OK, these tests don't import it yet)

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/jenkins-deploy/catalog/ \
        cortexapps_cli/solutions/jenkins-deploy/scorecards/ \
        tests/test_jenkins_deploy_setup.py
git commit -m "feat: add jenkins-deploy catalog entity and scorecard"
```

---

### Task 2: Jenkinsfile template

**Files:**
- Create: `cortexapps_cli/solutions/jenkins-deploy/_templates/Jenkinsfile`
- Test: `tests/test_jenkins_deploy_setup.py` (add tests)

**Interfaces:**
- Produces: Groovy pipeline with `callback_url` and `cortex_entity_tag` string parameters; stages Build, Record Deploy; `post { always }` callback block
- Consumes: Jenkins credentials `CORTEX_API_KEY` (secret text), `CORTEX_BASE_URL` (secret text)

- [ ] **Step 1: Write the Jenkinsfile**

```groovy
// cortexapps_cli/solutions/jenkins-deploy/_templates/Jenkinsfile
pipeline {
    agent any
    parameters {
        string(name: 'callback_url',      defaultValue: '', description: 'Cortex async callback URL')
        string(name: 'cortex_entity_tag', defaultValue: '', description: 'Cortex entity tag')
    }
    environment {
        CORTEX_API_KEY  = credentials('CORTEX_API_KEY')
        CORTEX_BASE_URL = credentials('CORTEX_BASE_URL')
    }
    stages {
        stage('Build') {
            steps {
                echo 'Placeholder for real deploy steps'
                // Replace this echo with your actual build and deploy commands
            }
        }
        stage('Record Deploy') {
            steps {
                script {
                    def timestamp = sh(script: 'date -u +%Y-%m-%dT%H:%M:%SZ', returnStdout: true).trim()
                    def payload = """{"sha":"${env.BUILD_NUMBER}","timestamp":"${timestamp}","environment":"production","type":"DEPLOY","title":"Build #${env.BUILD_NUMBER}","deployer":{"name":"Jenkins"},"customData":{"buildUrl":"${env.BUILD_URL}","buildNumber":"${env.BUILD_NUMBER}","jobName":"${env.JOB_NAME}"}}"""
                    sh """
                        curl -s -f -X POST \\
                          "\${CORTEX_BASE_URL}/api/v1/catalog/${params.cortex_entity_tag}/deploys" \\
                          -H "Authorization: Bearer \${CORTEX_API_KEY}" \\
                          -H "Content-Type: application/json" \\
                          -d '${payload}' || true
                    """
                }
            }
        }
    }
    post {
        always {
            script {
                if (params.callback_url) {
                    def status = currentBuild.currentResult == 'SUCCESS' ? 'SUCCESS' : 'FAILURE'
                    def payload = """{"status":"${status}","message":"Jenkins pipeline ${status.toLowerCase()}","response":{"buildUrl":"${env.BUILD_URL}","buildNumber":"${env.BUILD_NUMBER}","jobName":"${env.JOB_NAME}"}}"""
                    withEnv(["CALLBACK_URL=${params.callback_url}"]) {
                        sh """
                            curl -s -X POST "\$CALLBACK_URL" \\
                              -H "Content-Type: application/json" \\
                              -H "Authorization: Bearer \${CORTEX_API_KEY}" \\
                              -d '${payload}' || true
                        """
                    }
                }
            }
        }
    }
}
```

- [ ] **Step 2: Add test for Jenkinsfile structure**

Add to `tests/test_jenkins_deploy_setup.py`:

```python
def test_jenkinsfile_has_required_elements():
    path = Path("cortexapps_cli/solutions/jenkins-deploy/_templates/Jenkinsfile")
    content = path.read_text()
    assert "callback_url" in content
    assert "cortex_entity_tag" in content
    assert "CORTEX_API_KEY" in content
    assert "CORTEX_BASE_URL" in content
    assert "/deploys" in content
    assert "post {" in content
    assert "always {" in content
    assert "CALLBACK_URL" in content
```

- [ ] **Step 3: Run the test**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py::test_jenkinsfile_has_required_elements -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add cortexapps_cli/solutions/jenkins-deploy/_templates/Jenkinsfile \
        tests/test_jenkins_deploy_setup.py
git commit -m "feat: add Jenkinsfile template with Cortex deploy recording and async callback"
```

---

### Task 3: Cortex workflow template

**Files:**
- Create: `cortexapps_cli/solutions/jenkins-deploy/_templates/trigger-jenkins-deploy.yaml`
- Test: `tests/test_jenkins_deploy_setup.py` (add tests)

**Interfaces:**
- Produces: Cortex workflow YAML with four actions: GET custom data, JQ parse (extracts url/job/auth), SET_VARIABLES, HTTP_REQUEST_ASYNC to Jenkins
- Consumes: entity custom metadata `jenkins.url`, `jenkins.job`, `jenkins.username`, `jenkins.token`

- [ ] **Step 1: Write the workflow YAML**

```yaml
# cortexapps_cli/solutions/jenkins-deploy/_templates/trigger-jenkins-deploy.yaml
name: "Solution: Trigger Jenkins Deploy"
tag: jenkins-trigger-deploy
description: |
  Triggers a Jenkins pipeline and waits for it to report completion back to Cortex,
  registering a deploy event on the target entity. No inputs required — Jenkins
  coordinates (url, job, username, token) are read from the entity's custom metadata.
isDraft: false
isRunnableViaApi: true
filter:
  type: ENTITY
variables:
  - slug: jenkins-url
    type: STRING
    defaultValue: ""
  - slug: jenkins-job
    type: STRING
    defaultValue: ""
  - slug: jenkins-auth
    type: STRING
    defaultValue: ""
runResponseTemplate: |
  # Jenkins Deploy — Complete

  **Job:** [{{variables.jenkins-job}}]({{variables.jenkins-url}}/job/{{variables.jenkins-job}})

  **Cortex Deploys:** [see deploys for {{context.entity.tag}}](https://app.getcortexapp.com/admin/resources?tag={{context.entity.tag}})

  ---

  ## How this workflow works

  This Cortex workflow triggered a deploy in Jenkins and waited for it to finish.

  **1. Cortex read the entity's Jenkins configuration**

  The workflow fetched `x-cortex-custom-metadata.jenkins` from this entity to determine
  which Jenkins instance and job to trigger — no manual input required.

  **2. Cortex triggered the Jenkins build**

  It called the Jenkins `buildWithParameters` API, passing a one-time callback URL as
  the `callback_url` build parameter and the entity tag as `cortex_entity_tag`.

  **3. Jenkins ran the pipeline**

  The `cortex-deploy` pipeline runs two stages:

  - **Build** — your deploy steps (replace `echo "Placeholder"` with your real commands)

  - **Record Deploy** — POSTs a deploy event to `/api/v1/catalog/{tag}/deploys`, recording
    build number, URL, and job name. This feeds the Deploy Health scorecard.

  The `post { always { ... } }` block POSTs the final status (SUCCESS/FAILURE) to the
  callback URL — which is how Cortex knows the workflow run is done.

  **4. Cortex received the callback**

  When Jenkins posted to the callback URL, Cortex marked this workflow run complete.

  ---

  ## Adapting this to your own pipelines

  1. Replace `echo 'Placeholder for real deploy steps'` in the Build stage with your actual deploy commands

  2. Add the Record Deploy and callback steps to any existing Jenkinsfile — they only need
     the `CORTEX_API_KEY` and `CORTEX_BASE_URL` credentials plus the two build parameters

  3. Add `x-cortex-custom-metadata.jenkins` to your entity's catalog YAML with
     `url`, `job`, `username`, and `token` fields pointing at your real Jenkins job
actions:
- name: Get Jenkins config
  slug: get-jenkins-config
  schema:
    type: HTTP_REQUEST
    httpMethod: GET
    url: "https://api.getcortexapp.com/api/v1/catalog/{{context.entity.tag}}/custom-data/jenkins"
    headers:
      Authorization: "Bearer {{&context.secrets.cortex_api_key}}"
      Content-Type: application/json
    integration: null
    integrationAlias: null
  outgoingActions:
  - parse-jenkins-config
  isRootAction: true
- name: Parse Jenkins config
  slug: parse-jenkins-config
  schema:
    type: JQ
    expression: |
      .actions."get-jenkins-config".outputs.body.value as $j |
      if ($j == null or $j.url == null) then
        error("No Jenkins configuration found. Add x-cortex-custom-metadata.jenkins with url, job, username, and token to this entity.")
      else
        {
          url: $j.url,
          job: $j.job,
          auth: ("Basic " + (($j.username + ":" + $j.token) | @base64))
        }
      end
  outgoingActions:
  - set-variables
  isRootAction: false
- name: Set variables
  slug: set-variables
  schema:
    type: SET_VARIABLES
    variables:
    - slug: jenkins-url
      source:
        path: actions.parse-jenkins-config.outputs.result.url
        type: REFERENCE
    - slug: jenkins-job
      source:
        path: actions.parse-jenkins-config.outputs.result.job
        type: REFERENCE
    - slug: jenkins-auth
      source:
        path: actions.parse-jenkins-config.outputs.result.auth
        type: REFERENCE
  outgoingActions:
  - trigger-deploy
  isRootAction: false
- name: Trigger Jenkins Build
  slug: trigger-deploy
  schema:
    type: HTTP_REQUEST_ASYNC
    httpMethod: POST
    url: "{{variables.jenkins-url}}/job/{{variables.jenkins-job}}/buildWithParameters?callback_url={{{callbackUrl}}}&cortex_entity_tag={{context.entity.tag}}"
    integration: null
    integrationAlias: null
    headers:
      Authorization: "{{variables.jenkins-auth}}"
      Content-Type: application/x-www-form-urlencoded
    timeoutInSeconds: 300
  outgoingActions: []
  isRootAction: false
```

- [ ] **Step 2: Add test for workflow YAML structure**

Add to `tests/test_jenkins_deploy_setup.py`:

```python
def test_workflow_yaml_is_valid():
    import yaml
    path = Path("cortexapps_cli/solutions/jenkins-deploy/_templates/trigger-jenkins-deploy.yaml")
    data = yaml.safe_load(path.read_text())
    assert data["tag"] == "jenkins-trigger-deploy"
    slugs = {a["slug"] for a in data["actions"]}
    assert slugs == {"get-jenkins-config", "parse-jenkins-config", "set-variables", "trigger-deploy"}
    root_actions = [a for a in data["actions"] if a["isRootAction"]]
    assert len(root_actions) == 1
    async_action = next(a for a in data["actions"] if a["slug"] == "trigger-deploy")
    assert async_action["schema"]["type"] == "HTTP_REQUEST_ASYNC"
    assert "buildWithParameters" in async_action["schema"]["url"]
    assert "@base64" in data["actions"][1]["schema"]["expression"]
```

- [ ] **Step 3: Run the test**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py::test_workflow_yaml_is_valid -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add cortexapps_cli/solutions/jenkins-deploy/_templates/trigger-jenkins-deploy.yaml \
        tests/test_jenkins_deploy_setup.py
git commit -m "feat: add Cortex workflow template for triggering Jenkins deploys"
```

---

### Task 4: Devcontainer files

**Files:**
- Create: `.devcontainer/jenkins/Dockerfile`
- Create: `.devcontainer/jenkins/docker-compose.yml`
- Create: `.devcontainer/jenkins/jenkins.yaml`
- Create: `.devcontainer/jenkins/devcontainer.json`

No unit tests — these are infrastructure config files verified by Codespace smoke test in README.

**Interfaces:**
- Produces: A Codespace devcontainer that boots Jenkins at port 8080 with admin/cortex-demo credentials, no setup wizard, required plugins pre-installed

- [ ] **Step 1: Write the Dockerfile**

Jenkins LTS with required plugins pre-installed via `jenkins-plugin-cli`:

```dockerfile
# .devcontainer/jenkins/Dockerfile
FROM jenkins/jenkins:lts-jdk17

USER root
RUN apt-get update && apt-get install -y curl jq && rm -rf /var/lib/apt/lists/*
USER jenkins

# Pre-install plugins: pipeline, credentials, JCasC, Plain Credentials binding
RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    pipeline-model-definition \
    configuration-as-code \
    plain-credentials \
    credentials-binding \
    git \
    http_request \
    build-user-vars-plugin

ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
ENV CASC_JENKINS_CONFIG="/var/jenkins_home/casc_configs/jenkins.yaml"
```

- [ ] **Step 2: Write the JCasC config**

```yaml
# .devcontainer/jenkins/jenkins.yaml
jenkins:
  numExecutors: 2
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "cortex-demo"
  authorizationStrategy:
    loggedInUsersCanDoAnything:
      allowAnonymousRead: false
  remotingSecurity:
    enabled: true
unclassified:
  location:
    url: ""
```

- [ ] **Step 3: Write docker-compose.yml**

Two services: `jenkins` (the Jenkins server) and `devcontainer` (the VS Code workspace):

```yaml
# .devcontainer/jenkins/docker-compose.yml
version: "3.8"
services:
  devcontainer:
    image: mcr.microsoft.com/devcontainers/base:ubuntu-22.04
    volumes:
      - ../..:/workspace:cached
    command: sleep infinity

  jenkins:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./jenkins.yaml:/var/jenkins_home/casc_configs/jenkins.yaml
      - jenkins_home:/var/jenkins_home

volumes:
  jenkins_home:
```

- [ ] **Step 4: Write devcontainer.json**

```json
{
  "name": "Cortex Jenkins Demo",
  "dockerComposeFile": "docker-compose.yml",
  "service": "devcontainer",
  "workspaceFolder": "/workspace",
  "postCreateCommand": "pip install cortexapps-cli && bash -c 'until curl -s -o /dev/null -w \"%{http_code}\" http://jenkins:8080/login | grep -q 200; do echo \"Waiting for Jenkins...\"; sleep 5; done; echo \"Jenkins is ready at port 8080\"'",
  "forwardPorts": [8080],
  "portsAttributes": {
    "8080": {
      "label": "Jenkins UI",
      "onAutoForward": "notify"
    }
  },
  "remoteUser": "vscode"
}
```

- [ ] **Step 5: Commit**

```bash
git add .devcontainer/jenkins/
git commit -m "feat: add Jenkins devcontainer for GitHub Codespaces"
```

---

### Task 5: setup.py — class scaffold + prompts + Codespace API helpers

**Files:**
- Create: `cortexapps_cli/solutions/jenkins-deploy/setup.py` (partial — prompts + Codespace helpers only)
- Test: `tests/test_jenkins_deploy_setup.py` (add tests)

**Interfaces:**
- Produces:
  - `JenkinsDeploySetup(state_dir, cortex_api_key, cortex_base_url, no_prompt)` class
  - `collect_prompts()` — sets `_answers` keys: `cortex_api_key`, `cortex_base_url`, `entity_tag`, `use_codespace`, `github_pat`, `jenkins_url`, `jenkins_username`, `jenkins_token`, `jenkins_job`
  - `_create_codespace() -> str` — returns codespace name
  - `_wait_for_codespace(name: str) -> None` — polls until `state == "Available"`
  - `_expose_jenkins_port(name: str) -> str` — makes port 8080 public, returns Jenkins URL
- Consumes: `SolutionSetup` base class from `cortexapps_cli/solutions/_lib/setup_base.py`

- [ ] **Step 1: Write failing tests for Codespace helpers**

Add to `tests/test_jenkins_deploy_setup.py`:

```python
@pytest.fixture
def mod():
    return load_setup_module()

@pytest.fixture
def setup(mod, tmp_path):
    instance = mod.JenkinsDeploySetup(state_dir=tmp_path)
    instance._answers = {
        "github_pat": "ghp_test",
        "jenkins_url": "http://jenkins.example.com:8080",
        "jenkins_username": "admin",
        "jenkins_token": "cortex-demo",
        "jenkins_job": "cortex-deploy",
        "entity_tag": "jenkins-demo",
        "cortex_api_key": "crt_testkey",
        "cortex_base_url": "https://api.getcortexapp.com",
    }
    return instance

def test_create_codespace_returns_name(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=201)
    resp.json.return_value = {"name": "cortexapps-cli-abc123"}
    with patch("requests.post", return_value=resp):
        name = setup._create_codespace()
    assert name == "cortexapps-cli-abc123"

def test_create_codespace_raises_on_failure(setup):
    from unittest.mock import patch, MagicMock
    import pytest
    resp = MagicMock(status_code=422)
    resp.text = "Unprocessable Entity"
    with patch("requests.post", return_value=resp):
        with pytest.raises(RuntimeError, match="Failed to create Codespace"):
            setup._create_codespace()

def test_expose_jenkins_port_returns_url(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=200)
    with patch("requests.patch", return_value=resp):
        url = setup._expose_jenkins_port("my-codespace-abc")
    assert url == "https://my-codespace-abc-8080.app.github.dev"

def test_wait_for_codespace_polls_until_available(setup):
    from unittest.mock import patch, MagicMock
    pending = MagicMock(status_code=200)
    pending.json.return_value = {"state": "Starting"}
    ready = MagicMock(status_code=200)
    ready.json.return_value = {"state": "Available"}
    with patch("requests.get", side_effect=[pending, ready]), \
         patch("time.sleep"):
        setup._wait_for_codespace("my-codespace-abc")  # should not raise
```

- [ ] **Step 2: Run tests to see them fail**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py::test_create_codespace_returns_name -v
```

Expected: FAIL with `ModuleNotFoundError` or `AttributeError` (setup.py doesn't exist yet)

- [ ] **Step 3: Write setup.py with class scaffold, prompts, and Codespace helpers**

```python
# cortexapps_cli/solutions/jenkins-deploy/setup.py
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


def main(**kwargs):
    JenkinsDeploySetup(**kwargs).run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the Codespace helper tests**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py::test_create_codespace_returns_name \
                  tests/test_jenkins_deploy_setup.py::test_create_codespace_raises_on_failure \
                  tests/test_jenkins_deploy_setup.py::test_expose_jenkins_port_returns_url \
                  tests/test_jenkins_deploy_setup.py::test_wait_for_codespace_polls_until_available -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/jenkins-deploy/setup.py \
        tests/test_jenkins_deploy_setup.py
git commit -m "feat: add JenkinsDeploySetup class with prompts and Codespace provisioning"
```

---

### Task 6: setup.py — Jenkins API helpers

**Files:**
- Modify: `cortexapps_cli/solutions/jenkins-deploy/setup.py` (add Jenkins helpers)
- Test: `tests/test_jenkins_deploy_setup.py` (add tests)

**Interfaces:**
- Produces:
  - `_jenkins_auth() -> tuple[str, str]` — returns `(username, token)` for `requests` auth param
  - `_wait_for_jenkins() -> None` — polls `GET {url}/login` until HTTP 200
  - `_create_jenkins_job() -> None` — POST to `/createItem` with XML wrapping the Jenkinsfile; skips if job exists
  - `_add_jenkins_credential(credential_id: str, secret: str, description: str) -> None` — POST to credentials API; skips if exists
- Consumes: `_answers["jenkins_url"]`, `_answers["jenkins_username"]`, `_answers["jenkins_token"]`, `_answers["jenkins_job"]`, `JENKINSFILE_TEMPLATE_PATH`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_jenkins_deploy_setup.py`:

```python
def test_jenkins_auth(setup):
    assert setup._jenkins_auth() == ("admin", "cortex-demo")

def test_wait_for_jenkins_polls_until_200(setup):
    from unittest.mock import patch, MagicMock
    fail = MagicMock(status_code=503)
    ok = MagicMock(status_code=200)
    with patch("requests.get", side_effect=[fail, ok]), \
         patch("time.sleep"):
        setup._wait_for_jenkins()  # should not raise

def test_create_jenkins_job_skips_if_exists(setup):
    from unittest.mock import patch, MagicMock
    exists_resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=exists_resp) as mock_get, \
         patch("requests.post") as mock_post:
        setup._create_jenkins_job()
    mock_get.assert_called_once()
    mock_post.assert_not_called()

def test_create_jenkins_job_creates_when_missing(setup):
    from unittest.mock import patch, MagicMock
    missing_resp = MagicMock(status_code=404)
    created_resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=missing_resp), \
         patch("requests.post", return_value=created_resp) as mock_post:
        setup._create_jenkins_job()
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "application/xml" in call_kwargs.kwargs.get("headers", {}).get("Content-Type", "")

def test_add_jenkins_credential_skips_if_exists(setup):
    from unittest.mock import patch, MagicMock
    exists_resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=exists_resp) as mock_get, \
         patch("requests.post") as mock_post:
        setup._add_jenkins_credential("CORTEX_API_KEY", "secret", "Cortex API key")
    mock_get.assert_called_once()
    mock_post.assert_not_called()

def test_add_jenkins_credential_creates_when_missing(setup):
    from unittest.mock import patch, MagicMock
    missing_resp = MagicMock(status_code=404)
    created_resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=missing_resp), \
         patch("requests.post", return_value=created_resp) as mock_post:
        setup._add_jenkins_credential("CORTEX_API_KEY", "secret", "Cortex API key")
    mock_post.assert_called_once()
```

- [ ] **Step 2: Run tests to see them fail**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py::test_jenkins_auth \
                  tests/test_jenkins_deploy_setup.py::test_create_jenkins_job_skips_if_exists -v
```

Expected: FAIL with `AttributeError` (methods not yet implemented)

- [ ] **Step 3: Add Jenkins helpers to setup.py**

Add these methods to the `JenkinsDeploySetup` class, after `collect_prompts`:

```python
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
```

- [ ] **Step 4: Run all Jenkins helper tests**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py::test_jenkins_auth \
                  tests/test_jenkins_deploy_setup.py::test_wait_for_jenkins_polls_until_200 \
                  tests/test_jenkins_deploy_setup.py::test_create_jenkins_job_skips_if_exists \
                  tests/test_jenkins_deploy_setup.py::test_create_jenkins_job_creates_when_missing \
                  tests/test_jenkins_deploy_setup.py::test_add_jenkins_credential_skips_if_exists \
                  tests/test_jenkins_deploy_setup.py::test_add_jenkins_credential_creates_when_missing -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/jenkins-deploy/setup.py \
        tests/test_jenkins_deploy_setup.py
git commit -m "feat: add Jenkins job and credential creation helpers to JenkinsDeploySetup"
```

---

### Task 7: setup.py — Cortex steps, steps(), and post_steps()

**Files:**
- Modify: `cortexapps_cli/solutions/jenkins-deploy/setup.py` (add Cortex steps + steps() + post_steps())
- Test: `tests/test_jenkins_deploy_setup.py` (add tests)

**Interfaces:**
- Produces:
  - `_provision_codespace() -> str` — orchestrates create + wait + expose; sets `_answers["jenkins_url"]`; returns detail string
  - `_write_entity_custom_metadata() -> None` — PATCH to Cortex `/api/v1/open-api`
  - `_import_cortex_workflow() -> None` — POST to Cortex `/api/v1/workflows`
  - `_trigger_via_cortex_workflow() -> dict` — POST run + poll to terminal state
  - `steps() -> list[tuple[str, callable]]` — ordered step list
  - `post_steps() -> None` — summary + optional test trigger
- Consumes: all `_answers` keys set in Tasks 5 and 6

- [ ] **Step 1: Write failing tests**

Add to `tests/test_jenkins_deploy_setup.py`:

```python
def test_write_entity_custom_metadata(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=200)
    with patch("requests.patch", return_value=resp) as mock_patch:
        setup._write_entity_custom_metadata()
    mock_patch.assert_called_once()
    call_kwargs = mock_patch.call_args
    assert "open-api" in call_kwargs.args[0]
    body = call_kwargs.kwargs["data"].decode()
    assert "jenkins-demo" in body
    assert "jenkins_url" not in body  # the value, not the key
    assert "http://jenkins.example.com:8080" in body
    assert "cortex-deploy" in body

def test_import_cortex_workflow(setup):
    from unittest.mock import patch, MagicMock
    resp = MagicMock(status_code=201)
    with patch("requests.post", return_value=resp) as mock_post:
        setup._import_cortex_workflow()
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "workflows" in call_kwargs.args[0]
    assert call_kwargs.kwargs["headers"]["Content-Type"] == "application/yaml"

def test_steps_returns_expected_list(setup):
    setup._answers["use_codespace"] = False
    step_labels = [label for label, _ in setup.steps()]
    assert "Creating Jenkins deploy job" in step_labels
    assert "Adding CORTEX_API_KEY credential to Jenkins" in step_labels
    assert "Adding CORTEX_BASE_URL credential to Jenkins" in step_labels
    assert "Writing Jenkins config to entity custom metadata" in step_labels
    assert "Importing Cortex trigger workflow" in step_labels

def test_steps_includes_codespace_when_enabled(setup):
    setup._answers["use_codespace"] = True
    step_labels = [label for label, _ in setup.steps()]
    assert "Provisioning Jenkins in GitHub Codespaces" in step_labels

def test_main_callable(mod):
    assert callable(mod.main)
```

- [ ] **Step 2: Run tests to see them fail**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py::test_write_entity_custom_metadata \
                  tests/test_jenkins_deploy_setup.py::test_steps_returns_expected_list -v
```

Expected: FAIL with `AttributeError`

- [ ] **Step 3: Add Cortex steps to setup.py**

Add these methods to `JenkinsDeploySetup`, then add `steps()` and `post_steps()`:

```python
    # ── Codespace orchestration ────────────────────────────────────────────

    def _provision_codespace(self) -> str:
        """Create Codespace, wait for it to be ready, expose port, set jenkins_url."""
        name = self._create_codespace()
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
```

- [ ] **Step 4: Run all new tests**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py::test_write_entity_custom_metadata \
                  tests/test_jenkins_deploy_setup.py::test_import_cortex_workflow \
                  tests/test_jenkins_deploy_setup.py::test_steps_returns_expected_list \
                  tests/test_jenkins_deploy_setup.py::test_steps_includes_codespace_when_enabled \
                  tests/test_jenkins_deploy_setup.py::test_main_callable -v
```

Expected: PASS

- [ ] **Step 5: Run the full test suite for this file**

```bash
poetry run pytest tests/test_jenkins_deploy_setup.py -v
```

Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add cortexapps_cli/solutions/jenkins-deploy/setup.py \
        tests/test_jenkins_deploy_setup.py
git commit -m "feat: add Cortex integration steps and orchestration to JenkinsDeploySetup"
```

---

### Task 8: README

**Files:**
- Create: `cortexapps_cli/solutions/jenkins-deploy/README.md`

No unit tests — documentation file.

- [ ] **Step 1: Write the README**

```markdown
# Jenkins Deploy Solution

Track Jenkins pipeline deploys in Cortex. Each deploy is recorded via the Cortex Deploys API
and surfaces in your entity's deploy history and on the Deploy Health scorecard.

## How it works

```
Cortex Workflow → Jenkins buildWithParameters API → Jenkinsfile runs
  → Stage: Record Deploy  → POST /api/v1/catalog/{tag}/deploys
  → post { always }       → POST callback_url (SUCCESS or FAILURE)
                              → Cortex marks workflow run complete
```

The workflow uses an async callback pattern: Cortex triggers Jenkins and waits for Jenkins
to POST back when the pipeline finishes. Jenkins coordinates (URL, job, credentials) are
stored in the entity's `x-cortex-custom-metadata.jenkins` block.

## Setup

```bash
cortex solutions install -s jenkins-deploy
```

The setup script will:

1. Ask whether to provision Jenkins in GitHub Codespaces (recommended for first-time demo)
2. Create the `cortex-deploy` pipeline job in Jenkins
3. Add `CORTEX_API_KEY` and `CORTEX_BASE_URL` as Jenkins credentials
4. Write Jenkins coordinates to the entity's custom metadata
5. Import the **Trigger Jenkins Deploy** Cortex workflow
6. Optionally trigger a test deploy

### GitHub Codespaces path

Select **Y** when prompted. You'll need a GitHub Personal Access Token with `codespace` scope.

A Codespace is provisioned from `.devcontainer/jenkins/` in this repository. Jenkins boots
with admin credentials (`admin` / `cortex-demo`) pre-configured via Jenkins Configuration
as Code (no setup wizard). Port 8080 is made publicly accessible so the Cortex workflow
can reach it.

### Existing Jenkins path

Select **N** when prompted. You'll need:
- Jenkins URL (e.g. `https://jenkins.example.com`)
- Jenkins username and API token (or password)

The account needs permission to create jobs and credentials.

## Triggering a deploy

**Via CLI:**
```bash
cortex workflows run -t jenkins-trigger-deploy --scope ENTITY --entity jenkins-demo
```

**Via UI:** Open the entity in Cortex → Workflows tab → **Solution: Trigger Jenkins Deploy** → Run

## Rolling out to your own services

1. **Adapt the Jenkinsfile** — replace `echo 'Placeholder for real deploy steps'` in the
   Build stage with your real build and deploy commands. The Record Deploy stage and
   `post { always }` callback block can be added to any existing pipeline.

2. **Add Jenkins credentials** — the pipeline requires `CORTEX_API_KEY` and `CORTEX_BASE_URL`
   secret-text credentials in your Jenkins instance.

3. **Add custom metadata** to your entity's catalog YAML:

```yaml
x-cortex-custom-metadata:
  jenkins:
    url: "https://jenkins.example.com"
    job: "your-pipeline-name"
    username: "your-username"
    token: "your-api-token"
```

4. The **Trigger Jenkins Deploy** workflow will pick up the new entity automatically —
   no workflow changes needed.

## Production note

This solution stores Jenkins credentials in entity custom metadata for demo simplicity.
In production, use a Cortex HTTP integration with credential vaulting instead, and
restrict the Jenkins user to the minimum permissions needed (Build: Execute).

## Deploy Health scorecard

The **Jenkins Deploy Health** scorecard (`jenkins-deploy-health`) measures deploy cadence
for services in the `demo-jenkins-deploys` group:

| Level  | Requirement                  |
|--------|------------------------------|
| Bronze | 1+ deploy in the last year   |
| Silver | 1+ deploy in the last 30 days |
| Gold   | 1+ deploy in the last 7 days |

Remove the `hasGroup("demo-jenkins-deploys")` filter to apply to all services.
```

- [ ] **Step 2: Commit**

```bash
git add cortexapps_cli/solutions/jenkins-deploy/README.md
git commit -m "docs: add jenkins-deploy solution README"
```

---

## Self-Review Checklist

After all tasks are complete, run this verification:

```bash
# All tests pass
poetry run pytest tests/test_jenkins_deploy_setup.py -v

# YAML files are valid
python -c "import yaml; yaml.safe_load(open('cortexapps_cli/solutions/jenkins-deploy/catalog/jenkins-demo.yaml'))"
python -c "import yaml; yaml.safe_load(open('cortexapps_cli/solutions/jenkins-deploy/scorecards/deploy-health.yaml'))"
python -c "import yaml; yaml.safe_load(open('cortexapps_cli/solutions/jenkins-deploy/_templates/trigger-jenkins-deploy.yaml'))"

# Setup module loads cleanly
python -c "import importlib.util; spec = importlib.util.spec_from_file_location('s', 'cortexapps_cli/solutions/jenkins-deploy/setup.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK')"

# All solution files present
ls cortexapps_cli/solutions/jenkins-deploy/
ls .devcontainer/jenkins/
```
