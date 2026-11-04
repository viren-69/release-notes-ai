"""Group commit messages and request a Gemini release note draft."""

import re
from pathlib import Path

from google import genai

from release_notes.git_log import Commit


GROUPS = ("New", "Improved", "Fixed", "Other")


def group_commits(commits: list[Commit]) -> dict[str, list[Commit]]:
    """Classify commits by conventional subject prefixes."""
    groups = {name: [] for name in GROUPS}
    for commit in commits:
        subject = commit.subject.strip()
        match = re.match(r"^(feat|add|improve|update|refactor|fix|bug)(?:\([^)]*\))?(?:\s*[:\-])?\s*", subject, re.IGNORECASE)
        prefix = match.group(1).lower() if match else ""
        category = "New" if prefix in {"feat", "add"} else "Improved" if prefix in {"improve", "update", "refactor"} else "Fixed" if prefix in {"fix", "bug"} else "Other"
        groups[category].append(commit)
    return groups


def build_prompt(template: str, grouped: dict[str, list[Commit]], version: str, date: str) -> str:
    """Combine prompt instructions with grouped commit facts."""
    lines = [f"Release version: {version}", f"Release date: {date}", "Grouped commits:"]
    for group, commits in grouped.items():
        lines.append(f"\n{group}:")
        lines.extend(f"- {commit.subject}" for commit in commits)
    lines.append("\nReturn only the release notes in the required template.")
    return template.strip() + "\n\n" + "\n".join(lines)


def generate_notes(prompt: str, api_key: str) -> str:
    """Call Gemini 2.5 Flash and return its text response."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return response.text.strip()


def load_prompt(path: Path) -> str:
    """Read the release note prompt file."""
    return path.read_text(encoding="utf-8")
