import pytest
from pathlib import Path


def test_help(config_dir: Path) -> None:
    from tarmac.main import main

    with pytest.raises(SystemExit):
        main(["--help"])
