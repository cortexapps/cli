# GitHub Actions Deploy Solution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `github-actions-deploy` Cortex solution with a demo entity, deploy health scorecard, GitHub Actions workflow template, and an interactive post-install setup script that creates and seeds a GitHub repo end-to-end.

**Architecture:** Four layers: (1) solution content files installed via existing backup import; (2) a shared `SolutionSetup` base class in `solutions/_lib/` for reusable setup infrastructure; (3) a solution-specific `setup.py` using the GitHub API to create/seed a repo and set secrets; (4) CLI additions — `--skip-post-install-setup` on `install` and a new `post-install` subcommand.

**Tech Stack:** Python 3.11+, Typer, requests (existing), PyNaCl (new — for GitHub secret encryption)

## Global Constraints

- All commits include `Linear: CX-6` in body
- Branch: `cx-6-github-actions-deploy-solution` off `main`
- `_`-prefixed dirs already excluded from `_list_solution_tags` (line 155 of solutions.py) — no change needed
- `requests` is already a dependency — no change needed
- Only new dependency: `PyNaCl >= 1.5.0`
- Solution tag: `github-actions-deploy`
- Demo entity tag: `github-actions-demo`
- Demo group: `demo-github-actions-deploys`
- State file: `~/.cortex/setup-{solution_tag}.json`

---

## File Map

**Create:**
- `cortexapps_cli/solutions/github-actions-deploy/README.md`
- `cortexapps_cli/solutions/github-actions-deploy/catalog/github-actions-demo.yaml`
- `cortexapps_cli/solutions/github-actions-deploy/scorecards/deploy-health.yaml`
- `cortexapps_cli/solutions/github-actions-deploy/_templates/cortex-deploy.yml`
- `cortexapps_cli/solutions/github-actions-deploy/setup.py`
- `cortexapps_cli/solutions/_lib/__init__.py`
- `cortexapps_cli/solutions/_lib/setup_base.py`
- `tests/test_setup_base.py`
- `tests/test_github_actions_setup.py`
- `tests/test_solutions_postinstall.py`

**Modify:**
- `pyproject.toml` — add PyNaCl dependency
- `cortexapps_cli/commands/solutions.py` — add `_has_post_install`, `_run_post_install_script`, `post_install` subcommand, `--skip-post-install-setup` on `install`

---

### Task 1: Create Feature Branch

- [ ] **Step 1: Create branch**

```bash
git checkout -b cx-6-github-actions-deploy-solution
```

- [ ] **Step 2: Verify**

```bash
git branch --show-current
```
Expected: `cx-6-github-actions-deploy-solution`

---

### Task 2: Solution Content Files

**Files:**
- Create: `cortexapps_cli/solutions/github-actions-deploy/README.md`
- Create: `cortexapps_cli/solutions/github-actions-deploy/catalog/github-actions-demo.yaml`
- Create: `cortexapps_cli/solutions/github-actions-deploy/scorecards/deploy-health.yaml`
- Create: `cortexapps_cli/solutions/github-actions-deploy/_templates/cortex-deploy.yml`

**Interfaces:**
- Produces: installable solution discoverable by `cortex solutions list` and `cortex solutions info -s github-actions-deploy`

- [ ] **Step 1: Create README.md**

`cortexapps_cli/solutions/github-actions-deploy/README.md`:
```markdown
---
name: GitHub Actions Deploy Tracking
description: Track deployments from GitHub Actions in Cortex, with a deploy health scorecard measuring delivery cadence.
---

## What's Included

- **Entity:** `github-actions-demo` service — a sample entity to receive deploy events
- **Scorecard:** Deploy Health — Bronze/Silver/Gold based on deploy frequency
- **GitHub Actions workflow:** A two-job workflow (build → deploy notification) to seed into a GitHub repo
- **Setup script:** Interactive wizard that creates and seeds a GitHub repo end-to-end

## Quick Start

1. Install the solution:

   ```
   cortex solutions install -s github-actions-deploy
   ```

2. Follow the post-install setup prompts, or run later:

   ```
   cortex solutions post-install -s github-actions-deploy
   ```

## How It Works

The included GitHub Actions workflow fires a deploy event to Cortex after every successful build.
The `notify-cortex` job only runs if the `build` job succeeds, demonstrating conditional deploy tracking.

## Customizing for Production

- Point the workflow at your real entity by replacing `github-actions-demo` with your service tag
- Add `CORTEX_API_KEY` and `CORTEX_BASE_URL` secrets to your real repos
- The Deploy Health scorecard is scoped to `demo-github-actions-deploys` to avoid affecting your
  existing services. To roll it out broadly, remove the group filter from the scorecard.
  To opt in individual services, add the `demo-github-actions-deploys` group to them.
```

- [ ] **Step 2: Create catalog entity**

`cortexapps_cli/solutions/github-actions-deploy/catalog/github-actions-demo.yaml`:
```yaml
openapi: "3.0.0"
info:
  title: GitHub Actions Demo
  x-cortex-tag: github-actions-demo
  x-cortex-type: service
  x-cortex-description: Sample service for demonstrating deploy tracking via GitHub Actions.
  x-cortex-definition: {}
  x-cortex-groups:
    - demo-github-actions-deploys
```

- [ ] **Step 3: Create scorecard**

`cortexapps_cli/solutions/github-actions-deploy/scorecards/deploy-health.yaml`:
```yaml
tag: deploy-health
name: Deploy Health
description: Measures deployment cadence for services using GitHub Actions deploy tracking. Scoped to demo-github-actions-deploys group by default — remove the filter to apply to all services.
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
  query: hasGroup("demo-github-actions-deploys")
ladder:
  name: Default Ladder
  levels:
    - name: Bronze
      rank: 1
      description: Service has at least one recorded deployment.
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
    description: At least one deployment event has been recorded for this service.
    expression: deploys().count() > 0
    weight: 1
    level: Bronze

  - title: Deployed in the last 30 days
    description: A deployment was recorded within the past 30 days.
    expression: deploys(lookback=duration("P30D")).count() > 0
    weight: 1
    level: Silver

  - title: Deployed in the last 7 days
    description: A deployment was recorded within the past 7 days, indicating an active delivery cadence.
    expression: deploys(lookback=duration("P7D")).count() > 0
    weight: 1
    level: Gold
```

- [ ] **Step 4: Create GitHub Actions workflow template**

`cortexapps_cli/solutions/github-actions-deploy/_templates/cortex-deploy.yml`:
```yaml
name: Cortex Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Build
        run: echo "Hello, Cortex deploys!"

  notify-cortex:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Register deploy in Cortex
        run: |
          curl -s -f -X POST \
            "${{ secrets.CORTEX_BASE_URL }}/api/v1/catalog/github-actions-demo/deploys" \
            -H "Authorization: Bearer ${{ secrets.CORTEX_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "sha": "${{ github.sha }}",
              "environment": "production",
              "type": "DEPLOY",
              "title": "Triggered by ${{ github.actor }}",
              "deployer": { "name": "${{ github.actor }}" },
              "customData": {
                "branch": "${{ github.ref_name }}",
                "runId": "${{ github.run_id }}",
                "runUrl": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}",
                "trigger": "${{ github.event_name }}"
              }
            }'
```

- [ ] **Step 5: Verify solution is discoverable**

```bash
poetry run cortex solutions list
poetry run cortex solutions info -s github-actions-deploy
```
Expected: `github-actions-deploy` appears in list; README renders with "What's Included" section.

- [ ] **Step 6: Commit**

```bash
git add cortexapps_cli/solutions/github-actions-deploy/
git commit -m "$(cat <<'EOF'
add: github-actions-deploy solution content files

Catalog entity, deploy health scorecard, GitHub Actions workflow template,
and README for the GitHub Actions deploy tracking solution.

Linear: CX-6

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: SolutionSetup Base Class

**Files:**
- Create: `cortexapps_cli/solutions/_lib/__init__.py`
- Create: `cortexapps_cli/solutions/_lib/setup_base.py`
- Create: `tests/test_setup_base.py`

**Interfaces:**
- Produces:
  - `SolutionSetup` importable from `cortexapps_cli.solutions._lib.setup_base`
  - `SolutionSetup.solution_tag: str` — set by subclass
  - `SolutionSetup.prompt(key, message, env_var=None, default=None, secret=False) -> str`
  - `SolutionSetup.confirm(message, default=True) -> bool`
  - `SolutionSetup.already_done(key) -> bool`
  - `SolutionSetup.mark_done(key) -> None`
  - `SolutionSetup.collect_prompts() -> None` — abstract
  - `SolutionSetup.steps() -> list[tuple[str, callable]]` — abstract
  - `SolutionSetup.post_steps() -> None` — optional hook, default no-op
  - `SolutionSetup.run() -> None`

- [ ] **Step 1: Write failing tests**

`tests/test_setup_base.py`:
```python
import json
import pytest
from pathlib import Path
from unittest.mock import patch
from cortexapps_cli.solutions._lib.setup_base import SolutionSetup


class ConcreteSetup(SolutionSetup):
    solution_tag = "test-solution"
    steps_called = []

    def collect_prompts(self):
        self._answers["name"] = self.prompt("name", "Your name", default="Alice")

    def steps(self):
        return [("Do thing", lambda: ConcreteSetup.steps_called.append(True))]


def test_prompt_uses_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv("MY_VAR", "from-env")
    setup = ConcreteSetup(state_dir=tmp_path)
    result = setup.prompt("key", "Enter value", env_var="MY_VAR")
    assert result == "from-env"


def test_prompt_uses_default_on_empty_input(tmp_path, monkeypatch):
    monkeypatch.delenv("MY_VAR", raising=False)
    setup = ConcreteSetup(state_dir=tmp_path)
    with patch("builtins.input", return_value=""):
        result = setup.prompt("key", "Enter value", default="default-val")
    assert result == "default-val"


def test_prompt_uses_user_input(tmp_path, monkeypatch):
    monkeypatch.delenv("MY_VAR", raising=False)
    setup = ConcreteSetup(state_dir=tmp_path)
    with patch("builtins.input", return_value="user-value"):
        result = setup.prompt("key", "Enter value", default="default-val")
    assert result == "user-value"


def test_confirm_returns_true_for_y(tmp_path):
    setup = ConcreteSetup(state_dir=tmp_path)
    with patch("builtins.input", return_value="y"):
        assert setup.confirm("Do it?") is True


def test_confirm_returns_false_for_n(tmp_path):
    setup = ConcreteSetup(state_dir=tmp_path)
    with patch("builtins.input", return_value="n"):
        assert setup.confirm("Do it?") is False


def test_confirm_uses_default_on_empty(tmp_path):
    setup = ConcreteSetup(state_dir=tmp_path)
    with patch("builtins.input", return_value=""):
        assert setup.confirm("Do it?", default=True) is True
    with patch("builtins.input", return_value=""):
        assert setup.confirm("Do it?", default=False) is False


def test_already_done_false_initially(tmp_path):
    setup = ConcreteSetup(state_dir=tmp_path)
    assert setup.already_done("step1") is False


def test_mark_done_persists(tmp_path):
    setup = ConcreteSetup(state_dir=tmp_path)
    setup.mark_done("step1")
    assert setup.already_done("step1") is True


def test_mark_done_persists_across_instances(tmp_path):
    ConcreteSetup(state_dir=tmp_path).mark_done("step1")
    assert ConcreteSetup(state_dir=tmp_path).already_done("step1") is True


def test_state_file_path(tmp_path):
    setup = ConcreteSetup(state_dir=tmp_path)
    assert setup._state_file == tmp_path / "setup-test-solution.json"


def test_post_steps_called_after_steps(tmp_path):
    post_called = []

    class SetupWithPost(ConcreteSetup):
        def post_steps(self):
            post_called.append(True)

    setup = SetupWithPost(state_dir=tmp_path)
    with patch("builtins.input", return_value=""):
        setup.run()
    assert post_called == [True]
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
poetry run pytest tests/test_setup_base.py -v
```
Expected: `ModuleNotFoundError` for `cortexapps_cli.solutions._lib.setup_base`

- [ ] **Step 3: Create `_lib/__init__.py`**

`cortexapps_cli/solutions/_lib/__init__.py` — empty file.

- [ ] **Step 4: Implement `setup_base.py`**

`cortexapps_cli/solutions/_lib/setup_base.py`:
```python
import json
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class SolutionSetup(ABC):
    """
    Base class for solution post-install setup scripts.
    Subclasses define solution_tag, collect_prompts(), and steps().
    """

    solution_tag: str  # must be set by subclass

    def __init__(self, state_dir: Optional[Path] = None):
        self._answers: dict = {}
        state_dir = state_dir or Path.home() / ".cortex"
        state_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = state_dir / f"setup-{self.solution_tag}.json"
        self._state: dict = self._load_state()

    def _load_state(self) -> dict:
        if self._state_file.exists():
            try:
                return json.loads(self._state_file.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_state(self) -> None:
        self._state_file.write_text(json.dumps(self._state, indent=2))

    def prompt(
        self,
        key: str,
        message: str,
        env_var: Optional[str] = None,
        default: Optional[str] = None,
        secret: bool = False,
    ) -> str:
        """Prompt for a value. Uses env var if set, then prompts with optional default."""
        if env_var:
            env_val = os.environ.get(env_var)
            if env_val:
                masked = "********" if secret else env_val
                print(f"{message} [{masked} from {env_var}]")
                self._answers[key] = env_val
                return env_val

        prompt_str = message
        if default:
            prompt_str += f" [{default}]"
        prompt_str += ": "

        value = input(prompt_str).strip()
        if not value:
            value = default or ""
        self._answers[key] = value
        return value

    def confirm(self, message: str, default: bool = True) -> bool:
        """Y|N confirmation prompt."""
        hint = "[Y/n]" if default else "[y/N]"
        response = input(f"{message} {hint}: ").strip().lower()
        if not response:
            return default
        return response in ("y", "yes")

    def already_done(self, key: str) -> bool:
        """Return True if this step was previously completed."""
        return self._state.get(key, False)

    def mark_done(self, key: str) -> None:
        """Mark a step as completed in the persistent state file."""
        self._state[key] = True
        self._save_state()

    @abstractmethod
    def collect_prompts(self) -> None:
        """Collect all user inputs upfront before executing steps."""

    @abstractmethod
    def steps(self) -> list[tuple[str, callable]]:
        """Return ordered list of (label, callable) tuples."""

    def post_steps(self) -> None:
        """Optional hook called after all steps complete. Override in subclass."""

    def run(self) -> None:
        """Collect prompts then execute steps with progress display."""
        self.collect_prompts()
        print()
        step_list = self.steps()
        total = len(step_list)
        for i, (label, fn) in enumerate(step_list, 1):
            try:
                fn()
                print(f"[{i}/{total}] {label}... \u2713")
            except Exception as e:
                print(f"[{i}/{total}] {label}... \u2717  {e}", file=sys.stderr)
                raise SystemExit(1)
        self.post_steps()
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
poetry run pytest tests/test_setup_base.py -v
```
Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add cortexapps_cli/solutions/_lib/ tests/test_setup_base.py
git commit -m "$(cat <<'EOF'
add: SolutionSetup base class for reusable post-install setup scripts

Provides prompt collection with env var fallback, Y/N confirmation,
idempotency state tracking via ~/.cortex/setup-{solution}.json, step
execution with progress display, and post_steps() hook for subclasses.

Linear: CX-6

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Add PyNaCl Dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add to `[tool.poetry.dependencies]` in `pyproject.toml`**

```toml
PyNaCl = ">=1.5.0"
```

- [ ] **Step 2: Install**

```bash
poetry install
```

- [ ] **Step 3: Verify**

```bash
poetry run python -c "from nacl import encoding, public; print('PyNaCl OK')"
```
Expected: `PyNaCl OK`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml poetry.lock
git commit -m "$(cat <<'EOF'
add: PyNaCl dependency for GitHub secret encryption

Required by github-actions-deploy setup script to encrypt secrets
before storing them via the GitHub API (libsodium sealed box).

Linear: CX-6

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: GitHub Actions Deploy Setup Script

**Files:**
- Create: `cortexapps_cli/solutions/github-actions-deploy/setup.py`
- Create: `tests/test_github_actions_setup.py`

**Interfaces:**
- Consumes: `SolutionSetup` from `cortexapps_cli.solutions._lib.setup_base`
- Produces: `GitHubActionsSetup` class and `main()` callable by `cortex solutions post-install`

- [ ] **Step 1: Write failing tests**

`tests/test_github_actions_setup.py`:
```python
import base64
import importlib.util
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def load_setup_module():
    spec = importlib.util.spec_from_file_location(
        "github_actions_setup",
        "cortexapps_cli/solutions/github-actions-deploy/setup.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return load_setup_module()


@pytest.fixture
def setup(mod, tmp_path):
    instance = mod.GitHubActionsSetup(state_dir=tmp_path)
    instance._answers = {
        "github_token": "ghp_test",
        "github_owner": "test-org",
        "repo_name": "cortex-deploy-demo",
        "cortex_api_key": "crt_testkey",
        "cortex_base_url": "https://api.getcortexapp.com",
    }
    return instance


def test_get_authenticated_user(setup):
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"login": "test-user"}
    with patch("requests.get", return_value=resp):
        assert setup._get_authenticated_user() == "test-user"


def test_create_repo_skips_if_exists(setup):
    resp = MagicMock(status_code=200)
    with patch("requests.get", return_value=resp) as mock_get, \
         patch("requests.post") as mock_post:
        setup._create_repo()
    mock_get.assert_called_once()
    mock_post.assert_not_called()


def test_create_repo_creates_when_missing(setup):
    user_resp = MagicMock(status_code=200)
    user_resp.json.return_value = {"login": "test-org"}
    check_resp = MagicMock(status_code=404)
    post_resp = MagicMock(status_code=201)
    post_resp.json.return_value = {"html_url": "https://github.com/test-org/cortex-deploy-demo"}

    get_responses = [check_resp, user_resp]
    with patch("requests.get", side_effect=get_responses), \
         patch("requests.post", return_value=post_resp) as mock_post:
        setup._create_repo()
    mock_post.assert_called_once()


def test_seed_workflow_skips_if_unchanged(setup, tmp_path):
    # Read the actual template to simulate matching content
    template_path = Path("cortexapps_cli/solutions/github-actions-deploy/_templates/cortex-deploy.yml")
    content = template_path.read_text()
    content_b64 = base64.b64encode(content.encode()).decode()

    resp = MagicMock(status_code=200)
    resp.json.return_value = {"content": content_b64, "sha": "abc123"}

    with patch("requests.get", return_value=resp), \
         patch("requests.put") as mock_put:
        setup._seed_workflow()
    mock_put.assert_not_called()


def test_seed_workflow_creates_when_missing(setup):
    get_resp = MagicMock(status_code=404)
    put_resp = MagicMock(status_code=201)
    put_resp.json.return_value = {"content": {"sha": "abc123"}}

    with patch("requests.get", return_value=get_resp), \
         patch("requests.put", return_value=put_resp) as mock_put:
        setup._seed_workflow()
    mock_put.assert_called_once()


def test_set_secret(setup):
    # 32-byte key for valid libsodium public key
    dummy_key = base64.b64encode(b"\x00" * 32).decode()
    key_resp = MagicMock(status_code=200)
    key_resp.json.return_value = {"key_id": "key123", "key": dummy_key}
    key_resp.raise_for_status = MagicMock()

    put_resp = MagicMock(status_code=204)

    with patch("requests.get", return_value=key_resp), \
         patch("requests.put", return_value=put_resp) as mock_put:
        setup._set_secret("CORTEX_API_KEY", "crt_testkey")

    mock_put.assert_called_once()
    call_json = mock_put.call_args.kwargs["json"]
    assert "encrypted_value" in call_json
    assert call_json["key_id"] == "key123"


def test_trigger_workflow(setup):
    resp = MagicMock(status_code=204)
    with patch("requests.post", return_value=resp) as mock_post:
        setup._trigger_workflow()
    url = mock_post.call_args.args[0]
    assert "dispatches" in url
    assert mock_post.call_args.kwargs["json"] == {"ref": "main"}


def test_main_callable(mod):
    assert callable(mod.main)
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
poetry run pytest tests/test_github_actions_setup.py -v
```
Expected: failures (setup.py missing)

- [ ] **Step 3: Implement `setup.py`**

`cortexapps_cli/solutions/github-actions-deploy/setup.py`:
```python
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
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
poetry run pytest tests/test_github_actions_setup.py -v
```
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add cortexapps_cli/solutions/github-actions-deploy/setup.py tests/test_github_actions_setup.py
git commit -m "$(cat <<'EOF'
add: github-actions-deploy post-install setup script

Interactive wizard that creates a GitHub repo, seeds the Cortex deploy
workflow, sets CORTEX_API_KEY and CORTEX_BASE_URL secrets, and optionally
triggers the first workflow run. All steps are idempotent.

Linear: CX-6

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: CLI Integration — `post-install` Subcommand + Install Hook

**Files:**
- Modify: `cortexapps_cli/commands/solutions.py`
- Create: `tests/test_solutions_postinstall.py`

**Interfaces:**
- Produces:
  - `cortex solutions post-install -s github-actions-deploy` → runs setup script
  - `cortex solutions post-install -s ai-agents` → "No post-install setup available"
  - `cortex solutions install -s github-actions-deploy` → prompts for post-install after import
  - `cortex solutions install -s github-actions-deploy --skip-post-install-setup` → skips prompt

- [ ] **Step 1: Write failing tests**

`tests/test_solutions_postinstall.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from cortexapps_cli.cli import app

runner = CliRunner()


def test_post_install_no_setup_for_ai_agents():
    result = runner.invoke(app, ["solutions", "post-install", "-s", "ai-agents"])
    assert result.exit_code == 0
    assert "No post-install setup available" in result.output


def test_post_install_unknown_solution():
    result = runner.invoke(app, ["solutions", "post-install", "-s", "nonexistent-xyz"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_post_install_calls_run_for_github_actions():
    with patch("cortexapps_cli.commands.solutions._run_post_install_script") as mock_run:
        runner.invoke(app, ["solutions", "post-install", "-s", "github-actions-deploy"])
    mock_run.assert_called_once_with("github-actions-deploy", solutions_dir=None)
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
poetry run pytest tests/test_solutions_postinstall.py -v
```
Expected: failures (`post-install` subcommand doesn't exist yet)

- [ ] **Step 3: Add `_has_post_install` and `_run_post_install_script` helpers to `solutions.py`**

Add after the existing `_get_readme` function (after line ~177):

```python
def _has_post_install(tag: str, path: str | None = None) -> bool:
    """Return True if this solution has a post-install setup.py."""
    try:
        (_solutions_root(path) / tag / "setup.py").read_bytes()
        return True
    except Exception:
        return False


def _run_post_install_script(solution_tag: str, solutions_dir: str | None = None) -> None:
    """Find and invoke the solution's setup.py main() function."""
    import importlib.util

    root = _solutions_root(solutions_dir)
    try:
        with as_file(root / solution_tag / "setup.py") as setup_path:
            if not setup_path.exists():
                typer.echo("No post-install setup available for this solution.")
                return
            spec = importlib.util.spec_from_file_location(f"{solution_tag}_setup", setup_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.main()
    except FileNotFoundError:
        typer.echo("No post-install setup available for this solution.")
```

- [ ] **Step 4: Add `post_install` subcommand to `solutions.py`**

Add after the `install` command (after line ~661):

```python
@app.command(name="post-install")
def post_install(
    ctx: typer.Context,
    solution: str = typer.Option(..., "--solution", "-s", help="Solution tag"),
):
    """Run post-install setup for a solution."""
    solutions_dir = ctx.obj.get("solutions_dir") if ctx.obj else None
    if solution not in _list_solution_tags(solutions_dir):
        avail = ", ".join(_list_solution_tags(solutions_dir))
        typer.echo(f"Error: Solution '{solution}' not found. Available: {avail}")
        raise typer.Exit(1)
    _run_post_install_script(solution, solutions_dir=solutions_dir)
```

- [ ] **Step 5: Add `--skip-post-install-setup` to `install` and inject post-install hook**

In the `install` command signature (line ~603), add the new option:
```python
skip_post_install_setup: bool = typer.Option(
    False,
    "--skip-post-install-setup",
    help="Skip the post-install setup script prompt",
    is_flag=True,
),
```

After line 644 (end of import report display), before the `if not no_prompt:` block, insert:
```python
    # Post-install setup hook — runs before the informational menu
    if not no_prompt and not skip_post_install_setup and _has_post_install(solution, solutions_dir):
        typer.echo("\nThis solution includes a post-install setup script.")
        if typer.confirm("Run setup now?", default=True):
            _run_post_install_script(solution, solutions_dir=solutions_dir)
        else:
            typer.echo(f"\nRun setup later with: cortex solutions post-install -s {solution}")
    elif skip_post_install_setup and _has_post_install(solution, solutions_dir):
        typer.echo(f"\nRun setup later with: cortex solutions post-install -s {solution}")
```

- [ ] **Step 6: Run tests — verify they pass**

```bash
poetry run pytest tests/test_solutions_postinstall.py -v
```
Expected: all PASS

- [ ] **Step 7: Run existing solutions tests for regressions**

```bash
poetry run pytest tests/test_solutions.py -v
```
Expected: all PASS

- [ ] **Step 8: Smoke test CLI**

```bash
poetry run cortex solutions list
poetry run cortex solutions info -s github-actions-deploy
poetry run cortex solutions post-install -s ai-agents
```
Expected: `github-actions-deploy` in list; README renders; "No post-install setup available" for ai-agents.

- [ ] **Step 9: Commit**

```bash
git add cortexapps_cli/commands/solutions.py tests/test_solutions_postinstall.py
git commit -m "$(cat <<'EOF'
feat: add solutions post-install subcommand and install hook

- New `cortex solutions post-install -s <solution>` subcommand
- `cortex solutions install` prompts for post-install setup when setup.py present
- `--skip-post-install-setup` flag bypasses the prompt
- Helper functions _has_post_install and _run_post_install_script for reuse

Linear: CX-6

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review Checklist

| Spec Requirement | Task |
|---|---|
| Solution content files (entity, scorecard, template, README) | Task 2 |
| Entity with `demo-github-actions-deploys` group | Task 2 |
| Scorecard scoped to group with production note | Task 2 |
| `_templates/` convention for external files | Task 2 |
| `SolutionSetup` base class | Task 3 |
| `_lib/` shared directory, excluded from solutions list | Task 3 (already filtered) |
| Two-job GH workflow with `needs: build` | Task 2 |
| customData with branch/runId/runUrl/trigger | Task 2 |
| CORTEX_API_KEY + CORTEX_BASE_URL secrets | Tasks 2, 5 |
| Prompt for GH token, owner (derived), repo, API key, base URL | Task 5 |
| Idempotency per step via API checks | Task 5 |
| "Ready to trigger?" confirm via `post_steps()` | Tasks 3, 5 |
| PyNaCl for secret encryption | Task 4 |
| `cortex solutions post-install -s <solution>` | Task 6 |
| `--skip-post-install-setup` flag | Task 6 |
| Post-install prompt in `install` flow | Task 6 |
| "No post-install setup available" for other solutions | Task 6 |
| "Run later" message when skipped | Task 6 |
| Reusable base class pattern for future solutions | Task 3 |
