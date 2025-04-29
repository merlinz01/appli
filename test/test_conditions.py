import sys
from pathlib import Path


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
    assert outputs["succeeded"] is True
