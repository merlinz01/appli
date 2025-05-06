from pathlib import Path

import pytest


def test_validate_int(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "validate_int.yml", "w") as f:
        f.write(
            """
inputs:
    int:
        type: int
steps: []
"""
        )
    with pytest.raises(ValueError, match="Input int must be an integer"):
        runner.execute_workflow("validate_int", {"int": "not an int"})
    with pytest.raises(ValueError, match="Input int must be an integer"):
        runner.execute_workflow("validate_int", {"int": 3.14})
    runner.execute_workflow("validate_int", {"int": 42})


def test_validate_float(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "validate_float.yml", "w") as f:
        f.write(
            """
inputs:
    float:
        type: float
steps: []
"""
        )
    with pytest.raises(ValueError, match="Input float must be a float"):
        runner.execute_workflow("validate_float", {"float": "not a float"})
    with pytest.raises(ValueError, match="Input float must be a float"):
        runner.execute_workflow("validate_float", {"float": []})
    runner.execute_workflow("validate_float", {"float": 3})
    runner.execute_workflow("validate_float", {"float": 3.14})


def test_validate_bool(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "validate_bool.yml", "w") as f:
        f.write(
            """
inputs:
    bool:
        type: bool
steps: []
"""
        )
    with pytest.raises(ValueError, match="Input bool must be a boolean"):
        runner.execute_workflow("validate_bool", {"bool": "not a bool"})
    with pytest.raises(ValueError, match="Input bool must be a boolean"):
        runner.execute_workflow("validate_bool", {"bool": 3.14})
    runner.execute_workflow("validate_bool", {"bool": "True"})
    runner.execute_workflow("validate_bool", {"bool": "False"})
    runner.execute_workflow("validate_bool", {"bool": True})


def test_validate_string(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "validate_string.yml", "w") as f:
        f.write(
            """
inputs:
    string:
        type: str
steps: []
"""
        )
    runner.execute_workflow("validate_string", {"string": 3.14})
    runner.execute_workflow("validate_string", {"string": []})


def test_validate_list(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "validate_list.yml", "w") as f:
        f.write(
            """
inputs:
    list:
        type: list
steps: []
"""
        )
    with pytest.raises(ValueError, match="Input list must be a list"):
        runner.execute_workflow("validate_list", {"list": "not a list"})
    with pytest.raises(ValueError, match="Input list must be a list"):
        runner.execute_workflow("validate_list", {"list": 3.14})
    runner.execute_workflow("validate_list", {"list": [1, 2, 3]})


def test_validate_dict(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "validate_dict.yml", "w") as f:
        f.write(
            """
inputs:
    dict:
        type: dict
steps: []
"""
        )
    with pytest.raises(ValueError, match="Input dict must be a dict"):
        runner.execute_workflow("validate_dict", {"dict": "not a dict"})
    with pytest.raises(ValueError, match="Input dict must be a dict"):
        runner.execute_workflow("validate_dict", {"dict": 3.14})
    runner.execute_workflow("validate_dict", {"dict": {"key": "value"}})


def test_invalid_input_type(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()
    with open(config_dir / "workflows" / "invalid_input_type.yml", "w") as f:
        f.write(
            """
inputs:
    invalid_input:
        type: invalid_type
steps: []
"""
        )
    with pytest.raises(
        ValueError,
        match="1 validation error for WorkflowMetadata\ninputs.invalid_input.type\n.*",
    ):
        runner.execute_workflow("invalid_input_type", {"invalid_input": "value"})
