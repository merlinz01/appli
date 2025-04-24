import json
import logging
import os
import subprocess
import sys
import tempfile
import traceback

import dotmap
from uv import find_uv_bin

from tarmac.operations import Failure

from .metadata import ScriptMetadata, ValueMapping, WorkflowMetadata, WorkflowStep

logger = logging.getLogger(__name__)


class Runner:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._uv_bin = None

    def _find_uv_bin(self):
        if not self._uv_bin:
            self._uv_bin = find_uv_bin()
        return self._uv_bin

    def _get_workflow_filename(self, name: str) -> str:
        return os.path.join(self.base_path, "workflows", name + ".yml")

    def _get_script_filename(self, name: str) -> str:
        return os.path.join(self.base_path, "scripts", name + ".py")

    def execute_script(self, name: str, inputs: ValueMapping) -> ValueMapping:
        filename = self._get_script_filename(name)
        try:
            with open(filename) as f:
                metadata = ScriptMetadata.load(f.read())
        except FileNotFoundError as e:
            raise ValueError(f"script {name} not found") from e
        inputs = metadata.validate_inputs(inputs)
        with (
            tempfile.NamedTemporaryFile(mode="wb") as inputs_file,
            tempfile.NamedTemporaryFile(mode="w+b") as outputs_file,
        ):
            with_tarmac = ["--with", "tarmac"]
            if os.environ.get("TARMAC_EDITABLE_INSTALL"):
                with_tarmac = ["--with-editable", "."]
            cmd = [
                self._find_uv_bin(),
                "run",
                "--color",
                "never",
                "--no-progress",
                "--no-config",
                "--no-project",
                "--no-env-file",
                "--native-tls",
                *with_tarmac,
                "--script",
            ]
            cmd.extend(metadata.additional_uv_args)
            cmd.append(filename)
            os.chmod(inputs_file.name, 0o600)
            os.chmod(outputs_file.name, 0o600)
            inputs_file.write(json.dumps(inputs).encode("utf-8"))
            inputs_file.flush()
            inputs_file.seek(0)
            outputs_file.write(b"{}")
            outputs_file.flush()
            env = os.environ.copy()
            env["TARMAC_INPUTS_FILE"] = inputs_file.name
            env["TARMAC_OUTPUTS_FILE"] = outputs_file.name
            p = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = p.communicate()
            try:
                outputs_file.seek(0)
                outputs = json.load(outputs_file.file)
            except json.JSONDecodeError:
                logger.warning("Failed to decode JSON from outputs file")
                outputs = {
                    "succeeded": False,
                    "error": "Failed to decode JSON from outputs file",
                }
            if p.returncode != 0:
                if stdout:
                    outputs["output"] = stdout
                if stderr:
                    outputs["error"] = stderr
                outputs["succeeded"] = False
            else:
                if stdout:
                    outputs.setdefault("output", stdout)
                if stderr:
                    outputs.setdefault("error", stderr)
                outputs.setdefault("succeeded", True)
            return outputs

    def execute_shell(
        self, script: str | list[str], inputs: ValueMapping
    ) -> ValueMapping:
        env = os.environ.copy()
        env.update(inputs.pop("env", {}))
        cwd = inputs.pop("cwd", os.getcwd())
        stdin = inputs.pop("stdin", None)
        try:
            invalid = next(iter(inputs))
            raise ValueError(f"Invalid input for shell script: {invalid}")
        except StopIteration:
            pass
        if isinstance(script, str):
            script = [script]
        out: ValueMapping = {
            "succeeded": True,
            "output": "",
            "error": "",
            "returncode": 0,
        }
        for s in script:
            p = subprocess.Popen(
                s,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if stdin else None,
                text=True,
                env=env,
                cwd=cwd,
                encoding="utf-8",
                errors="replace",
            )
            stdout, stderr = p.communicate(stdin)
            stdin = None  # only pass stdin to the first command
            out["returncode"] = p.returncode
            out["output"] += stdout
            out["error"] += stderr
            if p.returncode != 0:
                out["succeeded"] = False
                break
            else:
                out["succeeded"] = True
        return out

    def execute_python(
        self, script: str, inputs: ValueMapping, steps: ValueMapping
    ) -> ValueMapping:
        env = {
            "inputs": inputs,
            "outputs": {},
            "steps": steps,
            "Failure": Failure,
        }
        try:
            exec(script, env)
        except BaseException:
            return {"succeeded": False, "error": traceback.format_exc()}
        out: dict = env.get("outputs", {})
        out.setdefault("succeeded", True)
        return out

    def execute_workflow(self, name: str, inputs: ValueMapping) -> ValueMapping:
        filename = self._get_workflow_filename(name)
        try:
            with open(filename) as f:
                metadata = WorkflowMetadata.load(f.read())
        except FileNotFoundError as e:
            raise ValueError(f"Workflow {name} not found") from e
        inputs = metadata.validate_inputs(inputs)
        for step in metadata.steps:
            step.validate_workflow_type()
        outputs = {}
        outputs["succeeded"] = True
        outputs["steps"] = {}
        for step in metadata.steps:
            out = self.execute_workflow_step(step, inputs, outputs)
            succeeded = out.get("succeeded", True)
            if succeeded is not None and not succeeded:
                outputs["succeeded"] = False
                break
        return outputs

    def execute_workflow_step(
        self, step: WorkflowStep, inputs: ValueMapping, outputs: ValueMapping
    ) -> ValueMapping:
        if step.condition is not None and not self.evaluate_condition(
            step.condition, inputs, outputs
        ):
            out = {"succeeded": None}
        elif step.type == "script":
            assert step.do is not None
            out = self.execute_script(step.do, step.params)
        elif step.type == "shell":
            assert step.run is not None
            out = self.execute_shell(step.run, step.params)
        elif step.type == "python":
            assert step.py is not None
            out = self.execute_python(step.py, step.params, outputs["steps"])
        elif step.type == "workflow":
            assert step.workflow is not None
            out = self.execute_workflow(step.workflow, step.params)
        else:
            raise ValueError("unknown step type")
        assert isinstance(outputs["steps"], dict)
        assert step.id is not None
        outputs["steps"][step.id] = out
        self.workflow_step_hook(step, out)
        return out

    def _run_command(self, cmd: str, **params) -> ValueMapping:
        return dotmap.DotMap(self.execute_shell(cmd, params))

    _run_command.__name__ = "run"

    def evaluate_condition(
        self, cond, inputs: ValueMapping, outputs: ValueMapping
    ) -> bool:
        if isinstance(cond, bool):
            return cond
        if not isinstance(cond, str):
            raise ValueError("Invalid condition type")
        env = {
            "inputs": dotmap.DotMap(inputs),
            "steps": dotmap.DotMap(outputs["steps"]),
            "run": self._run_command,
            "platform": sys.platform,
        }
        code = compile(f"({cond})", "<condition>", "eval")
        return bool(eval(code, env, {}))

    def workflow_step_hook(self, step: WorkflowStep, outputs: ValueMapping) -> None:
        """
        This method is called after each workflow step is executed.
        It can be used by subclasses to perform additional actions, such as logging or
        notifying the user.
        """
        logger.info(f"Step {step.name or step.id or '<unnamed>'} executed")
