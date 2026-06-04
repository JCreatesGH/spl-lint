from spllint import format_spl


def test_one_command_per_line():
    out = format_spl("index=web status=500   |stats count by uri|  sort -count")
    assert out == "index=web status=500\n| stats count by uri\n| sort -count"
