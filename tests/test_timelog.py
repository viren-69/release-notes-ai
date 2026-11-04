import csv

from release_notes.timelog import append_time_log


def test_appends_header_and_run(tmp_path):
    path = tmp_path / "logs" / "time_saved.csv"
    saved = append_time_log(path, "1.1.0", 4, 45, 2.5)
    assert saved == 42.5
    with path.open() as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["version"] == "1.1.0"
    assert rows[0]["commits"] == "4"


def test_appends_without_duplicate_header(tmp_path):
    path = tmp_path / "log.csv"
    append_time_log(path, "1", 1, 45, 2)
    append_time_log(path, "2", 2, 45, 3)
    assert path.read_text().count("date,version") == 1


def test_savings_can_be_negative(tmp_path):
    assert append_time_log(tmp_path / "log.csv", "1", 0, 1, 2) == -1
