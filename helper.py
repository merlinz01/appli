import argparse

parser = argparse.ArgumentParser(
    description="Helper program for various tasks in this repo."
)
command = parser.add_subparsers(dest="command", required=True)

# bump-version
bump_version = command.add_parser(
    "bump-version",
    help="Bump the version of the package.",
)
bump_version.add_argument(
    "--version",
    type=str,
    help="The new version to set.",
)

args = parser.parse_args()
if args.command == "bump-version":
    import re
    import subprocess

    # Check for uncommitted changes
    result = subprocess.run(
        ["git", "diff-index", "--quiet", "HEAD"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        print(
            "Uncommitted changes detected. Please commit or stash them before running this script."
        )
        exit(1)

    # Load the current version from __version__.py
    with open("src/tarmac/__version__.py", "r") as f:
        env = {}
        exec(f.read(), env)
    current_version = env["__version__"]
    print(f"Current version: {current_version}")

    # Automatically bump the version if not provided
    if args.version is None:
        major, minor, patch = map(int, current_version.split("."))
        patch += 1
        args.version = f"{major}.{minor}.{patch}"

    print(f"New version: {args.version}")

    # Check if the version is already set
    if args.version == current_version:
        print(f"Version {args.version} is already set.")
        exit(0)

    # Update the version in pyproject.toml
    with open("pyproject.toml", "r+b") as f:
        content = f.read()
        new_content = re.sub(
            rb'(?<=version = ")[0-9]+\.[0-9]+\.[0-9]+(?=")',
            args.version.encode(),
            content,
        )
        if new_content == content:
            print("Version not found in pyproject.toml.")
            exit(1)
        f.seek(0)
        f.write(new_content)
        f.truncate()

    # Update the version in __version__.py
    with open("src/tarmac/__version__.py", "w") as f:
        f.write(f'__version__ = "{args.version}"\n')

    # Sync the venv
    subprocess.run(["uv", "sync"], check=True)

    # Update the changelog
    with open("CHANGELOG.md", "r+b") as f:
        content = f.read()
        new_content = re.sub(
            rb"\n## \[Unreleased\]\n\n",
            f"\n## [Unreleased]\n\n## [{args.version}]\n\n".encode(),
            content,
        )
        if new_content == content:
            print("Unreleased marker not found in CHANGELOG.md.")
            exit(1)
        f.seek(0)
        f.write(new_content)
        f.truncate()
        print("Changelog updated.")

    # Commit the changes
    subprocess.run(
        [
            "git",
            "add",
            "pyproject.toml",
            "uv.lock",
            "src/tarmac/__version__.py",
            "CHANGELOG.md",
        ],
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", f"v{args.version}"],
        check=True,
    )
    subprocess.run(
        ["git", "tag", f"v{args.version}"],
        check=True,
    )

    print("Done.")
