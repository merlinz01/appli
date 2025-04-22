def test_load_script_metadata():
    from tarmac.metadata import ScriptMetadata

    script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "dependency>=2.1",
# ]
# ///

# /// tarmac
# description: |
#   This is the description.
#   It can be multi-line.
# inputs:
#   string_input:
#     type: str
#   integer_input:
#     type: int
#   float_input:
#     type: float
#   boolean_input:
#     type: bool
#   list_input:
#     type: list
#   dict_input:
#     type: dict
#   input_with_description:
#     type: str
#     description: This is the description of the input.
#   input_with_default:
#     type: str
#     default: "default_value"
#   input_with_required:
#     type: str
#     required: true
#   input_with_default_and_required:
#     type: str
#     default: "default_value"
#     required: false
#   input_with_example:
#     type: str
#     example: "example_value"
# outputs:
#   string_output:
#     type: str
#   integer_output:
#     type: int
#   float_output:
#     type: float
#   boolean_output:
#     type: bool
#   list_output:
#     type: list
#   dict_output:
#     type: dict
#   output_with_description:
#     type: str
#     description: This is the description of the output.
#   output_with_example:
#     type: str
#     example: "example_value"
# ///

import dependency
from tarmac.operations import OperationInterface, run


def MyOperation(op: OperationInterface):
    op.log("Running MyOperation")


run(MyOperation)
"""

    metadata = ScriptMetadata.load(script)
    assert metadata.description == "This is the description.\nIt can be multi-line.\n"
    assert metadata.inputs["string_input"].type == "str"
    assert metadata.inputs["integer_input"].type == "int"
    assert metadata.inputs["float_input"].type == "float"
    assert metadata.inputs["boolean_input"].type == "bool"
    assert metadata.inputs["list_input"].type == "list"
    assert metadata.inputs["dict_input"].type == "dict"
    assert (
        metadata.inputs["input_with_description"].description
        == "This is the description of the input."
    )
    assert metadata.inputs["input_with_default"].default == "default_value"
    assert metadata.inputs["input_with_required"].required is True
    assert metadata.inputs["input_with_default_and_required"].default == "default_value"
    assert metadata.inputs["input_with_default_and_required"].required is False
    assert metadata.inputs["input_with_example"].example == "example_value"
    assert metadata.outputs["string_output"].type == "str"
    assert metadata.outputs["integer_output"].type == "int"
    assert metadata.outputs["float_output"].type == "float"
    assert metadata.outputs["boolean_output"].type == "bool"
    assert metadata.outputs["list_output"].type == "list"
    assert metadata.outputs["dict_output"].type == "dict"
    assert (
        metadata.outputs["output_with_description"].description
        == "This is the description of the output."
    )
    assert metadata.outputs["output_with_example"].example == "example_value"


def test_load_workflow_metadata():
    from tarmac.metadata import WorkflowMetadata

    workflow = """
# This is YAML syntax
inputs:
    example_input:
        type: str
        description: This is an example input
        default: "default_value"
        required: true
        example: "example_value"
outputs:
    example_output:
        type: str
        description: This is an example output
        example: "example_value"
steps:
    - name: An example step
      id: example
      do: example_operation
      with:
        example_input: "example_value"
      if: foo.bar == 'baz'
    - name: Another example step
      run: apt-get update
      with:
        cwd: /tmp
        env:
            FOO: bar
            BAZ: qux
    - workflow: example_workflow

"""

    metadata = WorkflowMetadata.load(workflow)
    assert metadata.inputs["example_input"].type == "str"
    assert metadata.inputs["example_input"].description == "This is an example input"
    assert metadata.inputs["example_input"].default == "default_value"
    assert metadata.inputs["example_input"].required is True
    assert metadata.inputs["example_input"].example == "example_value"
    assert metadata.outputs["example_output"].type == "str"
    assert metadata.outputs["example_output"].description == "This is an example output"
    assert metadata.outputs["example_output"].example == "example_value"
    assert len(metadata.steps) == 3
    assert metadata.steps[0].name == "An example step"
    assert metadata.steps[0].id == "example"
    assert metadata.steps[0].do == "example_operation"
    assert metadata.steps[0].params["example_input"] == "example_value"
    assert metadata.steps[0].condition == "foo.bar == 'baz'"
    assert metadata.steps[1].name == "Another example step"
    assert metadata.steps[1].run == "apt-get update"
    assert metadata.steps[1].params["cwd"] == "/tmp"
    assert isinstance(metadata.steps[1].params["env"], dict)
    assert metadata.steps[1].params["env"]["FOO"] == "bar"
    assert metadata.steps[1].params["env"]["BAZ"] == "qux"
    assert metadata.steps[2].workflow == "example_workflow"
    assert metadata.steps[2].name == ""
