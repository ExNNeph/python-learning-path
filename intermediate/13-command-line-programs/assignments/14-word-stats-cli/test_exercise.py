"""Tests for assignment 14. Run: pytest intermediate/13-command-line-programs/assignments/14-word-stats-cli -v"""

import argparse
import io
import json
from collections import Counter
from pathlib import Path

import pytest

SAMPLE = Path(__file__).with_name("sample.txt")


def test_positive_int(ex):
    assert ex.positive_int("3") == 3
    for bad in ["0", "-2"]:
        with pytest.raises(argparse.ArgumentTypeError):
            ex.positive_int(bad)
    with pytest.raises(ValueError):
        ex.positive_int("many")


def test_parser_defaults(ex):
    args = ex.build_parser().parse_args([])
    assert (args.files, args.top, args.min_length, args.case_sensitive, args.format) == ([], 10, 1, False, "text")


def test_parser_all_options(ex):
    args = ex.build_parser().parse_args(["a.txt", "-", "-t", "3", "-m", "4", "--case-sensitive", "-f", "json"])
    assert (args.files, args.top, args.min_length, args.case_sensitive, args.format) == (["a.txt", "-"], 3, 4, True, "json")
    args = ex.build_parser().parse_args(["--top", "5", "--min-length", "2", "--format", "text"])
    assert (args.top, args.min_length, args.format) == (5, 2, "text")


def test_parser_prog_name(ex):
    assert ex.build_parser().prog == "wordstats"


@pytest.mark.parametrize("argv", [["--top", "0"], ["-t", "x"], ["-m", "-1"], ["--format", "xml"], ["--unknown"]])
def test_usage_errors_exit_with_2(ex, argv, capsys):
    with pytest.raises(SystemExit) as exit_info:
        ex.main(argv)
    assert exit_info.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "wordstats: error:" in captured.err


def test_help_and_version(ex, capsys):
    with pytest.raises(SystemExit) as exit_info:
        ex.main(["--help"])
    assert exit_info.value.code == 0
    assert "usage: wordstats" in capsys.readouterr().out
    with pytest.raises(SystemExit) as exit_info:
        ex.main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == "wordstats 1.0"


def test_count_words(ex):
    counts = ex.count_words(["Python's motto: Python, python!", "be_brave 42"])
    assert counts == Counter({"python": 2, "python's": 1, "motto": 1, "be_brave": 1, "42": 1})


def test_count_words_options(ex):
    lines = ["Python python PYTHON is it"]
    assert ex.count_words(lines, case_sensitive=True) == Counter({"Python": 1, "python": 1, "PYTHON": 1, "is": 1, "it": 1})
    assert ex.count_words(lines, min_length=3) == Counter({"python": 3})


def test_count_words_accepts_any_iterable(ex):
    assert ex.count_words(iter(["a a", "b"])) == Counter({"a": 2, "b": 1})


def test_format_text(ex):
    counts = Counter({"python": 12, "is": 3, "fun": 3})
    assert ex.format_text(counts, 2) == "   12  python\n    3  is"
    assert ex.format_text(Counter(), 5) == ""


def test_format_json(ex):
    counts = Counter({"python": 12, "is": 3, "fun": 1})
    text = ex.format_json(counts, 2)
    assert json.loads(text) == {"total": 16, "unique": 3, "top": [["python", 12], ["is", 3]]}
    assert '\n  "total"' in text, "use indent=2"


def test_main_with_file(ex, capsys):
    assert ex.main(["--top", "3", "--min-length", "4", str(SAMPLE)]) == 0
    assert capsys.readouterr().out == "    5  python\n    2  code\n    2  readable\n"


def test_main_json(ex, capsys):
    assert ex.main([str(SAMPLE), "--format", "json", "--top", "2"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["top"] == [["python", 5], ["is", 4]]
    assert report["total"] == 40
    assert report["unique"] == 30


def test_main_several_files(ex, tmp_path, capsys):
    first, second = tmp_path / "a.txt", tmp_path / "b.txt"
    first.write_text("tea tea\n", encoding="utf-8")
    second.write_text("tea coffee\n", encoding="utf-8")
    assert ex.main([str(first), str(second)]) == 0
    assert capsys.readouterr().out == "    3  tea\n    1  coffee\n"


def test_main_reads_stdin(ex, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("b a b\nB\n"))
    assert ex.main([]) == 0
    assert capsys.readouterr().out == "    3  b\n    1  a\n"


def test_main_dash_reads_stdin(ex, monkeypatch, capsys, tmp_path):
    path = tmp_path / "f.txt"
    path.write_text("file\n", encoding="utf-8")
    monkeypatch.setattr("sys.stdin", io.StringIO("stdin stdin\n"))
    assert ex.main(["-", str(path)]) == 0
    assert capsys.readouterr().out == "    2  stdin\n    1  file\n"


def test_main_empty_input(ex, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert ex.main([]) == 0
    assert capsys.readouterr().out == ""


def test_main_missing_file(ex, tmp_path, capsys):
    missing = tmp_path / "missing.txt"
    assert ex.main([str(SAMPLE), str(missing)]) == 1
    captured = capsys.readouterr()
    assert captured.out == "", "no half-finished report on stdout"
    assert captured.err.startswith(f"wordstats: error: cannot read {missing}: ")
