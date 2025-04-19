import argparse
import yaml
import logging

from .runner import Runner


def main(args=None):
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Execute a script with inputs")
    parser.add_argument("job", type=str, help="The job to execute")
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

    runner = Runner(base_path="example")
    result = runner.execute_job(args.job, inputs)
    print()
    print(yaml.dump(result, indent=2))
