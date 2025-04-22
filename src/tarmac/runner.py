import json
import os
import subprocess
import sys
import tempfile
from uv import find_uv_bin
from .metadata import ScriptMetadata, JobMetadata, ValueMapping, JobStep
from logging import getLogger
import dotmap

logger = getLogger(__name__)


class Runner:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def find_uv_bin(self):
        return find_uv_bin()

    def _get_job_filename(self, name: str) -> str:
        return os.path.join(self.base_path, "jobs", name + ".yml")

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
            cmd = [
                self.find_uv_bin(),
                "run",
                "--color",
                "never",
                "--no-progress",
                "--no-config",
                "--no-project",
                "--no-env-file",
                "--with",
                "tarmac",
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
            logger.info(f"Executing {cmd}")
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

    def execute_job(self, name: str, inputs: ValueMapping) -> ValueMapping:
        filename = self._get_job_filename(name)
        try:
            with open(filename) as f:
                metadata = JobMetadata.load(f.read())
        except FileNotFoundError as e:
            raise ValueError(f"job {name} not found") from e
        inputs = metadata.validate_inputs(inputs)
        for step in metadata.steps:
            step.validate_job_type()
        outputs = {}
        outputs["succeeded"] = True
        outputs["steps"] = {}
        for step in metadata.steps:
            if step.condition is not None and not self.evaluate_condition(
                step.condition, inputs, outputs
            ):
                continue
            out = self.execute_job_step(step, inputs)
            outputs["steps"][step.id] = out
            if not out.get("succeeded", True):
                outputs["succeeded"] = False
                break
        return outputs

    def execute_shell(self, script: str, inputs: ValueMapping) -> ValueMapping:
        p = subprocess.Popen(
            script,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        stdout, stderr = p.communicate()
        return {
            "output": stdout,
            "error": stderr,
            "returncode": p.returncode,
            "succeeded": p.returncode == 0,
        }

    def execute_job_step(self, step: JobStep, inputs: ValueMapping) -> ValueMapping:
        if step.type == "script":
            assert step.do is not None
            out = self.execute_script(step.do, step.params)
        elif step.type == "job":
            assert step.job is not None
            out = self.execute_job(step.job, step.params)
        elif step.type == "shell":
            assert step.run is not None
            out = self.execute_shell(step.run, step.params)
        else:
            raise ValueError("unknown step type")
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
