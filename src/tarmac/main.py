import argparse
import os
import logging
import yaml

from .runner import Runner


def main(args=None):
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Execute a script with inputs")
    parser.add_argument("workflow", type=str, help="The workflow to execute")
    parser.add_argument(
        "-b",
        "--base-path",
        type=str,
        help="The path to the workspace containing the scripts and inputs",
    )
    parser.add_argument(
        "-i",
        "--inputs",
        metavar="key=value",
        type=str,
        nargs="+",
        help="The inputs to pass to the script",
    )
    args = parser.parse_args(args)

    inputs = {}
    if args.inputs:
        for input_ in args.inputs:
            key, value = input_.split("=")
            inputs[key] = value

    runner = Runner(
        base_path=args.base_path
        or os.environ.get("TARMAC_BASE_PATH", "")
        or os.getcwd()
    )
    result = runner.execute_workflow(args.workflow, inputs)
    print()
    print(yaml.dump(result, indent=2))
