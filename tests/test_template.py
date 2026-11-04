from release_notes.template import BANNER, has_review_banner, make_draft, validate_notes


NOTES = """## Release 1.1.0 (2025-03-04)
### New
- A new item.
### Improved
### Fixed
### Known issues"""


def test_validates_all_sections():
    assert validate_notes(NOTES, "1.1.0", "2025-03-04")


def test_rejects_missing_section_or_wrong_release():
    assert not validate_notes(NOTES.replace("### Fixed\n", ""), "1.1.0", "2025-03-04")
    assert not validate_notes(NOTES, "2.0.0", "2025-03-04")


def test_banner_is_added_and_detected():
    draft = make_draft(NOTES)
    assert draft.startswith(BANNER + "\n")
    assert has_review_banner(draft)
    assert not has_review_banner(NOTES)
