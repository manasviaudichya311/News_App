import json
from pathlib import Path
from main import write_to_csv, get_named_entities, get_summary

def test_write_csv():
    headlines = json.load(open("tests/headlines.json", "r"))
    _ = write_to_csv(headlines, fname="tests/testfile.csv")
    csv_file = Path("tests/testfile.csv")
    assert csv_file.exists()
    # # for clearing files created during unit tests
    # csv_file.unlink()

def test_named_entities():
    text = Path("tests/text.txt").read_text(encoding="utf-8")
    ne = get_named_entities(text, "en")
    assert ne is not None
    assert type(ne) is list
    assert type(ne[0]) is tuple
    assert type(ne[0][1]) is int


def test_get_summary():
    text = Path("tests/text.txt").read_text(encoding="utf-8")
    summary = get_summary(text, "en")
    assert summary is not None
    assert len(summary) < len(text)