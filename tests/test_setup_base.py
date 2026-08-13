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
