import io
import json
import os
import traceback


class Failure(Exception):
    """Generic exception raised when an operation fails."""


class OperationInterface:
    def __init__(self):
        self.inputs = {}
        self.outputs = {}
        self._output_stream = io.StringIO()

    def log(self, message: str) -> None:
        output = self._output_stream
        output.write(message)
        output.write("\n")
        print(message)

    def changed(self, changed=True) -> None:
        self.outputs["changed"] = changed


def run(func):
    op = OperationInterface()
    with open(os.environ["TARMAC_INPUTS_FILE"]) as f:
        inputs = json.load(f)
    op.inputs = inputs
    op.inputs["changed"] = False
    try:
        func(op)
        op.outputs["succeeded"] = True
    except Failure as e:
        op.outputs["succeeded"] = False
        op.outputs["error"] = str(e)
    except Exception:
        op.outputs["succeeded"] = False
        op.outputs["error"] = traceback.format_exc()
    finally:
        op.outputs["output"] = op._output_stream.getvalue()
        outputs = op.outputs
        with open(os.environ["TARMAC_OUTPUTS_FILE"], "w") as f:
            f.write(json.dumps(outputs))
