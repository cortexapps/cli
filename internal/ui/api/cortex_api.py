import requests

from ui import config


class CortexAPI:
    """Lightweight Cortex API client for test setup/teardown."""

    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {config.API_KEY}",
            "Content-Type": "application/json",
        }

    def delete_workflow(self, tag: str) -> bool:
        """Delete a workflow by tag. Returns True if deleted, False if not found."""
        resp = requests.delete(
            f"{self.base_url}/api/v1/workflows/{tag}",
            headers=self.headers,
        )
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    def get_workflow(self, tag: str) -> dict | None:
        """Get a workflow by tag. Returns None if not found."""
        resp = requests.get(
            f"{self.base_url}/api/v1/workflows/{tag}",
            headers=self.headers,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def list_workflows(self) -> list[dict]:
        """List all workflows."""
        workflows = []
        page = 0
        while True:
            resp = requests.get(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                params={"page": page, "pageSize": 100},
            )
            resp.raise_for_status()
            data = resp.json()
            workflows.extend(data.get("workflows", []))
            if len(workflows) >= data.get("total", 0):
                break
            page += 1
        return workflows

    def delete_workflow_by_name(self, name: str) -> bool:
        """Find and delete a workflow by name. Returns True if deleted."""
        for wf in self.list_workflows():
            if wf.get("name") == name:
                return self.delete_workflow(wf["tag"])
        return False

    # --- Catalog (entities, teams, etc.) ---

    def list_catalog(self, **params) -> list[dict]:
        """List all catalog entities (paginated)."""
        entities = []
        page = 0
        while True:
            resp = requests.get(
                f"{self.base_url}/api/v1/catalog",
                headers=self.headers,
                params={"page": page, "pageSize": 250, **params},
            )
            resp.raise_for_status()
            data = resp.json()
            entities.extend(data.get("entities", []))
            if len(entities) >= data.get("total", 0):
                break
            page += 1
        return entities

    def delete_entity(self, tag: str) -> bool:
        """Delete a catalog entity by tag. Returns True if deleted, False if not found."""
        resp = requests.delete(
            f"{self.base_url}/api/v1/catalog/{tag}",
            headers=self.headers,
        )
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    def delete_entities_by_prefix(self, prefix: str) -> list[str]:
        """Delete all catalog entities whose tag starts with prefix. Returns deleted tags."""
        deleted = []
        for entity in self.list_catalog():
            tag = entity.get("tag", "")
            if tag.startswith(prefix):
                if self.delete_entity(tag):
                    deleted.append(tag)
        return deleted
