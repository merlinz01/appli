from pathlib import Path


def test_run_operation(config_dir: Path) -> None:
    """
    Test the run function in the operations module.
    """
    import json
    import os
    from tarmac.operations import run, OperationInterface

    # Create a temporary input file
    inputs = {"key": "value"}
    inputs_file = config_dir / "inputs.json"
    with open(inputs_file, "w") as f:
        json.dump(inputs, f)

    # Set the environment variable for the input file
    os.environ["TARMAC_INPUTS_FILE"] = str(inputs_file)
    os.environ["TARMAC_OUTPUTS_FILE"] = str(config_dir / "outputs.json")

    # Define a simple operation function
    def operation(op: OperationInterface) -> None:
        op.log("Running operation")
        op.changed()
        op.outputs["key"] = op.inputs["key"] + " output"

    # Run the operation
    run(operation)

    # Check the output file
    with open(os.environ["TARMAC_OUTPUTS_FILE"]) as f:
        outputs = json.load(f)

    assert outputs["succeeded"] is True
    assert outputs["changed"] is True
    assert "error" not in outputs
    assert outputs["output"] == "Running operation\n"
    assert outputs["key"] == "value output"
