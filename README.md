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

## License

Tarmac is available under the MIT License. See [LICENSE.txt](LICENSE.txt) for more information.
