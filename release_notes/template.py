"""Release note formatting and validation."""

import re


SECTIONS = ("New", "Improved", "Fixed", "Known issues")
BANNER = "> ⚠️ NEEDS HUMAN REVIEW: AI-generated draft. Verify every item against the product before publishing. Remove this banner after review."
CHECKLIST = """## Review checklist

- [ ] Each item verified against the product
- [ ] Terminology matches the style guide
- [ ] No confidential data
- [ ] Senior writer approved"""


def validate_notes(text: str, version: str, date: str) -> bool:
    """Check that the required release heading and all sections exist."""
    if not re.search(rf"^## Release {re.escape(version)} \({re.escape(date)}\)$", text, re.MULTILINE):
        return False
    return all(re.search(rf"^### {re.escape(section)}$", text, re.MULTILINE) for section in SECTIONS)


def make_draft(notes: str) -> str:
    """Add the required review banner and checklist around generated notes."""
    return f"{BANNER}\n\n{notes.strip()}\n\n{CHECKLIST}\n"


def has_review_banner(text: str) -> bool:
    """Return whether a draft still carries the mandatory review banner."""
    return BANNER in text
