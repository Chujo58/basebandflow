# bbflow

A command-line tool (with an importable Python API) that automates running the CHIME/FRB baseband pipeline through the workflow system on CANFAR.

For a given event ID, `bbflow` renders the pipeline config from a template, validates it, deploys it with the `workflow` CLI, and spawns the CANFAR sessions that act as workers for the pipeline's buckets. It also reports job status and can stop runs.

> Status: design document / pre-v1. Items marked **TODO** or listed under *Open questions* still need to be verified against the real tools.

---

## Goals

- One command to go from `event_id` to a running pipeline.
- Catch mistakes locally (bad username, bad event ID, invalid YAML, expired auth) before anything is submitted.
- Work as a normal CLI (`bbflow launch 20240101`) and as a library (`from basebandflow import api`).
- Keep each run reproducible: every rendered config is saved.

## Non-goals (v1)

- Multi-event fan-out, log viewing, interactive menu (see Roadmap).
- Replacing the `workflow` or `canfar` CLIs. `bbflow` wraps them.

---

## Install

```bash
pip install -e .          # development
bbflow --help
```

Prerequisites: `canfar` Python client, the CHIME/FRB `workflow` CLI available on `PATH`, and valid CANFAR and CHIME/FRB credentials.

---

## Usage

```text
bbflow                       Show login/settings status, then the help screen
bbflow config init           First-time setup (username)
bbflow config show           Print current settings
bbflow config path           Print the settings file location
bbflow login                 Log in to CANFAR (and refresh CHIME/FRB tokens)
bbflow launch EVENT_ID       Render, validate, deploy, and spawn workers
bbflow launch EVENT_ID --dry-run
                             Render and validate only; submit nothing
bbflow status                Show jobs / sessions
bbflow stop <ID>             Stop/delete a job
```

Typical first run:

```bash
bbflow config init           # asks for username
bbflow login
bbflow launch 20240101 --dry-run   # inspect the rendered config
bbflow launch 20240101
bbflow status
```

If you run `bbflow launch ...` before setup, it offers to run `config init` instead of failing.

---

## Architecture: api vs cli

The central rule:

> **`cli` imports `api`. `api` never imports `cli`.**

| Layer | Responsibility | May use | Must not use |
|---|---|---|---|
| `api/` | All real work. Returns data, raises exceptions. | subprocess, canfar client, jinja2, pydantic, yaml, platformdirs | typer, rich, `print`, `input`, `sys.exit` |
| `cli/` | Parse arguments, prompt, print, choose exit codes. | typer, rich, `api` | Business logic |

Why: the CLI stays thin, the API can be imported in notebooks or shared scripts, and the API can be tested without a terminal. Calling a Typer command function directly from other code does not work (its parameter defaults are `typer.Option` objects), so anything reusable lives in `api/`.

### Responsibility split by feature

| Feature | `api/` | `cli/` |
|---|---|---|
| Settings | `load_settings()`, `save_settings()`, `Settings` model, paths | `config init` prompts, `config show` printing |
| CANFAR login check | `is_logged_in() -> bool` / status object | Banner, `bbflow login` (interactive, inherits the terminal) |
| CHIME/FRB token handling | check expiry, refresh | Tell the user what is happening, prompt if needed |
| Config rendering | `render_config(username, event_id) -> RenderedConfig` | `--dry-run` output |
| Validation | event ID check, YAML parse, pydantic validation | Print errors |
| Deploy | wrap `workflow configs deploy <file>` | Progress and result display |
| Spawn bucket workers | canfar Python client calls | Summary table |
| Status | `list_jobs()` returns structured data | Rich table |
| Stop | `stop_job(id)` | Confirmation prompt (`Stop X? [y/N]`), result message |
| Preflight | `check_ready() -> Status` | Decide what to print / exit code |

### Errors

Define exceptions in `api/errors.py` (for example `NotLoggedIn`, `SettingsMissing`, `InvalidEventId`, `ConfigRenderError`, `DeployFailed`). The API raises them, and the CLI catches them in one place and converts them into messages and exit codes.

---

## Repository layout

```text
baseband_pipeline_run/
├── pyproject.toml
├── README.md
├── basebandflow/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py          # public surface: re-export the stable functions
│   │   ├── errors.py
│   │   ├── models.py            # Settings, Status, RenderedConfig, JobInfo
│   │   ├── settings.py          # platformdirs paths, load/save
│   │   ├── auth.py              # CANFAR login check, CHIME/FRB token check/refresh
│   │   ├── config.py            # template rendering + validation
│   │   ├── workflow.py          # wraps the `workflow` CLI (deploy, status, ...)
│   │   └── sessions.py          # CANFAR python client: spawn/list/stop worker sessions
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py              # Typer app, no-args callback (status banner + help)
│   │   ├── ui.py                # shared Console, banner, tables
│   │   ├── config_cmd.py        # config init/show/path
│   │   ├── login.py
│   │   ├── launch.py
│   │   ├── status.py
│   │   └── stop.py
│   └── templates/
│       └── pipeline_config.yaml.j2
└── tests/
```

### Entry point

```toml
[project]
name = "basebandflow"
dependencies = ["typer", "rich", "jinja2", "pyyaml", "pydantic", "platformdirs", "canfar"]

[project.scripts]
bbflow = "basebandflow.cli.main:app"

[tool.setuptools.package-data]
basebandflow = ["templates/*.j2"]
```

After `pip install -e .`, the `bbflow` command calls the `app` object in `cli/main.py`.

---

## Settings and generated files

Using `platformdirs` (paths vary by OS):

| What | Location | Notes |
|---|---|---|
| Settings file | `user_config_dir("bbflow")/settings.yaml` | Contains only `username` |
| Rendered configs | `user_data_dir("bbflow")/runs/<event_id>/<timestamp>/config.yaml` | Kept for reproducibility and re-runs |

```yaml
# settings.yaml
username: yourname
```

Write settings atomically (write a temp file, then replace). A missing or corrupt settings file is treated as "not set up" and points the user to `bbflow config init`.

---

## The config template

`basebandflow/templates/pipeline_config.yaml.j2` is a working workflow v2 config with exactly two Jinja variables:

| Variable | Source | Used in |
|---|---|---|
| `username` | settings file | pipeline `name`, `defaults.user`, every `pipeline: baseband-{{ username }}...` bucket name |
| `event_id` | CLI argument | the `event_number` and `event_str` lines at the top (all other uses are YAML aliases) |

Rules for editing the template:

1. **Protect workflow expressions.** `${{ matrix.job_id }}` is workflow syntax, not Jinja. Wrap each occurrence so Jinja leaves it alone:
   `job_id: {% raw %}${{ matrix.job_id }}{% endraw %}`
2. **Render with `StrictUndefined`** so a missing variable is an error, not an empty string.
3. **Upload the rendered text as-is.** Parse it only to validate. Re-dumping the parsed YAML would lose the anchors (`&event-number`) and comments.
4. **Validate `event_id` before rendering.** `event_number` is unquoted (parsed as an integer) while `event_str` is quoted, so IDs are assumed numeric. Reject anything else with a clear error.
5. **Validate `username`** before rendering, because it ends up in bucket and pipeline names. Confirm the allowed characters with the workflow maintainers.
6. Check that `${{ matrix.job_id }}` survives rendering with a unit test (render, parse, assert the literal string is intact).

### Things to double-check in the template

- `unstage-data` and `finalize` both have `stage: 12`. Confirm whether that is intentional (parallel) or whether the cleanup should be stage 13.
- The three matrix steps use `range: [1, 64]` together with `job_size: '64'`. They must agree. Leave them literal for now.

---

## Launch flow

`bbflow launch EVENT_ID` does the following, stopping at the first failure:

1. **Settings**: load them. If missing, offer to run `config init`.
2. **Validate** `event_id`.
3. **Render** the template, parse the result, and validate it. Save to `runs/<event_id>/<timestamp>/config.yaml`.
4. If `--dry-run`: print the path and a summary, then stop. (Dry runs need no login.)
5. **Auth preflight**: confirm CANFAR login and valid CHIME/FRB tokens, refreshing if needed.
6. **Deploy** the config: `workflow configs deploy <rendered file>`.
7. **Spawn workers** with the CANFAR Python client for the buckets used by the pipeline.
8. **Report**: print the saved config path, deployed pipeline name, and session IDs.

### Buckets and workers (inferred from the template, to verify)

The template uses three bucket names, which suggests three kinds of workers:

| Bucket | Used by |
|---|---|
| `baseband-<username>-datatrail` | `stage-data`, `unstage-data` |
| `baseband-<username>` | most processing stages |
| `baseband-<username>-brightest` | `refinement-analysis` |

`api/sessions.py` should map these to headless CANFAR sessions (image, resources, command per bucket). The exact images, resources, and counts are **TODO**.

---

## Authentication

Two separate credentials:

1. **CANFAR**: there is no confirmed dedicated "am I logged in" command. A cheap probe is running a read-only command such as `canfar ps` and checking the exit code. Verify on your installed version by logging out and confirming it fails. Treat a timeout as "could not verify", not "logged out".
2. **CHIME/FRB API tokens**: they may need refreshing before launch.

### Checking token age (open)

It is not yet known whether the tokens expose a "time since last refresh". Options, in order of preference:

1. If the tokens are JWTs, read the `exp` claim (decoding, not verifying) and refresh when close to expiry.
2. Make a cheap authenticated call and refresh on an auth error (401/403).
3. Record a timestamp in a small state file each time `bbflow` refreshes, and refresh when it is older than N hours.

Whichever is used goes in `api/auth.py`, behind a single function such as `ensure_tokens_valid()`.

### Subprocess rules

- `bbflow login` runs the interactive login with the terminal inherited (no output capture) so prompts work.
- Non-interactive calls use `stdin=subprocess.DEVNULL`, `capture_output=True`, and a timeout, so a surprise prompt fails fast instead of hanging.
- Check `shutil.which("canfar")` and `shutil.which("workflow")` up front and give an install hint if missing.

---

## The no-argument behavior

Running `bbflow` with no subcommand prints a short status banner and then the standard help screen:

```text
✔ Logged in to CANFAR
✖ No username set (run `bbflow config init`)

Usage: bbflow [OPTIONS] COMMAND [ARGS]...
...
```

Implementation notes:

- Use a Typer callback with `invoke_without_command=True`. Return early if `ctx.invoked_subcommand` is set, otherwise print the banner, then `ctx.get_help()`, then exit.
- Do not set `no_args_is_help=True`. It exits before the callback runs, so the banner would never appear.
- Settings and login are checked independently, each with its own message and fix.
- `bbflow --help` is handled by Click before the callback, so it stays fast and offline.
- Keep the login probe's timeout short. If startup feels slow, drop the network check from the banner and leave it to `bbflow status`.

---

## Development notes

- Put logic in `api/`; keep command functions short.
- Register commands with a function per module (`register_launch(app, console)`) or use `app.add_typer`. Avoid importing one command module from another. Shared helpers belong in `api/` or `cli/ui.py`.
- Import `Console` as `from rich.console import Console`.
- Tests worth writing first:
  - template renders and the result parses as YAML;
  - `${{ matrix.job_id }}` is preserved;
  - missing variable raises an error;
  - invalid `event_id` is rejected;
  - settings round-trip and a corrupt file is treated as "not set up".
- Mock `subprocess.run` for tests of login, deploy, and status.

---

## Open questions

1. **Stopping**: should `bbflow stop` stop the CANFAR worker sessions, cancel the workflow pipeline, or both?
2. **Status**: which sources should it combine (workflow status for the pipeline, CANFAR sessions for workers)? Which `workflow` subcommands provide that?
3. **Workers**: how many sessions per bucket, which image, which resources?
4. **Tokens**: what is the cheapest reliable way to know they need refreshing (see Authentication)?
5. **`workflow configs deploy`**: confirm exact flags and its exit codes for failures, and whether it returns an identifier worth saving.
6. **Re-launching the same event**: warn, skip, or allow with `--force`?
7. **Stage 12 duplicate** in the template (see above).

## Roadmap

- v1: `config init`, `login`, `launch` (one event, `--dry-run`), `status`, `stop`.
- Next: multiple events per launch (`bbflow launch A B C`), `--events-file`, `logs`, `--set key=value` overrides, an optional interactive menu (`bbflow menu`), and a user-supplied template path.