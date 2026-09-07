"""
Post-install setup script for the monorepo solution.
Configures a GitHub Personal Access Token integration in Cortex so that
the cortexapps/cli public repo can be used for GitOps discovery.

Run via: cortex solutions post-install -s monorepo
"""

import sys
from pathlib import Path

import requests

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

GITHUB_API = "https://api.github.com"
TARGET_REPO = "cortexapps/cli"


def _hyperlink(url: str, text: str = None) -> str:
    label = text if text is not None else url
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"


class MonorepoSetup(SolutionSetup):
    solution_tag = "monorepo"

    def __init__(self, cortex_api_key: str = None, cortex_base_url: str = None, no_prompt: bool = False, **kwargs):
        super().__init__(no_prompt=no_prompt, **kwargs)
        self._session_api_key = cortex_api_key
        self._session_base_url = cortex_base_url

    def _cortex_headers(self) -> dict:
        key = self._answers.get("cortex_api_key") or self._session_api_key or ""
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def _gh_headers(self) -> dict:
        token = self._answers.get("github_pat", "")
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _fetch_existing_integrations(self) -> list:
        base_url = (self._session_base_url or self._answers.get("cortex_base_url", "")).rstrip("/")
        if not base_url:
            return []
        try:
            resp = requests.get(
                f"{base_url}/api/v1/github/configurations",
                headers=self._cortex_headers(),
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("configurations", [])
        except Exception:
            pass
        return []

    def collect_prompts(self) -> None:
        # Cortex credentials — use CLI session values silently when available
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

        # Check for existing GitHub integrations
        existing = self._fetch_existing_integrations()
        if existing:
            aliases = [f"  - {c['alias']} [{c.get('type', '').replace('_', ' ').title()}]{'  (default)' if c.get('isDefault') else ''}" for c in existing]
            print("\nGitHub integrations already configured in Cortex:")
            for line in aliases:
                print(line)
            already_has_cortex_cli = any(c["alias"] == "cortex-cli" for c in existing)
            if already_has_cortex_cli:
                print("\nIntegration 'cortex-cli' already exists — nothing to do.")
                self._answers["skip_integration"] = "true"
                return
            if not self.confirm("\nCreate the required 'cortex-cli' integration now?", default=True):
                self._answers["skip_integration"] = "true"
                return

        self._answers.pop("skip_integration", None)
        gh_url = f"https://github.com/{TARGET_REPO}"
        print(f"\nThis solution uses the public GitHub repo: {_hyperlink(gh_url, gh_url)}")
        print("A GitHub Personal Access Token (PAT) lets Cortex read it for GitOps discovery.")
        print()
        print("Create a PAT at: https://github.com/settings/tokens")
        print("  Classic PAT  — scope: public_repo")
        print("  Fine-grained — Contents: Read-only on cortexapps/cli (or all public repos)")
        print()

        self.prompt("github_pat", "GitHub Personal Access Token", env_var="GITHUB_TOKEN", secret=True)
        self._answers["integration_alias"] = "cortex-cli"
        print("Integration alias: cortex-cli (fixed — entity YAMLs reference this alias)")

    def steps(self) -> list[tuple[str, callable]]:
        if self._answers.get("skip_integration") == "true":
            return [("Skipping — 'cortex-cli' integration already exists", lambda: None)]

        steps = [
            ("Validating PAT against GitHub API", self._validate_pat),
            ("Creating GitHub PAT integration in Cortex", self._create_integration),
            ("Verifying integration in Cortex", self._verify_integration),
        ]
        return steps

    def _validate_pat(self) -> str:
        resp = requests.get(
            f"{GITHUB_API}/repos/{TARGET_REPO}",
            headers=self._gh_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return f"Confirmed access to {TARGET_REPO} ({data.get('visibility', 'public')} repo)"
        if resp.status_code == 401:
            raise RuntimeError("PAT is invalid or expired — check the token and try again")
        if resp.status_code == 403:
            raise RuntimeError("PAT lacks permission to read public repos — ensure public_repo scope is set")
        raise RuntimeError(f"Unexpected GitHub API response: {resp.status_code}")

    def _create_integration(self) -> str:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        alias = self._answers["integration_alias"]

        # Check if alias already exists
        check = requests.get(
            f"{base_url}/api/v1/github/configurations/personal/{alias}",
            headers=self._cortex_headers(),
            timeout=10,
        )
        if check.status_code == 200:
            return f"Integration '{alias}' already exists — skipping creation"

        has_default = any(c.get("isDefault") for c in self._fetch_existing_integrations())
        resp = requests.post(
            f"{base_url}/api/v1/github/configurations/personal",
            json={
                "alias": alias,
                "accessToken": self._answers["github_pat"],
                "isDefault": not has_default,
            },
            headers=self._cortex_headers(),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"{resp.status_code} {resp.text}")
        default_note = "set as default" if not has_default else "not set as default (another integration is already default)"
        return f"Created personal PAT integration '{alias}' ({default_note})"

    def _verify_integration(self) -> list:
        base_url = self._answers["cortex_base_url"].rstrip("/")
        alias = self._answers["integration_alias"]

        resp = requests.post(
            f"{base_url}/api/v1/github/configurations/validate/{alias}",
            headers=self._cortex_headers(),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Cortex validation failed: {resp.status_code} {resp.text}")

        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url
        integrations_url = f"{app_url}/admin/integrations/github"
        return [
            f"Integration validated by Cortex",
            f"View: {_hyperlink(integrations_url, 'GitHub integrations')}",
        ]

    def post_steps(self) -> None:
        base_url = self._answers.get("cortex_base_url", "https://api.getcortexapp.com").rstrip("/")
        app_url = base_url.replace("api.", "app.", 1) if "api." in base_url else base_url

        gitops_url = f"{app_url}/admin/gitops"
        catalog_url = f"{app_url}/admin/resources"

        catalogs_url = f"{app_url}/admin/catalogs"

        repo_url = f"https://github.com/{TARGET_REPO}"

        print()
        print(f"Setup complete. Monorepo: {_hyperlink(repo_url, repo_url)}\n")
        print("Next steps:\n")
        print(f"1. Create a catalog to see all 5 components together:")
        print(f"   {_hyperlink(catalogs_url, 'Catalogs')} → New Catalog → name it 'Monorepo Demo'")
        print(f"   Catalog filter:")
        print(f"     Entity type: service")
        print(f"   Advanced options → Groups → Include: monorepo-demo")
        print(f"   (Catalog creation will be automated once the Cortex catalog API is available.)")
        print()
        print(f"2. (Optional) Enable GitOps so Cortex syncs directly from the repo:")
        print(f"   {_hyperlink(gitops_url, 'GitOps settings')} → Add repository → cortexapps/cli")
        print(f"   Cortex will discover:")
        print(f"     cortexapps_cli/solutions/monorepo/services/cli-core/cortex.yaml      →  monorepo-demo-cli-core")
        print(f"     cortexapps_cli/solutions/monorepo/services/cli-commands/cortex.yaml  →  monorepo-demo-cli-commands")
        print(f"     cortexapps_cli/solutions/monorepo/services/cli-solutions/cortex.yaml →  monorepo-demo-cli-solutions")
        print(f"     cortexapps_cli/solutions/monorepo/services/cli-tests/cortex.yaml     →  monorepo-demo-cli-tests")
        print(f"     cortexapps_cli/solutions/monorepo/services/cli-docker/cortex.yaml    →  monorepo-demo-cli-docker")
        print()
        print(f"3. (Optional) Test GitOps with this repo:")
        print(f"   Before testing, verify in {_hyperlink(gitops_url, 'GitOps settings')} that 'UI importing'")
        print(f"   is turned OFF for the service entity type — otherwise Cortex will allow")
        print(f"   entities to be created outside of GitOps, which undermines the test.")
        print()
        print(f"   Then delete the entities the solution just created:")
        print(f"     cortex catalog delete --tag monorepo-demo-cli-core --force")
        print(f"     cortex catalog delete --tag monorepo-demo-cli-commands --force")
        print(f"     cortex catalog delete --tag monorepo-demo-cli-solutions --force")
        print(f"     cortex catalog delete --tag monorepo-demo-cli-tests --force")
        print(f"     cortex catalog delete --tag monorepo-demo-cli-docker --force")
        print()
        print(f"   Then trigger a manual import:")
        print(f"   Catalogs → All Entities → Import Entities → Import Manually → GitHub → follow prompts")
        print(f"   Cortex will rediscover all 5 cortex.yaml files and recreate the entities.")
        print()
        print(f"4. Ready to model your own monorepo?")
        print(f"   For each component in your repo:")
        print(f"     a. Add a cortex.yaml to the component's subdirectory")
        print(f"     b. Set x-cortex-git.github.repository and basepath to match")
        print(f"     c. Add a consistent group tag (e.g. my-monorepo) to all components")
        print(f"     d. Add x-cortex-git.github.alias if you have more than one GitHub integration configured,")
        print(f"        and your entities aren't represented by the 'default' integration")
        print(f"   Then add your repo in {_hyperlink(gitops_url, 'GitOps settings')} and Cortex will")
        print(f"   discover and import all components automatically.")
        print()
        print(f"   Then create a catalog to see them together:")
        print(f"   {_hyperlink(catalogs_url, 'Catalogs')} → New Catalog")
        print(f"     Entity type: service")
        print(f"     Advanced options → Groups → Include: <your-group-tag>")
        print(f"   (Catalog creation will be automated once the Cortex catalog API is available.)")


def main(**kwargs):
    MonorepoSetup(**kwargs).run()


if __name__ == "__main__":
    main()
