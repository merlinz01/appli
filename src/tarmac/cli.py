import argparse
import json
import logging
import os
import sys
from typing import Any, TextIO

import yaml

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
        "--script",
        action="store_true",
        help="Run a script instead of a workflow",
    )
    parser.add_argument(
        "workflow",
        type=str,
        help="The workflow (or script if --script is given) to execute",
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
        choices=["json", "yaml", "text", "colored-text"],
        default="colored-text",
        help="Output format for the result",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
        type=lambda x: x.upper(),
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
    if args.script:
        result = runner.execute_script(args.workflow, inputs)
    else:
        result = runner.execute_workflow(args.workflow, inputs)

    def print_result(file: TextIO):
        if args.output_format == "json":
            file.write(json.dumps(result, indent=2))
        elif args.output_format == "yaml":
            file.write(yaml.safe_dump(result, indent=2))
        else:
            colors = {
                "red": "",
                "green": "",
                "yellow": "",
                "blue": "",
                "magenta": "",
                "cyan": "",
                "white": "",
                None: "",
            }
            if args.output_format == "colored-text":
                colors = {
                    "red": "\033[31m",
                    "green": "\033[32m",
                    "yellow": "\033[33m",
                    "blue": "\033[34m",
                    "magenta": "\033[35m",
                    "cyan": "\033[36m",
                    "white": "\033[37m",
                    None: "\033[0m",
                }
            file.write(colors["cyan"])
            file.write(
                "\n(Note: this output is meant to be human-readable."
                " Use JSON format for parsing.)\n\n",
            )
            file.write(colors[None])
            print_object_text(result, 0, file, colors)

    def print_object_text(obj: Any, indent: int, file: TextIO, colors: dict):
        max_length = 100
        scalars = (type(None), bool, str, int, float, complex)
        type_colors = {
            type(None): colors["magenta"],
            bool: colors["cyan"],
            str: colors["green"],
            int: colors["yellow"],
            float: colors["yellow"],
            complex: colors["yellow"],
        }
        if isinstance(obj, str):
            lines = obj.splitlines() or ['""']
            for line in lines:
                while True:
                    file.write(" " * indent)
                    file.write(colors["green"])
                    file.write(line[:max_length])
                    file.write(colors[None])
                    line = line[max_length:]
                    if not line:
                        break
                    file.write(colors["yellow"])
                    file.write(" \u2935")
                    file.write(colors[None])
                    file.write("\n")
                file.write("\n")
        elif isinstance(obj, dict):
            for key, value in obj.items():
                file.write(" " * indent)
                file.write(colors["blue"])
                file.write(str(key) or '""')
                file.write(colors[None])
                file.write(":")
                if (
                    isinstance(value, scalars)
                    and "\n" not in (s := str(value) or "")
                    and len(s) < max_length
                ):
                    file.write(" ")
                    file.write(type_colors.get(type(value), colors[None]))
                    file.write(str(value) or '""')
                    file.write(colors[None])
                    file.write("\n")
                else:
                    file.write("\n")
                    file.write(type_colors.get(type(value), colors[None]))
                    print_object_text(value, indent + 2, file, colors)
                    file.write(colors[None])
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                if (
                    isinstance(item, scalars)
                    and "\n" not in (s := str(item) or "")
                    and len(s) < max_length
                ):
                    file.write(" " * indent)
                    file.write(colors["blue"])
                    file.write("- ")
                    file.write(type_colors.get(type(item), colors[None]))
                    file.write(str(item) or '""')
                    file.write(colors[None])
                    file.write("\n")
                else:
                    file.write(" " * indent)
                    file.write(colors["blue"])
                    file.write("-\u2935\n")
                    file.write(type_colors.get(type(item), colors[None]))
                    print_object_text(item, indent + 2, file, colors)
                    file.write(colors[None])
        else:  # pragma: no cover
            file.write(" " * indent)
            file.write(colors["red"])
            file.write(repr(obj))
            file.write(colors[None])
            file.write("\n")

    if args.output_file:
        if args.output_file == "-":
            print_result(sys.stdout)
        else:
            with open(args.output_file, "w") as file:
                print_result(file)
