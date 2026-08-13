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

    def __init__(self, state_dir: Optional[Path] = None, no_prompt: bool = False):
        self._no_prompt = no_prompt
        self._secret_keys: set = set()
        self._answers: dict = {}

        solutions_dir = state_dir or Path.home() / ".cortex" / "solutions"
        solutions_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = solutions_dir / f"{self.solution_tag}.json"

        data = self._load_file()
        self._answers = data.get("answers", {})
        self._state: dict = data.get("state", {})

        self._migrate_old_state()

    def _load_file(self) -> dict:
        if self._state_file.exists():
            try:
                return json.loads(self._state_file.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_file(self) -> None:
        data = {
            "answers": {k: v for k, v in self._answers.items() if k not in self._secret_keys},
            "state": self._state,
        }
        self._state_file.write_text(json.dumps(data, indent=2))

    def _save_state(self) -> None:
        self._save_file()

    def _migrate_old_state(self) -> None:
        """Move state from the old flat ~/.cortex/setup-<tag>.json into the new file."""
        old_file = Path.home() / ".cortex" / f"setup-{self.solution_tag}.json"
        if not old_file.exists():
            return
        try:
            old_data = json.loads(old_file.read_text())
            if old_data and not self._state:
                self._state.update(old_data)
                self._save_file()
            old_file.unlink()
        except Exception:
            pass

    def prompt(
        self,
        key: str,
        message: str,
        env_var: Optional[str] = None,
        default: Optional[str] = None,
        secret: bool = False,
    ) -> str:
        """Prompt for a value. Uses saved answer or env var when available."""
        if secret:
            self._secret_keys.add(key)

        # Non-secret: use saved answer when --no-prompt
        if self._no_prompt and not secret and key in self._answers:
            return self._answers[key]

        # Non-secret: saved answer takes precedence over any derived default
        if not secret and key in self._answers:
            default = self._answers[key]

        if env_var:
            env_val = os.environ.get(env_var)
            if env_val:
                masked = "********" if secret else env_val
                if self._no_prompt or self.confirm(f"{message} [{masked} from {env_var}]", default=True):
                    self._answers[key] = env_val
                    return env_val

        # Secrets in --no-prompt mode still need a prompt if no env var provided
        if self._no_prompt and secret and key not in self._answers:
            print(f"  (secret required — no env var set for {key})", file=sys.stderr)

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
        """Y|N confirmation prompt. Auto-accepts default when --no-prompt."""
        if self._no_prompt:
            return default
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
        self._save_file()

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
        if self._no_prompt and self._answers:
            saved = {k: v for k, v in self._answers.items() if k not in self._secret_keys}
            if saved:
                print("Using saved configuration:")
                for k, v in saved.items():
                    print(f"  {k}: {v}")
                print()

        self.collect_prompts()
        self._save_file()

        print()
        step_list = self.steps()
        total = len(step_list)
        for i, (label, fn) in enumerate(step_list, 1):
            try:
                detail = fn()
                print(f"[{i}/{total}] {label}... \u2713")
                if detail:
                    lines = [detail] if isinstance(detail, str) else detail
                    for line in lines:
                        print(f"  {line}")
                print()
            except Exception as e:
                print(f"[{i}/{total}] {label}... \u2717  {e}", file=sys.stderr)
                raise SystemExit(1)
        self.post_steps()
