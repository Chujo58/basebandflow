class BBFlowError(Exception):
    """Baseband Flow error."""


class SettingsMissing(BBFlowError):
    """Configuration file or required settings are missing."""


class InvalidEventId(BBFlowError):
    """Event ID must be a non-empty numeric value."""


class InvalidUsername(BBFlowError):
    """Username is invalid or not recognized."""


class TemplateError(BBFlowError):
    """Failed to load the pipeline template."""


class ConfigRenderError(BBFlowError):
    """Failed to render the pipeline configuration."""


class NotLoggedIn(BBFlowError):
    """You must log in before performing this action."""


class TokenRefreshFailed(BBFlowError):
    """Unable to refresh the authentication token."""


class ToolNotFound(BBFlowError):
    """Required command-line tool was not found on PATH"""


class DeployFailed(BBFlowError):
    """Pipeline deployment failed."""


class SessionError(BBFlowError):
    """The user session is invalid or could not be restored."""
