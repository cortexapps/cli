"""
Post-install setup script for the kubernetes-agent solution.
Deploys the Cortex k8s-agent to a kind cluster and creates a demo entity.
Run via: cortex solutions post-install -s kubernetes-agent
"""

SETUP_DESCRIPTION = (
    "This solution deploys the Cortex Kubernetes agent to a local kind cluster "
    "and creates a demo entity to demonstrate the k8s integration."
)

import subprocess
import sys
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

GHCR_IMAGE = "ghcr.io/cortexapps/k8s-agent/k8s-agent"
ARGO_CRD_URL = "https://raw.githubusercontent.com/argoproj/argo-rollouts/stable/manifests/crds/rollout-crd.yaml"


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

    def collect_prompts(self) -> None:
        self._ghcr_token = self.prompt(
            "GHCR_TOKEN",
            "GitHub PAT with read:packages scope for pulling the k8s-agent image",
            env_var="GHCR_TOKEN",
            secret=True,
        )
        self._cluster_name = self.prompt(
            "cluster_name",
            "Name for this cluster as it will appear in Cortex",
            default="demo",
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

    def _create_secrets(self) -> None:
        if self.already_done("create_secrets"):
            return
        print("  Creating cortex-docker-registry-secret...")
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
        print(f"  Installing k8s-agent via helm (chart: {HELM_CHART_DIR})...")
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
            ["kubectl", "rollout", "restart", "deployment",
             "-l", "app.kubernetes.io/name=cortex-k8s-agent"],
            check=True,
        )
        self.mark_done("helm_install")

    def _wait_for_readiness(self) -> None:
        if self.already_done("wait_for_readiness"):
            return
        print("  Waiting for k8s-agent pod to be ready (timeout: 120s)...")
        subprocess.run(
            [
                "kubectl", "rollout", "status", "deployment",
                "-l", "app.kubernetes.io/name=cortex-k8s-agent",
                "--timeout=120s",
            ],
            check=True,
        )
        self.mark_done("wait_for_readiness")

    def _install_argo_crd(self) -> None:
        if self.already_done("install_argo_crd"):
            return
        print(f"  Installing Argo Rollouts CRD...")
        subprocess.run(
            ["kubectl", "apply", "-f", ARGO_CRD_URL],
            check=True,
        )
        self.mark_done("install_argo_crd")

    def _apply_manifests(self) -> None:
        if self.already_done("apply_manifests"):
            return
        print(f"  Applying demo k8s manifests from {MANIFESTS_DIR}...")
        subprocess.run(
            ["kubectl", "apply", "-f", str(MANIFESTS_DIR)],
            check=True,
        )
        self.mark_done("apply_manifests")

    def _create_entity(self) -> None:
        if self.already_done("create_entity"):
            return
        print(f"  Creating demo-kubernetes Cortex entity...")
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
        return [
            ("Create k8s secrets", self._create_secrets),
            ("Install k8s-agent via helm", self._helm_install),
            ("Wait for agent readiness", self._wait_for_readiness),
            ("Install Argo Rollouts CRD", self._install_argo_crd),
            ("Apply demo k8s manifests", self._apply_manifests),
            ("Create demo Cortex entity", self._create_entity),
        ]

    def post_steps(self) -> None:
        print("\n✓ Kubernetes agent deployed and demo workloads running.\n")
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
