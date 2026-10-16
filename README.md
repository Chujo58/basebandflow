# 🌌 basebandflow

A command-line interface to run the CHIME/FRB baseband pipeline on **CANFAR**.

## 📦 Installation

This project uses `pyproject.toml` to manage dependencies and expose the command-line executable.

```bash
# Clone the repository
git clone https://github.com
cd basebandflow

# Install the package locally in editable mode (remove -e for normal install)
pip install -e .
```

## 🛠️ Usage

Once installed, you can launch the CLI using the executable defined in your `pyproject.toml` (typically `bbflow` or `basebandflow`—replace `bbflow` below with your actual entry point name):

```bash
bbflow [OPTIONS] COMMAND [ARGS]...
```

If you run the base command without any subcommands, it will automatically check your CANFAR login status and display an interactive banner menu:
```bash
bbflow
```

### Debug Mode
If you encounter errors and need a full Python stack trace instead of a clean error message, set the debug environment variable:
```bash
export BBFLOW_DEBUG=1
bbflow <command>
```

---

## 📖 CLI Reference

The interface is broken down into several modular subcommands:

### Global Options
* `-h`, `--help`: Show the help message and exit.

### Command Groups

| Command Group | Description |
| :--- | :--- |
| **`config`** | Manage local CLI configurations and settings. |
| **`containers`** | List, pull, or manage CANFAR pipeline containers. |
| **`history`** | View historical logs and past pipeline runs. |
| **`launch`** | Spin up and initiate a new baseband pipeline job. |
| **`login`** | Authenticate with CANFAR services. |
| **`tokens`** | Manage CHIME/FRB and CANFAR authentication tokens. |
| **`workflow`** | Define, inspect, and track active workflow states. |

> 💡 *To view detailed arguments and options for any group, run `bbflow <group> --help`.*

> ⚠️ **More information about the commands in [CLI Reference](CLI_REFERENCE.md)**

---

<!-- ## 🧪 Development

To run the test suite or contribute to `basebandflow`:

```bash
pip install -e ".[test]"
pytest
``` -->