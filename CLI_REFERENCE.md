# `bbflow`

Run the baseband pipeline on CANFAR

**Usage**:

```console
$ bbflow [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `version`: Show the bbflow version
* `config`: Configuration of basebandflow (bbflow)
* `containers`: Commands to manage CANFAR headless...
* `history`: List recent launches, newest first
* `launch`: Launch the baseband pipeline (containers +...
* `login`: Log in to your CANFAR account
* `tokens`: Manage CHIME/FRB API tokens
* `workflow`: Workflow related commands

## `bbflow version`

Show the bbflow version

**Usage**:

```console
$ bbflow version [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `bbflow config`

Configuration of basebandflow (bbflow)

**Usage**:

```console
$ bbflow config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `init`: Initialize the configuration
* `set`: Change a configuration parameter
* `show`: Show the current configuration
* `path`: Show where the configuration is saved

### `bbflow config init`

Initialize the configuration

**Usage**:

```console
$ bbflow config init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `bbflow config set`

Change a configuration parameter

**Usage**:

```console
$ bbflow config set [OPTIONS] {parameter}
```

**Arguments**:

* `parameter`: Choose between username, baseband_path, refresh_timer to update the configuration  [required]

**Options**:

* `--help`: Show this message and exit.

### `bbflow config show`

Show the current configuration

**Usage**:

```console
$ bbflow config show [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `bbflow config path`

Show where the configuration is saved

**Usage**:

```console
$ bbflow config path [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `bbflow containers`

Commands to manage CANFAR headless containers/sessions

**Usage**:

```console
$ bbflow containers [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a CANFAR container
* `list`: List CANFAR headless containers
* `delete`: Delete one CANFAR container
* `prune`: Prune multiple CANFAR containers

### `bbflow containers create`

Create a CANFAR container

**Usage**:

```console
$ bbflow containers create [OPTIONS] [session_type]
```

**Arguments**:

* `session_type`: Type of session: datatrail, analysis, refinement, all

**Options**:

* `--help`: Show this message and exit.

### `bbflow containers list`

List CANFAR headless containers

**Usage**:

```console
$ bbflow containers list [OPTIONS]
```

**Options**:

* `-f, --filter <str>`: Type of session: datatrail, analysis, refinement, all
* `--help`: Show this message and exit.

### `bbflow containers delete`

Delete one CANFAR container

**Usage**:

```console
$ bbflow containers delete [OPTIONS] {session_id}
```

**Arguments**:

* `session_id`: CANFAR session ID  [required]

**Options**:

* `--help`: Show this message and exit.

### `bbflow containers prune`

Prune multiple CANFAR containers

**Usage**:

```console
$ bbflow containers prune [OPTIONS] [session_type]
```

**Arguments**:

* `session_type`: Type of session: datatrail, analysis, refinement, all

**Options**:

* `--help`: Show this message and exit.

## `bbflow history`

List recent launches, newest first

**Usage**:

```console
$ bbflow history [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-e, --event <str>`: Only this event ID
* `-n, --limit <int range>`: How many runs to show  [default: 10; x&gt;=1]
* `-a, --all`: Include dry runs
* `--help`: Show this message and exit.

**Commands**:

* `show`: Show most recent launch for an event

### `bbflow history show`

Show most recent launch for an event

**Usage**:

```console
$ bbflow history show [OPTIONS] {event_id}
```

**Arguments**:

* `event_id`: Event ID used for the baseband pipeline  [required]

**Options**:

* `--help`: Show this message and exit.

## `bbflow launch`

Launch the baseband pipeline (containers + deployment)

**Usage**:

```console
$ bbflow launch [OPTIONS] {event_id}
```

**Arguments**:

* `event_id`: [required]

**Options**:

* `--dry-run`
* `--help`: Show this message and exit.

## `bbflow login`

Log in to your CANFAR account

**Usage**:

```console
$ bbflow login [OPTIONS]
```

**Options**:

* `--check`: Report status only
* `--help`: Show this message and exit.

## `bbflow tokens`

Manage CHIME/FRB API tokens

**Usage**:

```console
$ bbflow tokens [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `path`: Show where CHIME/FRB tokens are saved
* `status`: Report the status and lifetime of JWT tokens
* `refresh`: Refresh CHIME/FRB tokens (requires...

### `bbflow tokens path`

Show where CHIME/FRB tokens are saved

**Usage**:

```console
$ bbflow tokens path [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `bbflow tokens status`

Report the status and lifetime of JWT tokens

**Usage**:

```console
$ bbflow tokens status [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `bbflow tokens refresh`

Refresh CHIME/FRB tokens (requires password input)

**Usage**:

```console
$ bbflow tokens refresh [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `bbflow workflow`

Workflow related commands

**Usage**:

```console
$ bbflow workflow [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `abort`: Abort the Workflow deployment
* `status`: Loads the status of the Workflow deployment
* `open`: Opens the Workflow page for the configuration

### `bbflow workflow abort`

Abort the Workflow deployment

**Usage**:

```console
$ bbflow workflow abort [OPTIONS] [config_id]
```

**Arguments**:

* `config_id`: Configuration ID from Workflow

**Options**:

* `--help`: Show this message and exit.

### `bbflow workflow status`

Loads the status of the Workflow deployment

**Usage**:

```console
$ bbflow workflow status [OPTIONS] [event_id]
```

**Arguments**:

* `event_id`: Event ID used for the baseband pipeline

**Options**:

* `--oneline / --no-oneline`: Oneline status  [default: no-oneline]
* `--help`: Show this message and exit.

### `bbflow workflow open`

Opens the Workflow page for the configuration

**Usage**:

```console
$ bbflow workflow open [OPTIONS] [event_id]
```

**Arguments**:

* `event_id`: Event ID used for the baseband pipeline

**Options**:

* `--help`: Show this message and exit.
