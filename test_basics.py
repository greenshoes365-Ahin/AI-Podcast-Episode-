import pytest

from podcast.llm import parse_json
from podcast.scriptwriter import validate_script
from podcast.show_notes import chapters, fmt_time


def test_parse_json_fenced():
    assert parse_json('Sure!\n```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_json_with_prose():
    assert parse_json('Here: {"a": 2} done') == {"a": 2}


def test_validate_rejects_unknown_speaker():
    with pytest.raises(ValueError):
        validate_script({"segments": [{"speaker": "Bob", "text": "hi"}]}, ["Alex"])


def test_fmt_time():
    assert fmt_time(75) == "01:15"
    assert fmt_time(3725) == "1:02:05"


def test_chapters_first_occurrence():
    script = {"segments": [{"section": "Intro"}, {"section": "Intro"}, {"section": "Deep dive"}]}
    assert chapters(script, [0, 5, 10]) == [(0, "Intro"), (10, "Deep dive")]
