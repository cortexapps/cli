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
