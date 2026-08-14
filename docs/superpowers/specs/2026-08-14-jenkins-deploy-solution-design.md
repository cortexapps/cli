# Jenkins Deploy Solution Design

**Date:** 2026-08-14
**Status:** Approved

## Overview

A Cortex CLI solution (`jenkins-deploy`) that enables customers to track Jenkins pipeline deploys in Cortex. Mirrors the `github-actions-deploy` and `harness-deploy` solutions in structure and async callback pattern. Includes optional GitHub Codespaces provisioning of a Jenkins instance via the GitHub REST API so customers can demo/explore without a pre-existing Jenkins setup.

---

## Solution Components

```
cortexapps_cli/solutions/jenkins-deploy/
  setup.py
  README.md
  _templates/
    Jenkinsfile                        # Groovy pipeline seeded into Jenkins
    trigger-jenkins-deploy.yaml        # Cortex workflow definition
  catalog/
    jenkins-demo.yaml                  # Sample Cortex service entity
  scorecards/
    deploy-health.yaml                 # Deploy health scorecard

.devcontainer/jenkins/
  devcontainer.json                    # GitHub Codespaces devcontainer definition
  docker-compose.yml                   # Jenkins container
  jenkins.yaml                         # JCasC — pre-configured, no setup wizard
```

---

## Setup Flow (`setup.py`)

Extends `SolutionSetup` base class, following the same pattern as `HarnessDeploySetup`.

### Prompts (collected via `collect_prompts`)

1. Cortex entity tag
2. Cortex API key (secret)
3. Cortex base URL
4. "Spin up Jenkins in a GitHub Codespace? [Y/n]"
   - **If Y:** GitHub PAT (secret, `codespace` scope required)
   - **If N:** Jenkins URL, Jenkins username, Jenkins API token (secret)

### Steps (executed via `steps`)

**Codespace path (Y):**
1. `POST /repos/cortexapps/cli/codespaces` with `devcontainer_path: .devcontainer/jenkins/devcontainer.json`
2. Poll `GET /user/codespaces/{name}` until `state == "Available"` (with timeout/backoff)
3. `PATCH /user/codespaces/{name}/ports/8080/visibility` → `"public"`
4. Derive Jenkins URL: `https://{codespace_name}-8080.app.github.dev`
5. Use `admin` as Jenkins username; password is fixed in JCasC (prompted before Codespace creation and passed as environment variable, or auto-generated and printed)

**Both paths continue:**
6. Seed Jenkins job via `POST {jenkins_url}/createItem?name=cortex-deploy` with XML job config (wrapping the Jenkinsfile as a Pipeline-from-SCM or inline script)
7. Add credentials to Jenkins credential store via REST API:
   - `CORTEX_API_KEY` (secret text)
   - `CORTEX_BASE_URL` (secret text)
8. Write Jenkins coordinates to entity custom metadata via Cortex API:
   ```json
   { "jenkins": { "url": "...", "job": "cortex-deploy", "username": "admin", "token": "..." } }
   ```
9. Import Cortex workflow (`trigger-jenkins-deploy`)
10. _(Optional)_ Trigger test deploy and poll for deploy registration in Cortex

### State Persistence
Answers saved to `~/.cortex/solutions/jenkins-deploy.json` via base class. Secrets (PAT, API token, Cortex API key) are not persisted.

---

## Cortex Workflow (`trigger-jenkins-deploy.yaml`)

Three actions, same structure as `trigger-harness-deploy.yaml`:

### Action 1 — Get Jenkins config
- Type: HTTP GET
- Endpoint: `GET /api/v1/catalog/{tag}/custom-data/jenkins`
- Extracts Jenkins coordinates from entity custom metadata

### Action 2 — Parse config
- Type: JQ expression
- Extracts: `url`, `job`, `username`, `token` from custom metadata response

### Action 3 — Trigger Jenkins build
- Type: `HTTP_REQUEST_ASYNC`
- Endpoint: `POST {url}/job/{job}/buildWithParameters`
- Auth: HTTP Basic (`username:token`, Base64-encoded, passed as `Authorization` header)
- Parameters: `callback_url` (Cortex async callback URL), `cortex_entity_tag`
- Jenkins credentials stored in entity custom metadata (simplest approach; no Cortex HTTP integration required)

---

## Jenkinsfile (Groovy Pipeline)

```
pipeline {
  agent any
  parameters {
    string(name: 'callback_url',       defaultValue: '', description: 'Cortex async callback URL')
    string(name: 'cortex_entity_tag',  defaultValue: '', description: 'Cortex entity tag')
  }
  environment {
    CORTEX_API_KEY  = credentials('CORTEX_API_KEY')
    CORTEX_BASE_URL = credentials('CORTEX_BASE_URL')
  }
  stages {
    stage('Build') {
      steps {
        echo 'Placeholder for real deploy steps'
      }
    }
    stage('Record Deploy') {
      steps {
        // POST to /api/v1/catalog/{tag}/deploys
        // Captures: BUILD_URL, BUILD_ID, GIT_COMMIT, executor username, timestamp
      }
    }
  }
  post {
    always {
      // POST to callback_url with SUCCESS or FAILURE status
      // Includes: BUILD_URL, BUILD_ID, pipeline name
    }
  }
}
```

Key points:
- `callback_url` and `cortex_entity_tag` injected as build parameters by the Cortex workflow
- Credentials fetched from Jenkins credential store (not hardcoded)
- `post { always { ... } }` ensures callback fires even on build failure
- Uses `curl` for HTTP calls (available in the Jenkins container)

---

## Catalog Entity (`jenkins-demo.yaml`)

```yaml
openapi: 3.0.1
info:
  title: Jenkins Demo
  x-cortex-tag: jenkins-demo
  x-cortex-type: service
  x-cortex-groups:
    - demo-jenkins-deploys
  x-cortex-custom-metadata:
    jenkins:
      url: ""        # filled in by setup.py
      job: cortex-deploy
      username: admin
      token: ""      # filled in by setup.py
```

---

## Scorecard (`deploy-health.yaml`)

Tag: `jenkins-deploy-health`
Scoped to group: `demo-jenkins-deploys`
Three-level ladder identical to other deploy solutions:

- **Bronze:** 1+ deploys in last year
- **Silver:** 1+ deploys in last 30 days
- **Gold:** 1+ deploys in last 7 days

---

## Devcontainer

### `devcontainer.json`
- Base image: `mcr.microsoft.com/devcontainers/base:ubuntu`
- Uses Docker Compose (`docker-compose.yml`)
- `postCreateCommand`: waits for Jenkins to be healthy (polls `/login`)
- Pre-installed tools: `cortex` CLI (via pip), `curl`, `jq`
- Forwarded port: 8080 (Jenkins UI)

### `docker-compose.yml`
- Service: `jenkins` using `jenkins/jenkins:lts` official image
- Mounts JCasC config file
- Sets env vars: `JAVA_OPTS=-Djenkins.install.runSetupWizard=false`, `CASC_JENKINS_CONFIG=/var/jenkins_home/casc_configs/jenkins.yaml`
- Plugins pre-installed: `pipeline`, `http_request`, `credentials`, `git`, `configuration-as-code`, `workflow-aggregator`

### `jenkins.yaml` (JCasC)
- Admin user: `admin` / password from env var `JENKINS_ADMIN_PASSWORD` (prompted during setup, passed at Codespace creation via `machine.env`)
- Security realm: local (username/password)
- Authorization: logged-in users can do anything (demo simplicity)
- Setup wizard: disabled via `JAVA_OPTS`

---

## Credentials Storage Design

Jenkins credentials for the Cortex workflow to authenticate when triggering builds are stored in **entity custom metadata** (`x-cortex-custom-metadata.jenkins.token`). This avoids requiring a Cortex HTTP integration and keeps the setup self-contained. The token is a Jenkins API token (not the user password).

This is intentionally a demo-friendly tradeoff. The README will note that production deployments should use a Cortex HTTP integration with credential vaulting.

---

## Error Handling

- **Codespace creation:** timeout after N minutes with a clear message; surface GitHub API error responses
- **Jenkins not ready:** poll `/login` with exponential backoff before attempting job creation
- **Job already exists:** `createItem` returns 400 — handle with `--replace-existing` behavior (delete + recreate)
- **Test deploy:** poll Cortex deploys endpoint for up to 5 minutes; report timeout gracefully

---

## Testing

- `tests/test_jenkins.py` following the pattern of `test_catalog.py`
- Requires `JENKINS_URL`, `JENKINS_USERNAME`, `JENKINS_API_TOKEN` env vars (pointing at a real or Codespace Jenkins)
- Tests: install solution, trigger deploy, verify deploy registered in Cortex, verify scorecard evaluates correctly
- Mark serial: setup/teardown affect shared Jenkins state

---

## README

Covers:
- Architecture diagram: `Cortex Workflow → Jenkins API → Jenkinsfile → Cortex Deploys API + Callback`
- Two setup paths (Codespace vs. existing Jenkins)
- How to roll out to real services (replace placeholder Build stage, point workflow at real job)
- Production note: use Cortex HTTP integration instead of custom metadata for credentials
