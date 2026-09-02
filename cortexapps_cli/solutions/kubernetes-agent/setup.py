"""
Post-install setup script for the kubernetes-agent solution.
Deploys the Cortex k8s-agent either by creating a GitHub Codespace with a kind
cluster, or against an existing Kubernetes cluster.
Run via: cortex solutions post-install -s kubernetes-agent
"""

SETUP_DESCRIPTION = (
    "This solution deploys the Cortex Kubernetes agent to a Kubernetes cluster "
    "and creates a demo entity to demonstrate the k8s integration. "
    "It can spin up a GitHub Codespace with a kind cluster "
    "(https://kind.sigs.k8s.io) automatically, or deploy to any existing cluster."
)

import shlex
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

SOLUTION_DIR = Path(__file__).parent
CATALOG_FILE = SOLUTION_DIR / "catalog" / "demo-kubernetes.yaml"
MANIFESTS_DIR = SOLUTION_DIR / "manifests"
HELM_CHART_DIR = SOLUTION_DIR / "helm-chart"

ARGO_CRD_URL = "https://raw.githubusercontent.com/argoproj/argo-rollouts/stable/manifests/crds/rollout-crd.yaml"

CODESPACE_BRANCH = "worktree-kubernetes-agent-solution"
CODESPACE_READY_TIMEOUT = 600  # 10 minutes for Codespace + kind cluster startup
CODESPACE_POLL_INTERVAL = 20   # seconds between readiness checks


class KubernetesAgentSetup(SolutionSetup):
    solution_tag = "kubernetes-agent"

    def __init__(
        self,
        cortex_api_key: str = None,
        cortex_base_url: str = None,
        no_prompt: bool = False,
        **kwargs,
    ):
        super().__init__(no_prompt=no_prompt, **kwargs)
        self._api_key = cortex_api_key or ""
        self._base_url = (cortex_base_url or "https://api.getcortexapp.com").rstrip("/")
        self._ghcr_token = ""
        self._cluster_name = ""
        self._github_repo = ""
        # Recover codespace name from previous run; its presence means codespace mode
        self._codespace_name = self._state.get("codespace_name", "")
        self._use_codespace = bool(self._codespace_name)

    def collect_prompts(self) -> None:
        # If a Codespace was already created in a prior run, stay in codespace mode.
        # Otherwise ask the user which path they want.
        if not self._codespace_name:
            use_cs_raw = self.prompt(
                "use_codespace",
                "Create a new GitHub Codespace with a kind cluster?"
                " (yes = spin up Codespace, no = use an existing configured cluster)",
                default="yes",
            )
            self._use_codespace = use_cs_raw.lower() in ("yes", "y", "true", "1")

        if self._use_codespace:
            self._github_repo = self.prompt(
                "github_repo",
                "GitHub repository to create the Codespace from (org/repo)",
                default="cortexapps/cli",
            )

        self._ghcr_token = self.prompt(
            "GHCR_TOKEN",
            "GitHub PAT provided by Cortex Customer Engineering for pulling the k8s-agent image"
            " (see https://docs.cortex.io/ingesting-data-into-cortex/integrations/kubernetes#prerequisites)",
            env_var="GHCR_TOKEN",
            secret=True,
        )
        self._cluster_name = self.prompt(
            "cluster_name",
            "Name for this cluster as it will appear in Cortex",
            default="cortex-demo",
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _remote_solution_dir(self) -> str:
        """Path to the solution directory inside the Codespace."""
        repo_name = self._github_repo.split("/")[-1]
        return f"/workspaces/{repo_name}/cortexapps_cli/solutions/kubernetes-agent"

    def _run_remote(self, bash_cmd: str) -> None:
        """Run a bash command inside the Codespace via gh codespace ssh."""
        subprocess.run(
            [
                "gh", "codespace", "ssh",
                "-c", self._codespace_name,
                "--", "bash", "-c", bash_cmd,
            ],
            check=True,
        )

    def _fetch_image_tag(self) -> str:
        """Fetch the latest k8s-agent image tag from the GitHub API."""
        r = requests.get(
            "https://api.github.com/orgs/cortexapps/packages/container/k8s-agent%2Fk8s-agent/versions",
            headers={
                "Authorization": f"Bearer {self._ghcr_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        r.raise_for_status()
        versions = r.json()
        if not versions:
            raise RuntimeError("No k8s-agent versions found in GHCR — is GHCR_TOKEN valid?")
        tags = versions[0].get("metadata", {}).get("container", {}).get("tags", [])
        tag = tags[0] if tags else ""
        if not tag:
            raise RuntimeError("Could not determine k8s-agent image tag from GHCR API response")
        print(f"  Using image tag: {tag}")
        return tag

    # -------------------------------------------------------------------------
    # Step: Create GitHub Codespace (codespace mode only)
    # -------------------------------------------------------------------------

    def _check_gh_cli(self) -> None:
        """Verify gh CLI is installed and authenticated."""
        if subprocess.run(["gh", "--version"], capture_output=True).returncode != 0:
            raise RuntimeError(
                "The 'gh' CLI is required but not found.\n"
                "Install it from https://cli.github.com and run 'gh auth login' first."
            )
        if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
            raise RuntimeError(
                "The 'gh' CLI is not authenticated.\n"
                "Run 'gh auth login' and try again."
            )

    def _create_codespace(self) -> None:
        """Create a GitHub Codespace and wait for the kind cluster to be ready."""
        # Always check gh CLI — also needed for SSH steps that follow
        self._check_gh_cli()

        if self._codespace_name:
            print(f"  Using existing Codespace: {self._codespace_name}")
            return

        print(f"  Creating GitHub Codespace from {self._github_repo}...")
        result = subprocess.run(
            [
                "gh", "codespace", "create",
                "--repo", self._github_repo,
                "--branch", CODESPACE_BRANCH,
                "--devcontainer-path", ".devcontainer/kubernetes-agent/devcontainer.json",
                "--machine", "basicLinux32gb",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self._codespace_name = result.stdout.strip()
        if not self._codespace_name:
            raise RuntimeError("gh codespace create did not return a codespace name")
        print(f"  Codespace created: {self._codespace_name}")

        # Persist the name so re-runs find the existing Codespace
        self._state["codespace_name"] = self._codespace_name
        self._save_file()

        print(
            f"  Waiting for Codespace and kind cluster to initialize "
            f"(up to {CODESPACE_READY_TIMEOUT // 60} min)..."
        )
        deadline = time.time() + CODESPACE_READY_TIMEOUT
        while time.time() < deadline:
            probe = subprocess.run(
                [
                    "gh", "codespace", "ssh",
                    "-c", self._codespace_name,
                    "--", "kubectl", "cluster-info",
                ],
                capture_output=True,
            )
            if probe.returncode == 0:
                return
            time.sleep(CODESPACE_POLL_INTERVAL)

        raise RuntimeError(
            f"Timed out waiting for the kind cluster in Codespace '{self._codespace_name}'.\n"
            "The Codespace may still be initializing. Re-run this command to retry."
        )

    # -------------------------------------------------------------------------
    # Step: Check existing cluster (existing-cluster mode only)
    # -------------------------------------------------------------------------

    def _check_cluster(self) -> None:
        """Verify kubectl can reach a running cluster."""
        result = subprocess.run(["kubectl", "cluster-info"], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(
                "kubectl cannot reach a cluster.\n"
                "Ensure your kubectl context points to a running Kubernetes cluster and try again."
            )

    # -------------------------------------------------------------------------
    # Steps: shared between both modes
    # -------------------------------------------------------------------------

    def _create_secrets(self) -> None:
        if self.already_done("create_secrets"):
            return
        print("  Creating cortex-docker-registry-secret...")
        if self._use_codespace:
            self._run_remote(
                f"kubectl create secret docker-registry cortex-docker-registry-secret "
                f"--docker-server=ghcr.io --docker-username=cortex "
                f"--docker-password={shlex.quote(self._ghcr_token)} "
                f"--dry-run=client -o yaml | kubectl apply -f -"
            )
        else:
            result = subprocess.run(
                [
                    "kubectl", "create", "secret", "docker-registry",
                    "cortex-docker-registry-secret",
                    "--docker-server=ghcr.io",
                    "--docker-username=cortex",
                    f"--docker-password={self._ghcr_token}",
                    "--dry-run=client", "-o", "yaml",
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout, check=True)

        print("  Creating cortex-key secret...")
        if self._use_codespace:
            self._run_remote(
                f"kubectl create secret generic cortex-key "
                f"--from-literal=api-key={shlex.quote(self._api_key)} "
                f"--dry-run=client -o yaml | kubectl apply -f -"
            )
        else:
            result = subprocess.run(
                [
                    "kubectl", "create", "secret", "generic", "cortex-key",
                    f"--from-literal=api-key={self._api_key}",
                    "--dry-run=client", "-o", "yaml",
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout, check=True)

        self.mark_done("create_secrets")

    def _helm_install(self) -> None:
        if self.already_done("helm_install"):
            return
        image_tag = self._fetch_image_tag()
        print("  Installing k8s-agent via helm...")
        if self._use_codespace:
            helm_chart = f"{self._remote_solution_dir()}/helm-chart"
            self._run_remote(
                f"helm upgrade --install cortex-k8s-agent {helm_chart} "
                f"--set image.tag={shlex.quote(image_tag)} "
                f"--set app.baseUrl={shlex.quote(self._base_url)} "
                f"--set app.clusterName={shlex.quote(self._cluster_name)}"
            )
            self._run_remote("kubectl rollout restart deployment/cortex-k8s-agent")
        else:
            subprocess.run(
                [
                    "helm", "upgrade", "--install", "cortex-k8s-agent",
                    str(HELM_CHART_DIR),
                    "--set", f"image.tag={image_tag}",
                    "--set", f"app.baseUrl={self._base_url}",
                    "--set", f"app.clusterName={self._cluster_name}",
                ],
                check=True,
            )
            # Restart to ensure secrets/configmaps are picked up
            subprocess.run(
                ["kubectl", "rollout", "restart", "deployment/cortex-k8s-agent"],
                check=True,
            )
        self.mark_done("helm_install")

    def _wait_for_readiness(self) -> None:
        if self.already_done("wait_for_readiness"):
            return
        print("  Waiting for k8s-agent pod to be ready (timeout: 120s)...")
        if self._use_codespace:
            self._run_remote(
                "kubectl rollout status deployment/cortex-k8s-agent --timeout=120s"
            )
        else:
            subprocess.run(
                [
                    "kubectl", "rollout", "status", "deployment/cortex-k8s-agent",
                    "--timeout=120s",
                ],
                check=True,
            )
        self.mark_done("wait_for_readiness")

    def _install_argo_crd(self) -> None:
        if self.already_done("install_argo_crd"):
            return
        print("  Installing Argo Rollouts CRD...")
        if self._use_codespace:
            self._run_remote(f"kubectl apply -f {ARGO_CRD_URL}")
        else:
            subprocess.run(["kubectl", "apply", "-f", ARGO_CRD_URL], check=True)
        self.mark_done("install_argo_crd")

    def _apply_manifests(self) -> None:
        if self.already_done("apply_manifests"):
            return
        print("  Applying demo k8s manifests...")
        if self._use_codespace:
            manifests = f"{self._remote_solution_dir()}/manifests"
            self._run_remote(f"kubectl apply -f {manifests}")
        else:
            subprocess.run(["kubectl", "apply", "-f", str(MANIFESTS_DIR)], check=True)
        self.mark_done("apply_manifests")

    def _create_entity(self) -> None:
        if self.already_done("create_entity"):
            return
        print("  Creating demo-kubernetes Cortex entity...")
        yaml_content = CATALOG_FILE.read_bytes()
        r = requests.post(
            f"{self._base_url}/api/v1/open-api",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/openapi;charset=UTF-8",
            },
            data=yaml_content,
        )
        if not r.ok:
            raise RuntimeError(
                f"Failed to create Cortex entity: {r.status_code} {r.text}"
            )
        self.mark_done("create_entity")

    def steps(self) -> list:
        first_step = (
            ("Create GitHub Codespace", self._create_codespace)
            if self._use_codespace
            else ("Check cluster connectivity", self._check_cluster)
        )
        return [
            first_step,
            ("Create k8s secrets", self._create_secrets),
            ("Install k8s-agent via helm", self._helm_install),
            ("Wait for agent readiness", self._wait_for_readiness),
            ("Install Argo Rollouts CRD", self._install_argo_crd),
            ("Apply demo k8s manifests", self._apply_manifests),
            ("Create demo Cortex entity", self._create_entity),
        ]

    def post_steps(self) -> None:
        print("\n✓ Kubernetes agent deployed and demo workloads running.\n")
        if self._codespace_name:
            print(f"Codespace: {self._codespace_name}")
            print(f"  Open terminal: gh codespace ssh -c {self._codespace_name}")
            print(f"  Stop Codespace: gh codespace stop -c {self._codespace_name}")
            print()
        print("The agent syncs every 5 minutes. After the first sync, visit:")
        print(f"  {self._base_url.replace('api.', 'app.')}/catalog/demo-kubernetes/k8s")
        print("\nYou should see: demo-deployment, demo-statefulset, demo-cronjob, demo-rollout")
        print("\nNote: GHCR_TOKEN requirement goes away once the k8s-agent image is made public.")


def main(cortex_api_key=None, cortex_base_url=None, no_prompt=False, **kwargs):
    KubernetesAgentSetup(
        cortex_api_key=cortex_api_key,
        cortex_base_url=cortex_base_url,
        no_prompt=no_prompt,
    ).run()


if __name__ == "__main__":
    main()
