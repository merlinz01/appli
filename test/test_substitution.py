from pathlib import Path


def test_substitution(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "substitution.yml", "w") as f:
        f.write(
            """
steps:
  - id: step1
    run: echo "Hi. $TEST_ENV"
    with:
      env:
        TEST_ENV: This is a test. ${" ".join(["Hello", "World"])}
  - id: step2
    do: test
    with:
      full_subst: ${["Hello", "World"]}
      nested_subst:
        - ${"Hello"}
        - world:
            - ${"nested"}
            - ${"substitution"}
            - ${"test"}
"""
        )
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "test.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   full_subst:
#     type: list
#   nested_subst:
#     type: list
# ///
from tarmac.operations import run
def main(op):
    op.outputs["a_list"] = op.inputs["full_subst"]
    op.outputs["nested_list"] = op.inputs["nested_subst"]
run(main)
"""
        )

    outputs = runner.execute_workflow("substitution", {})
    assert outputs["succeeded"] is True
    assert outputs["steps"]["step1"]["output"] == "Hi. This is a test. Hello World\n"
    assert outputs["steps"]["step2"]["a_list"] == ["Hello", "World"]
    assert outputs["steps"]["step2"]["nested_list"] == [
        "Hello",
        {"world": ["nested", "substitution", "test"]},
    ]
