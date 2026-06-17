import json
from spllint.cli import main


def test_cli_reports_findings_and_exit_1(capsys):
    code = main(["status=500 | join id [search index=x]"])
    out = capsys.readouterr().out
    assert code == 1
    assert "no-index" in out and "join" in out


def test_cli_json_output(capsys):
    code = main(["index=web sourcetype=a status=500 | stats count", "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert all(f["severity"] != "high" for f in data)
    assert code == 0


def test_cli_no_format(capsys):
    main(["index=web | stats count", "--no-format"])
    out = capsys.readouterr().out
    # formatted query line would start with the raw search; with --no-format it's omitted
    assert "| stats count\n\n" not in out


def test_cli_empty_query_usage(capsys):
    code = main([""])   # joins to empty string; does not read stdin
    assert code == 2
    assert "usage" in capsys.readouterr().err.lower()
