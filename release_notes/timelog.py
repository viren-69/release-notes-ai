"""Track time spent generating release notes."""

import csv
from datetime import date
from pathlib import Path


FIELDS = ("date", "version", "commits", "manual_minutes", "tool_minutes", "minutes_saved")


def append_time_log(path: Path, version: str, commits: int, manual_minutes: float, tool_minutes: float) -> float:
    """Append one run and return estimated minutes saved."""
    path.parent.mkdir(parents=True, exist_ok=True)
    saved = round(manual_minutes - tool_minutes, 2)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow({"date": date.today().isoformat(), "version": version, "commits": commits,
                         "manual_minutes": manual_minutes, "tool_minutes": round(tool_minutes, 2),
                         "minutes_saved": saved})
    return saved
