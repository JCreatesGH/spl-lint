from spllint import lint


def rules(spl):
    return {f.rule for f in lint(spl)}


def test_flags_missing_index_and_wildcard():
    assert "no-index" in rules("status=500 | stats count")
    assert "index-wildcard" in rules("index=* error | stats count")


def test_flags_leading_wildcard():
    assert "leading-wildcard" in rules("index=web user=*admin")


def test_flags_join_and_transaction():
    assert "join" in rules("index=web | join id [ search index=db ]")
    assert "transaction" in rules("index=web | transaction session")


def test_high_severity_sorted_first():
    findings = lint("status=500 | join id [search index=x]")
    assert findings[0].severity == "high"


def test_clean_query_minimal_findings():
    findings = lint("index=web sourcetype=access status=500 | stats count by uri | fields uri count")
    assert all(f.severity != "high" for f in findings)
