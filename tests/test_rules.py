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


def test_sort_unbounded_logic():
    # No leading count -> flagged; an explicit positive count -> not flagged.
    assert "sort-unbounded" in rules("index=web | sort -_time")
    assert "sort-unbounded" not in rules("index=web | sort 1000 -_time")
    assert "sort-unbounded" in rules("index=web | sort 0 -_time")   # 0 means unlimited


def test_subsearch_flagged():
    assert "subsearch" in rules("index=web [ search index=err | fields id ] | stats count")


def test_mvexpand_flagged():
    assert "mvexpand" in rules("index=web | mvexpand recipients")


def test_leading_wildcard_emitted_once():
    findings = [f for f in lint("index=web a=*x b=*y") if f.rule == "leading-wildcard"]
    assert len(findings) == 1


def test_flags_append_and_appendcols():
    assert "append" in rules("index=web | append [search index=db]")
    assert "append" in rules("index=web | appendcols [search index=db]")


def test_flags_noop_wildcard_field_but_not_index_wildcard():
    assert "wildcard-field" in rules("index=web host=* status=500")
    # index=* must be reported as index-wildcard, not the generic no-op field rule
    r = rules("index=* error")
    assert "index-wildcard" in r and "wildcard-field" not in r
    # a leading wildcard (=*term) is its own rule, not a no-op field
    assert "wildcard-field" not in rules("index=web user=*admin")


def test_flags_dedup():
    assert "dedup" in rules("index=web | dedup host")
    assert "dedup" not in rules("index=web | stats latest(status) by host")
