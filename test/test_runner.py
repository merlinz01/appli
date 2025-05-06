from pathlib import Path

import pytest


def test_create_runner(config_dir: Path):
    from tarmac.runner import Runner

    Runner(base_path=str(config_dir))


def test_run_empty_workflow(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "empty.yml", "w") as f:
        f.write("")
    outputs = runner.execute_workflow("empty", {})
    assert outputs == {"steps": {}, "succeeded": True}


def test_run_empty_script(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "empty.py", "w") as f:
        f.write("")
    outputs = runner.execute_script("empty", {})
    assert outputs == {"succeeded": True}


def test_run_nonexistent_script(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    with pytest.raises(ValueError, match="Script nonexistent not found"):
        runner.execute_script("nonexistent", {})


def test_run_nonexistent_workflow(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    with pytest.raises(ValueError, match="Workflow nonexistent not found"):
        runner.execute_workflow("nonexistent", {})


def test_run_script_returning_invalid_json(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "invalid_json.py", "w") as f:
        f.write(
            """
# /// tarmac
# ///
import os
with open(os.environ["TARMAC_OUTPUTS_FILE"], "w") as f:
    f.write("not a json")
"""
        )
    outputs = runner.execute_script("invalid_json", {})
    assert outputs == {
        "succeeded": False,
        "error": "Failed to decode JSON from outputs file",
    }


def test_run_script_failing(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "failing.py", "w") as f:
        f.write(
            """
# /// tarmac
# ///
print("This is a test script")
raise Exception("This is a test exception")
"""
        )
    outputs = runner.execute_script("failing", {})
    assert outputs["succeeded"] is False
    assert outputs["output"] == "This is a test script\n"
    assert outputs["error"].startswith("Traceback (most recent call last):")
    assert outputs["error"].endswith("Exception: This is a test exception\n")


def test_run_script_output(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "stderr.py", "w") as f:
        f.write(
            """
# /// tarmac
# ///
import sys
sys.stdout.write("This is a test output message")
sys.stderr.write("This is a test error message")
"""
        )
    outputs = runner.execute_script("stderr", {})
    assert outputs["succeeded"] is True
    assert outputs["output"] == "This is a test output message"
    assert outputs["error"] == "This is a test error message"


def test_run_script_raising_failure(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "raise.py", "w") as f:
        f.write(
            """
# /// tarmac
# ///
from tarmac.operations import run, Failure
def main(op):
    raise Failure("This is a test failure")
run(main)
"""
        )
    outputs = runner.execute_script("raise", {})
    assert outputs["succeeded"] is False
    assert outputs["error"] == "This is a test failure"


def test_run_script_raising_error(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "raise.py", "w") as f:
        f.write(
            """
# /// tarmac
# ///
from tarmac.operations import run
def main(op):
    raise ValueError("This is a test error")
run(main)
"""
        )
    outputs = runner.execute_script("raise", {})
    assert outputs["succeeded"] is False
    assert outputs["error"].startswith("Traceback (most recent call last):")
    assert outputs["error"].endswith("ValueError: This is a test error\n")


def test_run_script_missing_input(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "missing_input.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   required_input:
#     type: str
#     required: true
# ///
from tarmac.operations import run
def main(op):
    op.log("This is a test script")
run(main)
"""
        )
    with pytest.raises(
        ValueError,
        match="Missing required input: required_input",
    ):
        runner.execute_script("missing_input", {})


def test_run_script_default_input(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "default_input.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   default_input:
#     type: str
#     required: false
#     default: "default_value"
# ///
from tarmac.operations import run
def main(op):
    op.log(op.inputs["default_input"])
run(main)
"""
        )
    outputs = runner.execute_script("default_input", {})
    assert outputs["succeeded"] is True
    assert outputs["output"] == "default_value\n"


def test_run_script_with_extra_inputs(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "extra_inputs.py", "w") as f:
        f.write(
            """
# /// tarmac
# ///
from tarmac.operations import run
def main(op):
    op.log("This is a test script")
run(main)
"""
        )
    with pytest.raises(
        ValueError,
        match="Unknown input: extra_input",
    ):
        runner.execute_script("extra_inputs", {"extra_input": "value"})
