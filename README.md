# release-notes-ai

## What it does

`release-notes-ai` reads a Git commit range, groups subjects by likely change type, and asks Gemini 2.5 Flash for a release note draft. It puts a human review banner on every draft and refuses the publish check while that banner remains.

## Why a human review gate matters

An LLM can misread a commit or turn an implementation detail into an unsupported product claim. Its context can also be stale or incomplete. Verify each item against the product, current terminology, and approved release scope before sharing notes.

## Install

Use Python 3.11. Install dependencies with `python -m pip install -r requirements.txt`. Copy `.env.example` to `.env` and add an API key obtained through your approved process. The tool reads the key from `.env` only and never prints it.

Use only company-approved AI tools. Never send confidential or customer data to an AI service.

## Quick start

```sh
python -m release_notes.cli --from v1.0.0 --to HEAD --version 1.1.0 --repo-path . --manual-minutes 45
```

Omit `--from` to read the latest 20 commits. Review `drafts/release-notes-1.1.0.md`, verify every item, then remove its banner. Run `python -m release_notes.cli --version 1.1.0 --publish` to check and display the reviewed draft. This command does not publish to an external service.

## Workflow diagram

```text
Git refs -> grouped commit subjects -> Gemini draft -> human review -> publish check
                                      |                            |
                                      +-> time_saved.csv           +-> refuses while banner remains
```

## Time saved log

| Column | Meaning |
|---|---|
| date | Date of the generation run |
| version | Release version supplied to the CLI |
| commits | Number of commits read |
| manual_minutes | Estimated manual writing time from `--manual-minutes` |
| tool_minutes | Time spent waiting for generation |
| minutes_saved | Manual estimate minus tool time |

## Limitations

Commit subjects may omit user impact, so the draft can be incomplete. Prefix grouping is a heuristic, and unclassified commits go into `Other`. Gemini may still produce inaccurate claims; the review gate does not replace editorial judgment. The tool records generation time, not the time spent reviewing or editing. Git history and a valid API key in the repository path's `.env` file are required.
