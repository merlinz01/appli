import re
from typing import Any, Iterator, Literal, Self, TypeAlias

import yaml
from pydantic import BaseModel, Field

REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"


def _metadata_stream(script: str) -> Iterator[tuple[str, str]]:
    for match in re.finditer(REGEX, script):
        yield (
            match.group("type"),
            "".join(
                line[2:] if line.startswith("# ") else line[1:]
                for line in match.group("content").splitlines(keepends=True)
            ),
        )


IOTypeString: TypeAlias = Literal["str", "int", "float", "bool", "list", "dict"]
IOType: TypeAlias = Any
ValueMapping: TypeAlias = dict[str, IOType]


class Input(BaseModel):
    """
    Describes an input for a workflow step.
    """

    name: str = ""
    """
    The name of the input.
    """

    type: IOTypeString = "str"
    """
    The type of the input.
    Can be one of: str, int, float, bool, list, dict.
    """

    description: str = ""
    """
    A description of the input.
    """

    default: IOType = None
    """
    The default value of the input.
    Not required if the input is required.
    """

    required: bool = True
    """
    Whether the input is required.
    If True, the input must be provided.
    If False, the default value will be used if not provided.
    """

    example: Any = None
    """
    An example value for the input.
    This is used for documentation purposes only.
    """


class Output(BaseModel):
    """
    Describes an output for a workflow step.
    """

    name: str = ""
    """
    The name of the output.
    """

    type: IOTypeString = "str"
    """
    The type of the output.
    Can be one of: str, int, float, bool, list, dict.
    The type is not validated at runtime.
    """

    description: str = ""
    """
    A description of the output.
    """

    example: Any = None
    """
    An example value for the output.
    This is used for documentation purposes only.
    """


class Metadata(BaseModel):
    """
    Common metadata for all operations.
    """

    inputs: dict[str, Input] = Field(default_factory=dict)
    """
    A dictionary of inputs for the operation.
    The keys are the names of the inputs.
    The values are Input objects.
    """

    outputs: dict[str, Output] = Field(default_factory=dict)
    """
    A dictionary of outputs for the operation.
    The keys are the names of the outputs.
    The values are Output objects.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        for name, input in self.inputs.items():
            input.name = name
        for name, output in self.outputs.items():
            output.name = name

    def validate_inputs(self, inputs: ValueMapping) -> ValueMapping:
        res = {}
        for input in self.inputs.values():
            if input.name not in inputs:
                if input.required:
                    raise ValueError(f"Missing required input: {input.name}")
                value = input.default
            else:
                value = inputs[input.name]
            res[input.name] = self.validate_type(input.name, value, input.type)
        for unknown_key in set(inputs) - set(self.inputs):
            raise ValueError(f"Unknown input: {unknown_key}")
        return res

    def validate_type(self, name: str, value: IOType, type_: IOTypeString) -> Any:
        if type_ == "str":
            return str(value)
        if type_ == "int":
            if isinstance(value, str):
                try:
                    return int(value)
                except ValueError:
                    raise ValueError(f"Input {name} must be an integer")
            if not isinstance(value, int):
                raise ValueError(f"Input {name} must be an integer")
            return value
        if type_ == "float":
            if isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    raise ValueError(f"Input {name} must be a float")
            if not isinstance(value, (float, int)):
                raise ValueError(f"Input {name} must be a float")
            return float(value)
        if type_ == "bool":
            if isinstance(value, str):
                if value.lower() in ("true", "1"):
                    return True
                elif value.lower() in ("false", "0"):
                    return False
            if not isinstance(value, bool):
                raise ValueError(f"Input {name} must be a boolean")
            return value
        if type_ == "list":
            if not isinstance(value, list):
                raise ValueError(f"Input {name} must be a list, got {value!r}")
            return value
        if type_ == "dict":
            if not isinstance(value, dict):
                raise ValueError(f"Input {name} must be a dict")
            return value
        raise ValueError(f"Invalid input type: {type_}")  # pragma: no cover


class ScriptMetadata(Metadata):
    """
    Metadata for a Python script.
    """

    description: str = ""
    """
    A description of the operation.
    """

    dependencies: list[str] = []
    """
    A list of dependencies for the script.
    The dependencies are installed in the environment before the script is run.
    You can specify versions in PEP 508 format.
    """

    additional_uv_args: list[str] = []
    """
    A list of additional arguments to pass to the script runner (the uv command).
    """

    @classmethod
    def load(cls, script: str) -> Self:
        metadata = None
        for type_, content in _metadata_stream(script):
            if type_ == "tarmac":
                metadata = yaml.safe_load(content)
                break
        if metadata is None:
            metadata = {}
        return cls(**metadata)


WorkflowType: TypeAlias = Literal["script", "shell", "python", "workflow"]


class WorkflowStep(BaseModel):
    """
    Describes a workflow step.
    """

    id: str | None = None
    """
    The ID of the workflow step.
    If not provided, the ID will be set to the name of the workflow step.
    """

    type: WorkflowType | None = None
    """
    The type of the workflow step.
    Can be one of: script, workflow, shell.
    The type will be set based on the presence of the `do`, `run`, or `workflow` fields.
    """

    name: str = ""
    """
    The human-readable name of the workflow step.
    """

    do: str | None = None
    """
    The script to run.
    If provided, the type will be set to "script".
    """

    run: str | list[str] | None = None
    """
    The shell command to run.
    Can be a list to run multiple commands.
    If provided, the type will be set to "shell".
    """

    py: str | None = None
    """
    The Python script to run.
    If provided, the type will be set to "script".
    """

    workflow: str | None = None
    """
    The workflow to run.
    If provided, the type will be set to "workflow".
    """

    params: ValueMapping = Field(alias="with", default_factory=dict)
    """
    The inputs to pass to the workflow step.
    """

    condition: Any = Field(alias="if", default=None)
    """
    The condition to run the workflow step.
    If provided, the workflow step will only run if the condition is true.
    """

    model_config = {
        "extra": "forbid",
    }

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if not self.id:
            self.id = self.name

    def validate_workflow_type(self):
        if self.type is not None:
            raise ValueError(
                "Do not set `type` manually, use the relevant parameter instead"
            )
        if self.do is not None:
            if self.run is not None:
                raise ValueError("Cannot use `run` with `do`")
            if self.workflow is not None:
                raise ValueError("Cannot use `workflow` with `do`")
            if self.py is not None:
                raise ValueError("Cannot use `py` with `do`")
            self.type = "script"
        elif self.run is not None:
            if self.workflow is not None:
                raise ValueError("Cannot use `workflow` with `run`")
            if self.py is not None:
                raise ValueError("Cannot use `py` with `run`")
            self.type = "shell"
        elif self.py is not None:
            if self.workflow is not None:
                raise ValueError("Cannot use `workflow` with `py`")
            self.type = "python"
        elif self.workflow is not None:
            self.type = "workflow"
        else:
            raise ValueError("Must have either `do`, `run`, `py`, or `workflow`")


class WorkflowMetadata(Metadata):
    """
    Metadata for a workflow.
    """

    description: str = ""
    """
    A description of the workflow.
    """

    steps: list[WorkflowStep] = Field(default_factory=list)
    """
    A list of workflow steps.
    The steps are executed in order.
    """

    @classmethod
    def load(cls, file: str) -> Self:
        metadata = yaml.safe_load(file)
        if metadata is None:
            metadata = {}
        return cls(**metadata)
