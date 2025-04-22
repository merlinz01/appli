import pytest
from pathlib import Path


def test_help(config_dir: Path):
    from tarmac.main import main

    with pytest.raises(SystemExit):
        main(["--help"])
