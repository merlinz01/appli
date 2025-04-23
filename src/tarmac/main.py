import argparse
import os
import logging
import sys
import yaml
import json
from . import __version__

from .runner import Runner


def main(args=None):
    parser = argparse.ArgumentParser(
        prog="tarmac",
        description="Execute a tarmac workflow",
        epilog="See https://github.com/merlinz01/tarmac for more information.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version and exit",
    )
    parser.add_argument(
        "workflow",
        type=str,
        help="The workflow to execute",
    )
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
        choices=["json", "yaml", "text"],
        default="text",
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
        elif args.output_format == "yaml":
            print(yaml.safe_dump(result, indent=2), file=file)
        else:
            print_object_text(result, indent=0, file=file)

    def print_object_text(obj, indent=0, file=sys.stdout):
        if isinstance(obj, str):
            lines = obj.splitlines() or ['""']
            for line in lines:
                print(" " * indent + line, file=file)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                print(" " * indent + str(key) + ":", file=file, end="")
                if isinstance(
                    value, (str, int, float, bool, type(None))
                ) and "\n" not in str(value):
                    print(" ", file=file, end="")
                    print_object_text(value, indent=0, file=file)
                else:
                    print(file=file)
                    print_object_text(value, indent=indent + 2, file=file)
        else:
            print(" " * indent + str(obj), file=file)

    if args.output_file:
        if args.output_file == "-":
            print_result(sys.stdout)
        else:
            with open(args.output_file, "w") as file:
                print_result(file)
