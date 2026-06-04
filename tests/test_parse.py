from spllint import split_pipeline


def test_splits_on_top_level_pipes_only():
    stages = split_pipeline('index=web status=500 | stats count by uri | sort -count')
    assert [s.command for s in stages] == ["search", "stats", "sort"]
    assert stages[0].is_search


def test_pipe_inside_quotes_and_subsearch_ignored():
    stages = split_pipeline('index=web msg="a | b" | eval x=1')
    assert len(stages) == 2
    sub = split_pipeline('index=web [ search index=err | fields id ] | stats count')
    assert [s.command for s in sub] == ["search", "stats"]
