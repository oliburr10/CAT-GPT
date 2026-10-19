import json

from catagent import config, connections
from catagent.context import Context

VSCODE = Context(app="Code", pid=1, window_title="solver.py — homework")
OVERLEAF = Context(app="Google Chrome", pid=2, url="https://www.overleaf.com/project/abc", page_title="Thesis")
SAFARI = Context(app="Safari", pid=3, url="https://example.com", page_title="Example")


def test_first_run_shows_vscode_and_overleaf_connected():
    assert [(tool_id, on) for tool_id, _, on in connections.shown()] == [("vscode", True), ("overleaf", True)]
    assert connections.blocked(VSCODE) is None
    assert connections.describe(OVERLEAF) == OVERLEAF.describe()


def test_a_disconnected_tool_is_off_limits():
    connections.set_connected("overleaf", False)
    assert connections.blocked(OVERLEAF) == "Overleaf"
    described = connections.describe(OVERLEAF)
    assert "Thesis" not in described and "overleaf.com" not in described
    assert "isn't connected" in described
    assert connections.status("overleaf") == ("red", "Not connected")


def test_apps_not_in_the_list_work_as_before():
    connections.set_connected("vscode", False)
    connections.set_connected("overleaf", False)
    assert connections.blocked(SAFARI) is None
    assert connections.describe(SAFARI) == SAFARI.describe()
    assert connections.is_connected("word")  # not listed, so not switched off


def test_choices_are_saved():
    connections.set_connected("vscode", False)
    connections.add("google_docs")
    assert json.loads((config.HOME_DIR / "connections.json").read_text()) == {
        "vscode": False, "overleaf": True, "google_docs": True}
    connections.reset_cache()
    assert not connections.is_connected("vscode")
    assert "google_docs" not in [tool_id for tool_id, _ in connections.addable()]


def test_removing_a_tool_puts_it_back_in_the_catalog():
    connections.set_connected("overleaf", False)
    connections.remove("overleaf")
    assert connections.blocked(OVERLEAF) is None
    assert "overleaf" in [tool_id for tool_id, _ in connections.addable()]


def test_a_broken_file_falls_back_to_the_defaults():
    config.HOME_DIR.mkdir(parents=True)
    (config.HOME_DIR / "connections.json").write_text("[not, a dict")
    assert [tool_id for tool_id, _, _ in connections.shown()] == ["vscode", "overleaf"]
