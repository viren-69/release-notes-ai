from release_notes.git_log import Commit, parse_commits


def test_parses_delimited_commit():
    assert parse_commits("abc123|A Writer|2025-01-02|feat: add reply button") == [
        Commit("abc123", "A Writer", "2025-01-02", "feat: add reply button")]


def test_subject_can_contain_pipe():
    assert parse_commits("abc|Name|2025-01-02|fix: left | right")[0].subject == "fix: left | right"


def test_ignores_malformed_line():
    assert parse_commits("bad line") == []
