from pathlib import Path


def test_create_runner(config_dir: Path) -> None:
    from tarmac.runner import Runner

    Runner(base_path=str(config_dir))


def test_run_empty_workflow(config_dir: Path) -> None:
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "jobs").mkdir()
    with open(config_dir / "jobs" / "empty.yml", "w") as f:
        f.write("")
    outputs = runner.execute_job("empty", {})
    assert outputs == {"steps": {}, "succeeded": True}


def test_run_empty_script(config_dir: Path) -> None:
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "scripts").mkdir()
    with open(config_dir / "scripts" / "empty.py", "w") as f:
        f.write("")
    outputs = runner.execute_script("empty", {})
    assert outputs == {"succeeded": True}
