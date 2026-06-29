from pathlib import Path

from healthos_api.services.fitnesssyncer import parse_fitnesssyncer_csv


SAMPLE = Path(__file__).resolve().parents[3] / "samples" / "fitnesssyncer_mock.csv"


def test_parse_fitnesssyncer_mock_csv() -> None:
    rows, errors = parse_fitnesssyncer_csv(SAMPLE.read_text(encoding="utf-8-sig"))

    assert errors == []
    assert len(rows) == 6
    assert rows[0].record_type == "sleep"
    assert rows[0].value == 465
    assert rows[3].raw["sport_type"] == "running"


def test_parse_fitnesssyncer_reports_missing_required_columns() -> None:
    rows, errors = parse_fitnesssyncer_csv("type,value\nsleep,465\n")

    assert rows == []
    assert "Missing required columns" in errors[0]["error"]
