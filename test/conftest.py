from pathlib import Path

import pytest
from pytest import MonkeyPatch


@pytest.fixture
def config_dir(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    """
    Fixture to create a temporary config directory.
    """
    # Create a temporary directory
    config_path = tmp_path / "config"
    config_path.mkdir()

    return config_path
