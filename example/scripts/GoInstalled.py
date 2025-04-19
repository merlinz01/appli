# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///

# /// tarmac
# description: |
#   This operation installs the specified version of Go.
# additional_uv_args: []
# inputs:
#   version:
#     type: str
#     description: The version of Go to install, or "latest" for the latest version.
#     default: "latest"
#     required: false
#     example: "1.20.3"
#   base_path:
#     type: str
#     description: The base path to install Go to.
#     default: "/usr/local"
#     required: false
#   dry_run:
#     type: bool
#     description: If true, the operation will not make any changes.
#     default: false
#     required: false
# outputs:
#   installed_version:
#     type: str
#     description: The version of Go that was installed.
#   previous_version:
#     type: str
#     description: The version of Go that was previously installed, or None if no version was installed.
# ///

import subprocess
import tarfile
import tempfile
import os
import shutil
import requests  # type: ignore
from tarmac.operations import OperationInterface, run


def GoInstalled(op: OperationInterface):
    if op.inputs["version"] == "latest":
        version = (
            requests.get("https://golang.org/VERSION?m=text")
            .text.strip()
            .splitlines()[0]
            .removeprefix("go")
        )
    else:
        version = op.inputs["version"]
        r = requests.head(f"https://golang.org/dl/go{version}.linux-amd64.tar.gz")
        r.raise_for_status()
    op.outputs["installed_version"] = version
    op.log(f"Checking for Go {version}")
    try:
        p = subprocess.run(
            [
                os.path.join(op.inputs["base_path"], "go", "bin", "go"),
                "version",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        installed_version = None
    else:
        if p.returncode != 0:
            installed_version = None
        else:
            installed_version = p.stdout.split()[2].removeprefix("go")
    op.outputs["previous_version"] = installed_version
    if installed_version:
        if installed_version == version:
            op.log(f"Go {version} is already installed")
            return
        op.log(f"Go {installed_version} is currently installed")
    uninstall = os.path.exists(os.path.join(op.inputs["base_path"], "go"))
    if op.inputs["dry_run"]:
        if uninstall:
            op.log(f"Would uninstall Go ({installed_version})")
        op.log(f"Would install Go {version}")
        op.changed()
        return
    if uninstall:
        op.log(f"Uninstalling Go ({installed_version})...")
        shutil.rmtree(os.path.join(op.inputs["base_path"], "go"))
        op.log(f"Successfully uninstalled Go {installed_version}.")
    op.log(f"Installing Go {version}")
    dl_url = f"https://golang.org/dl/go{version}.linux-amd64.tar.gz"
    with tempfile.TemporaryFile() as archive:
        op.log(f"Downloading {dl_url}...")
        r = requests.get(dl_url)
        r.raise_for_status()
        archive.write(r.content)
        op.log(f"Extracting archive to {op.inputs['base_path']}...")
        archive.seek(0)
        with tarfile.open(fileobj=archive, mode="r:gz") as tar:
            tar.extractall(path=op.inputs["base_path"])
    op.changed()
    op.log(f"Successfully installed Go {version} to {op.inputs['base_path']}.")


run(GoInstalled)
