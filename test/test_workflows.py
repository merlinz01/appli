from pathlib import Path


def test_workflow_step_run_type(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "workflow.yml", "w") as f:
        f.write(
            """
            steps:
              - name: step1
                run: echo "Hello, World!"
            """
        )
    outputs = runner.execute_workflow("workflow", {})
    assert outputs == {
        "steps": {
            "step1": {
                "succeeded": True,
                "error": "",
                "output": "Hello, World!\n",
                "returncode": 0,
            }
        },
        "succeeded": True,
    }


def test_workflow_step_script_type(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "workflow.yml", "w") as f:
        f.write(
            """
            steps:
              - name: step1
                do: script
            """
        )
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "script.py", "w") as f:
        f.write(
            """
from tarmac.operations import OperationInterface, run


def MyOperation(op: OperationInterface):
    op.log("Hello, World!")

run(MyOperation)
"""
        )
    outputs = runner.execute_workflow("workflow", {})
    assert outputs == {
        "steps": {
            "step1": {
                "succeeded": True,
                "output": "Hello, World!\n",
            }
        },
        "succeeded": True,
    }


def test_workflow_step_workflow_type(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "workflow.yml", "w") as f:
        f.write(
            """
            steps:
              - name: step1
                workflow: workflow2
            """
        )
    with open(config_dir / "workflows" / "workflow2.yml", "w") as f:
        f.write(
            """
            steps:
              - name: step2
                run: echo "Hello, World!"
            """
        )
    outputs = runner.execute_workflow("workflow", {})
    assert outputs == {
        "steps": {
            "step1": {
                "succeeded": True,
                "steps": {
                    "step2": {
                        "succeeded": True,
                        "error": "",
                        "output": "Hello, World!\n",
                        "returncode": 0,
                    }
                },
            }
        },
        "succeeded": True,
    }
