import sys
import subprocess


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
