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
            print(
                "\n(Note: this output is meant to be human-readable. Use JSON format for parsing.)\n",
                file=file,
            )
            print_object_text(result, indent=0, file=file)

    def print_object_text(obj, indent=0, file=sys.stdout):
        max_length = 100
        scalars = (str, int, float, bool, type(None))
        if isinstance(obj, str):
            lines = obj.splitlines() or ['""']
            for line in lines:
                while True:
                    print(" " * indent + line[:max_length], file=file)
                    line = line[max_length:]
                    if not line:
                        break
        elif isinstance(obj, dict):
            for key, value in obj.items():
                print(" " * indent + (str(key) or '""') + ":", file=file, end="")
                if (
                    isinstance(value, scalars)
                    and "\n" not in (s := str(value))
                    and len(s) < max_length
                ):
                    print(" ", file=file, end="")
                    print_object_text(s, indent=0, file=file)
                else:
                    print(file=file)
                    print_object_text(value, indent=indent + 2, file=file)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                if (
                    isinstance(item, scalars)
                    and "\n" not in (s := str(item))
                    and len(s) < max_length
                ):
                    print(" " * indent + "- ", file=file, end="")
                    print_object_text(s, indent=0, file=file)
                else:
                    print(" " * indent + "-\u2935", file=file)
                    print_object_text(item, indent=indent + 2, file=file)
        else:
            print(" " * indent + str(obj), file=file)

    if args.output_file:
        if args.output_file == "-":
            print_result(sys.stdout)
        else:
            with open(args.output_file, "w") as file:
                print_result(file)
