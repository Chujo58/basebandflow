# This contains all the help menu text for each command. Some of the arguments are also listed here.

EID = "Event ID used for the baseband pipeline"
CONFIG_ID = "Configuration ID from Workflow"
PIPELINE_ID = "Pipeline ID from Workflow"

# Config
CONFIG_TYPER = "Configuration of basebandflow (bbflow)"
CONFIG_INIT = "Initialize the configuration"
CONFIG_SET = "Change a configuration parameter"
CONFIG_SHOW = "Show the current configuration"
CONFIG_PATH = "Show where the configuration is saved"

# Containers
CONTAINERS_TYPER = "Commands to manage CANFAR headless containers/sessions"
CONTAINER_CREATE = "Create a CANFAR container"
CONTAINER_LIST = "List CANFAR headless containers"
CONTAINER_DELETE = "Delete one CANFAR container"
CONTAINER_PRUNE = "Prune multiple CANFAR containers"

# History
HISTORY_TYPER = "History of past launches stored locally"
HISTORY_HISTORY = "List recent launches, newest first"
HISTORY_SHOW = "Show most recent launch for an event"

# Launch
LAUNCH_LAUNCH = "Launch the baseband pipeline (containers + deployment)"

# Login
LOGIN_TYPER = "CANFAR login helper"
LOGIN_LOGIN = "Log in to your CANFAR account"
LOGIN_CHECK = "Report status only"

# Tokens
TOKENS_TYPER = "Manage CHIME/FRB API tokens"
TOKEN_PATH = "Show where CHIME/FRB tokens are saved"
TOKEN_REFRESH = "Refresh CHIME/FRB tokens (requires password input)"
TOKEN_STATUS = "Report the status and lifetime of JWT tokens"

# Workflow
WORKFLOW_ABORT = "Abort the Workflow deployment"
WORKFLOW_OPEN = "Opens the Workflow page for the configuration"
WORKFLOW_STATUS = "Loads the status of the Workflow deployment"
WORKFLOW_TYPER = "Commands to access Workflow"

# Version
VERSION = "Show the bbflow version"
