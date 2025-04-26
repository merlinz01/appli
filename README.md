# 🛫 Tarmac

**Reliable deployments, repeatable workflows**

Tarmac is a library and command-line tool for running
repeatable workflows.
It uses Python scripts combined with a Github-Actions-esque workflow definition
to execute idempotent workflow runs.

This library is useful for setting up
and deploying code to production servers.
You can define your workflow, using custom scripts if needed,
then simply run `tarmac` every time you want to push out an update.

## Usage

(Recommended) Install the tool using the [uv](https://github.com/astral-sh/uv) package manager:

```bash
uv tool install tarmac
```

This will make the tool available as the `tarmac` command in the shell.

### Command options

```bash
tarmac WORKFLOW [OPTIONS]
```

| Option | Description |
|-|-|
| `-h`, `--help` | Show the command usage and exit. |
| `--version` | Show the version and exit. |
| `WORKFLOW` | The name of the workflow (or script if `--script` is given) to run. |
| `--script` | Run a script directly instead of a workflow. |
| `-i`, `--input` | Define an input for the workflow. |
| `--output-format` | Define the output format for the workflow. Default is `colored-text` |
| `-b`, `--base-path` | Define the base path for the workflow, containing workflows and scripts. Defaults to `TARMAC_BASE_PATH` environment variable or the current directory. |
| `-o`, `--output-file` | Define the output file for the workflow. Defaults to stdout. |


## License

Tarmac is available under the MIT License. See [LICENSE.txt](LICENSE.txt) for more information.
