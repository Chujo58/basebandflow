import shutil
import subprocess

from basebandflow.api.errors import ToolNotFound


def require_tool(name: str) -> str:  # shutil.which, raises ToolNotFound
    cmd_path = shutil.which(name)
    if not cmd_path:
        raise ToolNotFound(f"{name} is not on PATH")
    return cmd_path


def run_tool(args: list, subprocess_kwargs: dict, tool):
    check = subprocess_kwargs.pop("check", False)
    return subprocess.run([tool, *args], check=check, **subprocess_kwargs)


def canfar(*args, **subprocess_kwargs) -> subprocess.CompletedProcess:
    tool = require_tool("canfar")
    return run_tool(args, subprocess_kwargs, tool)


def frb_api(*args, **subprocess_kwargs) -> subprocess.CompletedProcess:
    tool = require_tool("frb-api")
    return run_tool(args, subprocess_kwargs, tool)


def workflow(*args, **subprocess_kwargs) -> subprocess.CompletedProcess:
    tool = require_tool("workflow")
    return run_tool(args, subprocess_kwargs, tool)
