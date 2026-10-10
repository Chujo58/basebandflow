from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml
from pydantic import ValidationError

from basebandflow.api.settings import RUNS_DIR
from basebandflow.models import LaunchResult


@dataclass
class RunRecord:
    path: Path  # the run folder
    event_id: str
    started: (
        datetime | None
    )  # parsed from folder names; None if they don't match the format
    result: LaunchResult | None  # None = launch_results.yaml missing or unreadable


def load_run(path: Path) -> LaunchResult | None:
    try:
        data = yaml.safe_load(
            (path / "launch_results.yaml").read_text(encoding="utf-8")
        )
        return LaunchResult(**data)
    except (OSError, yaml.YAMLError, ValidationError, TypeError):
        return None


def _parse_run_dir(path: Path) -> tuple[str, datetime | None]:
    """Folder layout: <YYYY-MM-DD>/<HHMMSS>_<event_id>"""
    time_part, _, event_id = path.name.partition("_")
    try:
        started = datetime.strptime(
            f"{path.parent.name} {time_part}", "%Y-%m-%d %H%M%S"
        ).astimezone()
    except ValueError:
        started = None
    return event_id, started


def list_runs(
    event_id: str | None = None,
    *,
    limit: int | None = None,
    include_dry_runs: bool = False,
) -> list[RunRecord]:
    """Newest first. Dry runs (status 'rendered') are hidden unless include_dry_runs."""
    if not RUNS_DIR.exists():
        return []

    records: list[RunRecord] = []
    # date folders and HHMMSS_ names both sort chronologically as plain strings
    for path in sorted((p for p in RUNS_DIR.glob("*/*") if p.is_dir()), reverse=True):
        eid, started = _parse_run_dir(path)
        if event_id and eid != event_id:
            continue
        result = load_run(path)
        if result is not None and result.status == "rendered" and not include_dry_runs:
            continue
        records.append(
            RunRecord(path=path, event_id=eid, started=started, result=result)
        )
        if limit and len(records) >= limit:
            break
    return records


def latest_run(event_id: str) -> RunRecord | None:
    runs = list_runs(event_id, limit=1)
    return runs[0] if runs else None
