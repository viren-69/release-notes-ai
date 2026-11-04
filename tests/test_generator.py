from unittest.mock import Mock

from release_notes.generator import generate_notes, group_commits
from release_notes.git_log import Commit


def test_groups_commit_prefixes():
    commits = [Commit("1", "A", "d", "feat: add export"), Commit("2", "A", "d", "update docs"),
               Commit("3", "A", "d", "bug: handle timeout"), Commit("4", "A", "d", "chore: tidy")]
    groups = group_commits(commits)
    assert [c.hash for c in groups["New"]] == ["1"]
    assert [c.hash for c in groups["Improved"]] == ["2"]
    assert [c.hash for c in groups["Fixed"]] == ["3"]
    assert [c.hash for c in groups["Other"]] == ["4"]


def test_grouping_is_case_insensitive_and_supports_scope():
    commit = Commit("1", "A", "d", "Fix(api): timeout")
    assert group_commits([commit])["Fixed"] == [commit]


def test_generate_calls_gemini(monkeypatch):
    from release_notes import generator

    response = Mock(text="release notes")
    client = Mock()
    client.models.generate_content.return_value = response
    monkeypatch.setattr(generator.genai, "Client", lambda api_key: client)
    assert generate_notes("prompt", "secret") == "release notes"
    client.models.generate_content.assert_called_once_with(model="gemini-2.5-flash", contents="prompt")
