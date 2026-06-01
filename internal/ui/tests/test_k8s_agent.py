import time

import pytest
from playwright.sync_api import Page, expect

from ui import config

ENTITY_TAG = "k8s-test-annotation"
POLL_INTERVAL = 10  # seconds
POLL_TIMEOUT = 300  # 5 minutes

# Expected workload names from k8s/manifests/
EXPECTED_WORKLOADS = [
    "k8s-deployment",
    "k8s-statefulset",
    "k8s-cronjob",
    "k8s-rollout",
]


class TestK8sAgent:
    """Verify that the k8s-agent pushes workloads to Cortex and they appear in the UI.

    Prerequisites:
        - just k8s-agent-setup (deploys agent + test manifests to minikube)
        - Wait ~5 minutes for the agent to sync data to Cortex
    """

    def test_k8s_workloads_visible(self, authenticated_page: Page):
        """Navigate to the entity's K8s tab and verify all test workloads appear."""
        page = authenticated_page

        # Navigate to the K8s tab for our test entity
        page.goto(
            f"{config.BASE_URL}/admin/catalog/{ENTITY_TAG}/k8s"
        )
        page.wait_for_load_state("networkidle")

        # Poll for workloads to appear (agent syncs every 5 minutes)
        deadline = time.time() + POLL_TIMEOUT
        missing = list(EXPECTED_WORKLOADS)

        while missing and time.time() < deadline:
            content = page.content()
            missing = [name for name in EXPECTED_WORKLOADS if name not in content]
            if missing:
                time.sleep(POLL_INTERVAL)
                page.reload()
                page.wait_for_load_state("networkidle")

        assert not missing, (
            f"K8s workloads not found on entity page after {POLL_TIMEOUT}s: {missing}"
        )
        print(f"All {len(EXPECTED_WORKLOADS)} workloads visible on K8s tab:")
        for name in EXPECTED_WORKLOADS:
            print(f"  - {name}")

    def test_rollout_has_containers(self, authenticated_page: Page):
        """Verify the Argo Rollout with workloadRef shows containers.

        This is the regression test for CET-429: workloadRef-style Rollouts
        should resolve containers from the referenced Deployment.
        """
        page = authenticated_page

        page.goto(
            f"{config.BASE_URL}/admin/catalog/{ENTITY_TAG}/k8s"
        )
        page.wait_for_load_state("networkidle")

        # Find the rollout row and click into it to see details
        rollout_link = page.get_by_role("link", name="k8s-rollout")
        rollout_link.wait_for(state="visible", timeout=30000)
        rollout_link.click()
        page.wait_for_load_state("networkidle")

        # The container from the referenced Deployment (nginx:alpine) should appear
        # This will fail until the backend resolves workloadRef -> Deployment -> containers
        expect(page.get_by_text("nginx")).to_be_visible(timeout=10000)
