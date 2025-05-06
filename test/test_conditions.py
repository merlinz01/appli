import sys
from pathlib import Path

import pytest


def test_conditions(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "conditions.yml", "w") as f:
        f.write(
            f"""
steps:
  - id: step1
    py: print("true")
    if: True
  - id: step2
    py: print("false")
    if: False
  - id: step3
    py: print("true and false")
    if: True and False
  - id: step4
    py: print("exists(nonexistent.txt)")
    if: exists({str((config_dir / "nonexistent.txt").absolute())!r})
  - id: step5
    py: print("exists(existing.txt)")
    if: exists({str((config_dir / "existing.txt").absolute())!r})
  - id: step6
    py: print("isfile(existing.txt)")
    if: isfile({str((config_dir / "existing.txt").absolute())!r})
  - id: step7
    py: print("isdir(existing.txt)")
    if: isdir({str((config_dir / "existing.txt").absolute())!r})
  - id: step8
    py: print("isdir(workflows)")
    if: isdir({str((config_dir / "workflows").absolute())!r})
  - id: step9
    py: print("isfile(workflows)")
    if: isfile({str((config_dir / "workflows").absolute())!r})
  - id: step10
    py: print("platform")
    if: platform == "linux"
  - id: step11
    py: print("platform")
    if: platform == "win32"
  - id: step12
    py: print("platform")
    if: platform == "darwin"
  - id: step13
    py: outputs['changed'] = True
  - id: step14
    py: print("changed(step13)")
    if: changed("step13")
  - id: step15
    py: print("changed(step14)")
    if: changed("step14")
  - id: step16
    py: print("changed(nonexistent)")
    if: changed("nonexistent")
  - id: step17
    py: print("cmd('echo hello')")
    if: run('echo hello').succeeded
  - id: step18
    py: print("cmd('laskjfasdfsdf')")
    if: run('laskjfasdfsdf').succeeded
  - id: step19
    py: print("skipped(step1)")
    if: skipped("step1")
  - id: step20
    py: print("skipped(step2)")
    if: skipped("step2")
"""
        )
    with open(config_dir / "existing.txt", "w") as f:
        f.write("This is a test file.")

    outputs = runner.execute_workflow("conditions", {})

    assert outputs["steps"]["step1"]["succeeded"] is True
    assert outputs["steps"]["step2"]["succeeded"] is None
    assert outputs["steps"]["step3"]["succeeded"] is None
    assert outputs["steps"]["step4"]["succeeded"] is None
    assert outputs["steps"]["step5"]["succeeded"] is True
    assert outputs["steps"]["step6"]["succeeded"] is True
    assert outputs["steps"]["step7"]["succeeded"] is None
    assert outputs["steps"]["step8"]["succeeded"] is True
    assert outputs["steps"]["step9"]["succeeded"] is None
    assert outputs["steps"]["step10"]["succeeded"] is (
        (sys.platform == "linux") or None
    )
    assert outputs["steps"]["step11"]["succeeded"] is (
        (sys.platform == "win32") or None
    )
    assert outputs["steps"]["step12"]["succeeded"] is (
        (sys.platform == "darwin") or None
    )
    assert outputs["steps"]["step13"]["succeeded"] is True
    assert outputs["steps"]["step13"]["changed"] is True
    assert outputs["steps"]["step14"]["succeeded"] is True
    assert outputs["steps"]["step15"]["succeeded"] is None
    assert outputs["steps"]["step16"]["succeeded"] is None
    assert outputs["steps"]["step17"]["succeeded"] is True
    assert outputs["steps"]["step18"]["succeeded"] is None
    assert outputs["steps"]["step19"]["succeeded"] is None
    assert outputs["steps"]["step20"]["succeeded"] is True
    assert outputs["succeeded"] is True


def test_invalid_condition_type(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "invalid_condition.yml", "w") as f:
        f.write(
            """
steps:
  - id: step1
    py: print("true")
    if: 12345
"""
        )
    with pytest.raises(ValueError, match="Invalid condition type"):
        runner.execute_workflow("invalid_condition", {})
    with open(config_dir / "workflows" / "invalid_condition.yml", "w") as f:
        f.write(
            """
steps:
  - id: step1
    py: print("true")
    if: ["one", "two", "three"]
"""
        )
    with pytest.raises(ValueError, match="Invalid condition type"):
        runner.execute_workflow("invalid_condition", {})
