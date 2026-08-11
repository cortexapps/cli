import getpass
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
                if self.confirm(f"{message} [{masked} from {env_var}]", default=True):
                    self._answers[key] = env_val
                    return env_val
                # User declined — fall through to manual prompt

        prompt_str = message
        if default:
            prompt_str += f" [{default}]"
        prompt_str += ": "

        if secret:
            value = getpass.getpass(prompt_str).strip()
        else:
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
