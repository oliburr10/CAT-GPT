import pytest

from catagent import config, connections


@pytest.fixture(autouse=True)
def notes_dir(tmp_path, monkeypatch):
    """Every test gets its own empty ~/Ginger and ~/.ginger."""
    monkeypatch.setattr(config, "NOTES_DIR", tmp_path / "Ginger")
    monkeypatch.setattr(config, "HOME_DIR", tmp_path / ".ginger")
    monkeypatch.setattr(config, "NOTEPAD_FILE", tmp_path / ".ginger" / "notepad.json")
    connections.reset_cache()
    return tmp_path / "Ginger"
