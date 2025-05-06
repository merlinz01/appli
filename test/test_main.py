import subprocess
import sys
from pathlib import Path


def run_tarmac(*args: str) -> subprocess.CompletedProcess:
    """Run the tarmac command with the given arguments."""
    command = [sys.executable, "-m", "tarmac"] + list(args)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with error: {result.stderr}")
    return result


def test_help():
    """Test the help command."""
    output = run_tarmac("--help").stdout
    assert "usage:" in output
    assert "--version" in output
    assert "--log-level" in output
    assert "--output-format" in output
    assert "--base-path" in output
    assert "--inputs" in output
    assert "--output-file" in output


def test_version():
    """Test the version command."""
    from tarmac import __version__

    output = run_tarmac("--version").stdout
    assert output == f"tarmac {__version__}\n"


def test_json_output(config_dir: Path):
    """Test running a simple workflow."""
    import json

    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "simple.yml", "w") as f:
        f.write(
            """
steps:
  - id: test
    do: test
    with:
      test: "test"
"""
        )
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "test.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   test:
#     type: str
#     description: This is a test input
# outputs:
#   test:
#     type: str
#     description: This is a test output
# ///
from tarmac.operations import run
def main(op):
    op.outputs["test"] = op.inputs["test"]
    op.log("This is a test log message")
run(main)
"""
        )
    p = run_tarmac(
        "simple",
        "--base-path",
        str(config_dir),
        "--output-format",
        "json",
        "--log-level",
        "error",
    )
    assert p.returncode == 0
    assert p.stdout == json.dumps(
        {
            "succeeded": True,
            "steps": {
                "test": {
                    "test": "test",
                    "succeeded": True,
                    "output": "This is a test log message\n",
                }
            },
        },
        indent=2,
    )
    assert p.stderr == ""


def test_yaml_output(config_dir: Path):
    """Test running a simple workflow."""
    import yaml

    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "simple.yml", "w") as f:
        f.write(
            """
steps:
  - id: test
    do: test
    with:
      test: "test"
"""
        )
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "test.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   test:
#     type: str
#     description: This is a test input
# outputs:
#   test:
#     type: str
#     description: This is a test output
# ///
from tarmac.operations import run
def main(op):
    op.outputs["test"] = op.inputs["test"]
    op.log("This is a test log message")
run(main)
"""
        )
    p = run_tarmac(
        "simple",
        "--base-path",
        str(config_dir),
        "--output-format",
        "yaml",
        "--log-level",
        "error",
    )
    assert p.returncode == 0
    assert p.stdout == yaml.dump(
        {
            "succeeded": True,
            "steps": {
                "test": {
                    "test": "test",
                    "succeeded": True,
                    "output": "This is a test log message\n",
                }
            },
        },
        indent=2,
    )
    assert p.stderr == ""


def test_text_output(config_dir: Path):
    """Test running a simple workflow."""
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "simple.yml", "w") as f:
        f.write(
            """
steps:
  - id: test
    do: test
    with:
      test: "test"
"""
        )
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "test.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   test:
#     type: str
#     description: This is a test input
# outputs:
#   test:
#     type: str
#     description: This is a test output
#   list:
#     type: list
#     description: This is a test list output
#   dict:
#     type: dict
#     description: This is a test dict output
# ///
from tarmac.operations import run
def main(op):
    op.outputs["test"] = op.inputs["test"]
    op.outputs['list'] = [
        1, 2, 3,
        'averylongstring'*10,
    ]
    op.outputs['dict'] = {
        'a': 1, 'b': 2,
        'c': 'averylongstring'*10,
    }
    op.log("This is a test log message")
run(main)
"""
        )
    p = run_tarmac(
        "simple",
        "--base-path",
        str(config_dir),
        "--output-format",
        "text",
        "--log-level",
        "error",
    )
    assert p.returncode == 0
    assert p.stdout == (
        "\n"
        "(Note: this output is meant to be human-readable. Use JSON format for parsing.)\n"
        "\n"
        "succeeded: True\n"
        "steps:\n"
        "  test:\n"
        "    test: test\n"
        "    list:\n"
        "      - 1\n"
        "      - 2\n"
        "      - 3\n"
        "      -⤵\n"
        "        averylongstringaverylongstringaverylongstringaverylongstringaverylongstringaverylongstringaverylongs ⤵\n"
        "        tringaverylongstringaverylongstringaverylongstring\n"
        "    dict:\n"
        "      a: 1\n"
        "      b: 2\n"
        "      c:\n"
        "        averylongstringaverylongstringaverylongstringaverylongstringaverylongstringaverylongstringaverylongs ⤵\n"
        "        tringaverylongstringaverylongstringaverylongstring\n"
        "    succeeded: True\n"
        "    output:\n"
        "      This is a test log message\n"
    )
    assert p.stderr == ""


def test_colored_text_output(config_dir: Path):
    """Test running a simple workflow."""
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "simple.yml", "w") as f:
        f.write(
            """
steps:
  - id: test
    do: test
    with:
      test: "test"
"""
        )
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "test.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   test:
#     type: str
#     description: This is a test input
# outputs:
#   test:
#     type: str
#     description: This is a test output
#   list:
#     type: list
#     description: This is a test list output
#   dict:
#     type: dict
#     description: This is a test dict output
# ///
from tarmac.operations import run
def main(op):
    op.outputs["test"] = op.inputs["test"]
    op.outputs['list'] = [1, 2, 3]
    op.outputs['dict'] = {'a': 1, 'b': 2}
    op.log("This is a test log message")
run(main)
"""
        )
    p = run_tarmac(
        "simple",
        "--base-path",
        str(config_dir),
        "--output-format",
        "colored-text",
        "--log-level",
        "error",
    )
    assert p.returncode == 0
    assert p.stdout == (
        "\x1b[36m\n(Note: this output is meant to be human-readable. Use JSON format for parsing.)\n\n\x1b[0m"
        "\x1b[34msucceeded\x1b[0m: \x1b[36mTrue\x1b[0m\n"
        "\x1b[34msteps\x1b[0m:\n\x1b[0m  \x1b[34mtest\x1b[0m:\n\x1b[0m    \x1b[34mtest\x1b[0m: \x1b[32mtest\x1b[0m\n    \x1b[34mlist\x1b[0m:\n\x1b[0m      \x1b[34m- \x1b[33m1\x1b[0m\n      \x1b[34m- \x1b[33m2\x1b[0m\n      \x1b[34m- \x1b[33m3\x1b[0m\n\x1b[0m    \x1b[34mdict\x1b[0m:\n\x1b[0m      \x1b[34ma\x1b[0m: \x1b[33m1\x1b[0m\n      \x1b[34mb\x1b[0m: \x1b[33m2\x1b[0m\n\x1b[0m    \x1b[34msucceeded\x1b[0m: \x1b[36mTrue\x1b[0m\n    \x1b[34moutput\x1b[0m:\n\x1b[32m      \x1b[32mThis is a test log message\x1b[0m\n\x1b[0m\x1b[0m\x1b[0m"
    )
    assert p.stderr == ""


def test_output_to_file(config_dir: Path):
    """Test running a simple workflow and writing output to a file."""
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "simple.yml", "w") as f:
        f.write(
            """
steps:
  - id: test
    do: test
    with:
      test: "test"
"""
        )
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "test.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   test:
#     type: str
#     description: This is a test input
# outputs:
#   test:
#     type: str
#     description: This is a test output
# ///
from tarmac.operations import run

def main(op):
    op.outputs["test"] = op.inputs["test"]
    op.log("This is a test log message")
run(main)
"""
        )

    output_file = config_dir / "output.json"
    p = run_tarmac(
        "simple",
        "--base-path",
        str(config_dir),
        "--output-format",
        "json",
        "--log-level",
        "error",
        "--output-file",
        str(output_file),
    )
    assert p.returncode == 0
    assert output_file.exists()
    with open(output_file, "r") as f:
        output = f.read()
        assert output == (
            "{\n"
            '  "succeeded": true,\n'
            '  "steps": {\n'
            '    "test": {\n'
            '      "test": "test",\n'
            '      "succeeded": true,\n'
            '      "output": "This is a test log message\\n"\n'
            "    }\n"
            "  }\n"
            "}"
        )
    assert p.stderr == ""
    assert p.stdout == ""


def test_execute_script_with_inputs(config_dir: Path):
    """Test running a script with inputs."""
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "test.py", "w") as f:
        f.write(
            """
# /// tarmac
# inputs:
#   test:
#     type: str
#     description: This is a test input
# outputs:
#   test:
#     type: str
#     description: This is a test output
# ///
from tarmac.operations import run

def main(op):
    op.outputs["test"] = op.inputs["test"]
    op.log("This is a test log message")

run(main)
"""
        )
    p = run_tarmac(
        "--script",
        "test",
        "--base-path",
        str(config_dir),
        "--input",
        "test=test_input",
        "--output-format",
        "json",
        "--log-level",
        "error",
    )
    assert p.returncode == 0
    assert p.stdout == (
        "{\n"
        '  "test": "test_input",\n'
        '  "succeeded": true,\n'
        '  "output": "This is a test log message\\n"\n'
        "}"
    )
