import argparse
import os
import logging
import sys
import yaml
import json

from .runner import Runner


def main(args=None):
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
        help="An input to pass to the script",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "yaml"],
        default="json",
        help="Output format for the result",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        default="-",
        metavar="FILE",
        help="File to write the output to. If not specified or '-', output will be printed to stdout.",
    )

    args = parser.parse_args(args)

    logging.basicConfig(level=args.log_level)

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

    def print_result(file):
        if args.output_format == "json":
            print(json.dumps(result, indent=2), file=file)
        else:
            print(yaml.safe_dump(result, indent=2), file=file)

    if args.output_file:
        if args.output_file == "-":
            print_result(sys.stdout)
        else:
            with open(args.output_file, "w") as file:
                print_result(file)
