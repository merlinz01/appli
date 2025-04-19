from pathlib import Path


def test_create_runner(config_dir: Path) -> None:
    from tarmac.runner import Runner

    Runner(base_path=str(config_dir))
