"""
Post-install setup for the terraform solution.
Verifies Terraform is installed, copies template files to a working directory,
writes credentials, and runs terraform init + apply.

Run via: cortex solutions post-install -s terraform
"""

SETUP_DESCRIPTION = (
    "Sets up the Parts Unlimited demo org in your Cortex instance using the "
    "Cortex Terraform provider. Requires Terraform >= 1.5 — install at "
    "https://developer.hashicorp.com/terraform/install"
)

import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from cortexapps_cli.solutions._lib.setup_base import SolutionSetup
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from _lib.setup_base import SolutionSetup

_TEMPLATES_DIR = Path(__file__).parent / "_templates" / "terraform"
_DELTA_DIR = Path(__file__).parent / "_templates" / "terraform-delta"

_GITIGNORE_ENTRIES = [
    "terraform.tfvars",
    ".terraform/",
    "*.tfstate",
    "*.tfstate.backup",
    ".terraform.lock.hcl",
]


class TerraformSetup(SolutionSetup):
    solution_tag = "terraform"

    def __init__(self, cortex_api_key: str = None, cortex_base_url: str = None, no_prompt: bool = False, **kwargs):
        super().__init__(no_prompt=no_prompt, **kwargs)
        self._session_api_key = cortex_api_key
        self._session_base_url = cortex_base_url

    def collect_prompts(self) -> None:
        self.prompt(
            "work_dir",
            "Working directory for Terraform files",
            default=str(Path.home() / "parts-unlimited-terraform"),
            env_var="TERRAFORM_WORK_DIR",
        )

    def steps(self) -> list[tuple[str, callable]]:
        return [
            ("Check Terraform CLI", self._check_terraform),
            ("Create working directory", self._create_work_dir),
            ("Copy Terraform files", self._copy_files),
            ("Write terraform.tfvars", self._write_tfvars),
            ("Write .gitignore", self._write_gitignore),
            ("terraform init", self._terraform_init),
            ("terraform apply", self._terraform_apply),
        ]

    def post_steps(self) -> None:
        work_dir = self._answers["work_dir"]
        delta_dir = _DELTA_DIR

        print("\n✓ Parts Unlimited demo org created in Cortex via Terraform!\n")
        print(f"  Terraform files are at: {work_dir}\n")
        print("─" * 60)
        print("NEXT: Try the delta to see Terraform's incremental update\n")
        print("  1. Copy the delta files into your working directory:")
        print(f"     cp {delta_dir}/ecommerce.tf {work_dir}/ecommerce.tf")
        print(f"     cp {delta_dir}/teams.tf {work_dir}/teams.tf\n")
        print("  2. Preview the changes:")
        print(f"     cd {work_dir} && terraform plan\n")
        print("     Look for:")
        print("       ~ cortex_catalog_entity.phoenix       (update: links + metadata added)")
        print("       + cortex_catalog_entity.notification_service  (create: new service)")
        print("       ~ cortex_catalog_entity.team_development      (update: new member)\n")
        print("  3. Apply:")
        print(f"     terraform apply\n")
        print("  4. Check the Production Readiness scorecard in Cortex.")
        print("     The Phoenix Project should now show Silver.\n")
        print("─" * 60)
        print("To use Terraform for your real catalog, see the CI/CD integration")
        print("section in: cortex solutions info -s terraform")

    # ── Private step implementations ──────────────────────────────────────────

    def _check_terraform(self) -> None:
        if self.already_done("check_terraform"):
            return
        result = shutil.which("terraform")
        if result is None:
            print(
                "\nERROR: terraform CLI not found in PATH.\n"
                "Install Terraform >= 1.5 from: https://developer.hashicorp.com/terraform/install",
                file=sys.stderr,
            )
            raise RuntimeError("terraform not found")
        # Check version >= 1.5
        try:
            out = subprocess.check_output(
                ["terraform", "version", "-json"], text=True
            )
            version_str = json.loads(out).get("terraform_version", "0.0.0")
            major, minor, *_ = (int(x) for x in version_str.split("."))
            if (major, minor) < (1, 5):
                raise RuntimeError(
                    f"Terraform {version_str} is too old. Version >= 1.5 required.\n"
                    "Upgrade at: https://developer.hashicorp.com/terraform/install"
                )
        except (subprocess.CalledProcessError, KeyError, ValueError):
            # If version check fails, proceed — let terraform itself error if needed
            pass
        self.mark_done("check_terraform")

    def _create_work_dir(self) -> None:
        if self.already_done("create_work_dir"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        work_dir.mkdir(parents=True, exist_ok=True)
        self.mark_done("create_work_dir")

    def _copy_files(self) -> None:
        if self.already_done("copy_files"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        for src in _TEMPLATES_DIR.iterdir():
            if src.is_file():
                shutil.copy2(src, work_dir / src.name)
        self.mark_done("copy_files")

    def _write_tfvars(self) -> None:
        if self.already_done("write_tfvars"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        api_key = self._session_api_key or ""
        base_url = self._session_base_url or "https://api.getcortexapp.com"
        tfvars = work_dir / "terraform.tfvars"
        tfvars.write_text(
            f'cortex_api_token = "{api_key}"\n'
            f'cortex_base_url  = "{base_url}"\n'
        )
        self.mark_done("write_tfvars")

    def _write_gitignore(self) -> None:
        if self.already_done("write_gitignore"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        gitignore = work_dir / ".gitignore"
        existing = gitignore.read_text() if gitignore.exists() else ""
        additions = [e for e in _GITIGNORE_ENTRIES if e not in existing]
        if additions:
            with gitignore.open("a") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write("\n".join(additions) + "\n")
        self.mark_done("write_gitignore")

    def _terraform_init(self) -> None:
        if self.already_done("terraform_init"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        result = subprocess.run(
            ["terraform", "init"],
            cwd=work_dir,
            capture_output=False,  # stream output to terminal
        )
        if result.returncode != 0:
            raise RuntimeError("terraform init failed — see output above")
        self.mark_done("terraform_init")

    def _terraform_apply(self) -> None:
        if self.already_done("terraform_apply"):
            return
        work_dir = Path(self._answers["work_dir"]).expanduser()
        result = subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=work_dir,
            capture_output=False,  # stream output to terminal
        )
        if result.returncode != 0:
            raise RuntimeError(
                "terraform apply failed — see output above.\n"
                f"State may be partially created. Retry from: {work_dir}"
            )
        self.mark_done("terraform_apply")


def main(**kwargs):
    TerraformSetup(**kwargs).run()


if __name__ == "__main__":
    main()
