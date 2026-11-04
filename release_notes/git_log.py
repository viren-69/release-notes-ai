"""Read and parse commits from a Git repository."""

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Commit:
    """The commit fields used to prepare release notes."""

    hash: str
    author: str
    date: str
    subject: str


def parse_commits(output: str) -> list[Commit]:
    """Parse pipe-delimited output from ``git log``."""
    commits: list[Commit] = []
    for line in output.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            commit_hash, author, date, subject = parts
            commits.append(Commit(commit_hash, author, date, subject))
    return commits


def read_commits(repo_path: Path, from_ref: str | None, to_ref: str) -> list[Commit]:
    """Read a ref range, or the latest 20 commits when no start ref is given."""
    if from_ref:
        revision = f"{from_ref}..{to_ref}"
        args = ["git", "log", revision]
    else:
        args = ["git", "log", "-20", to_ref]
    args.extend(["--pretty=format:%h|%an|%ad|%s", "--date=short"])
    try:
        result = subprocess.run(args, cwd=repo_path, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or "git log failed"
        raise RuntimeError(detail) from exc
    except FileNotFoundError as exc:
        raise RuntimeError("Git is not installed or the repository path is invalid.") from exc
    return parse_commits(result.stdout)
