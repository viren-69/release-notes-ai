"""Command-line interface for release-notes-ai."""

import argparse
from datetime import date
from pathlib import Path
import re
import sys
import time

from dotenv import dotenv_values

from release_notes.generator import build_prompt, generate_notes, group_commits, load_prompt
from release_notes.git_log import read_commits
from release_notes.template import has_review_banner, make_draft, validate_notes
from release_notes.timelog import append_time_log


PROJECT_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    """Run generation or check a draft for human approval."""
    parser = argparse.ArgumentParser(description="Draft release notes from Git history.")
    parser.add_argument("--from", dest="from_ref", help="Starting Git ref; defaults to the latest 20 commits")
    parser.add_argument("--to", default="HEAD", help="Ending Git ref (default: HEAD)")
    parser.add_argument("--version", required=True, help="Release version, such as 1.1.0")
    parser.add_argument("--repo-path", type=Path, default=Path("."))
    parser.add_argument("--manual-minutes", type=float, default=45)
    parser.add_argument("--publish", action="store_true", help="Check and display the reviewed draft for this version")
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        parser.error("--version must use X.Y.Z format, for example 1.1.0")

    drafts_dir = PROJECT_DIR / "drafts"
    draft_path = drafts_dir / f"release-notes-{args.version}.md"
    if args.publish:
        if not draft_path.is_file():
            print(f"Draft not found: {draft_path}", file=sys.stderr)
            return 1
        content = draft_path.read_text(encoding="utf-8")
        if has_review_banner(content):
            print("Publish refused: remove the human review banner after completing the checklist.", file=sys.stderr)
            return 1
        print(content, end="")
        return 0

    repo_path = args.repo_path.resolve()
    try:
        commits = read_commits(repo_path, args.from_ref, args.to)
    except RuntimeError as exc:
        print(f"Could not read Git history: {exc}", file=sys.stderr)
        return 1
    if not commits:
        print("No commits found in the requested range.", file=sys.stderr)
        return 1

    # dotenv_values reads only this file and never falls back to environment variables.
    env_file = repo_path / ".env"
    api_key = dotenv_values(env_file).get("GEMINI_API_KEY") if env_file.is_file() else None
    if not api_key:
        print(f"GEMINI_API_KEY is missing from {env_file}.", file=sys.stderr)
        return 1

    today = date.today().isoformat()
    prompt_text = load_prompt(PROJECT_DIR / "prompts" / "release_notes_prompt.md")
    prompt = build_prompt(prompt_text, group_commits(commits), args.version, today)
    started = time.monotonic()
    notes = ""
    try:
        for attempt in range(2):
            notes = generate_notes(prompt, api_key)
            if validate_notes(notes, args.version, today):
                break
            if attempt == 0:
                prompt += "\n\nThe previous response failed validation. Return all four required headings exactly, with the requested version and date."
        else:
            print("Gemini output failed template validation after one retry.", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"Gemini generation failed ({type(exc).__name__}).", file=sys.stderr)
        return 1
    tool_minutes = (time.monotonic() - started) / 60
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(make_draft(notes), encoding="utf-8")
    saved = append_time_log(PROJECT_DIR / "logs" / "time_saved.csv", args.version,
                            len(commits), args.manual_minutes, tool_minutes)
    print(f"Draft written to {draft_path}")
    print(f"Commits: {len(commits)} | Manual estimate: {args.manual_minutes:g} min | Tool: {tool_minutes:.2f} min | Estimated time saved: {saved:.2f} min")
    print("Review every item before publishing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
