"""Connections: the apps and sites Ginger may see and work in, switched on and off from its panel.

A connected tool works as usual. A disconnected one is off limits: Ginger isn't told what you
have open in it, won't take a screenshot while it's in front, and (for VS Code) opens files in
their default app instead. Apps that aren't in the list behave as they always have.

The choice is saved in ~/.ginger/connections.json.
"""

import json
import shutil
import threading
from dataclasses import dataclass, field
from pathlib import Path

from . import config, context


@dataclass(frozen=True)
class Tool:
    name: str
    apps: frozenset[str] = field(default_factory=frozenset)   # macOS app names
    hosts: tuple[str, ...] = ()                                # websites, matched against the tab's URL
    does: str = ""                                             # what being connected lets Ginger do


CATALOG: dict[str, Tool] = {
    "vscode": Tool("VS Code", frozenset({"Code", "Visual Studio Code"}),
                   does="Sees which file you're in and opens files at the right line."),
    "overleaf": Tool("Overleaf", hosts=("overleaf.com",),
                     does="Reads your Overleaf tab and tells you what to change and where."),
    "google_docs": Tool("Google Docs", hosts=("docs.google.com",),
                        does="Reads your Google Doc and tells you what to change and where."),
    "word": Tool("Word", frozenset({"Microsoft Word"}), does="Finds your open Word document and reads it."),
    "jupyter": Tool("Jupyter", hosts=("localhost:8888", "127.0.0.1:8888", "colab.research.google.com"),
                    does="Reads the notebook open in your browser."),
    "terminal": Tool("Terminal", frozenset({"Terminal", "iTerm2", "Warp", "Ghostty"}),
                     does="Sees your terminal window, so it can read errors."),
    "xcode": Tool("Xcode", frozenset({"Xcode"}), does="Sees which project you're in."),
    "pycharm": Tool("PyCharm", frozenset({"PyCharm", "PyCharm CE"}), does="Sees which file you're in."),
    "notion": Tool("Notion", frozenset({"Notion"}), hosts=("notion.so",), does="Reads the page you have open."),
}
DEFAULT = {"vscode": True, "overleaf": True}  # shown in the panel on first run, both connected

_lock = threading.Lock()
_state: dict[str, bool] | None = None  # tool id -> connected, in the order shown


def _file() -> Path:
    return config.HOME_DIR / "connections.json"


def _load() -> dict[str, bool]:
    global _state
    if _state is None:
        try:
            saved = json.loads(_file().read_text())
            _state = {k: bool(v) for k, v in saved.items() if k in CATALOG}
        except (OSError, ValueError, AttributeError):
            _state = dict(DEFAULT)
    return _state


def _save() -> None:
    config.HOME_DIR.mkdir(parents=True, exist_ok=True)
    _file().write_text(json.dumps(_state))


def reset_cache() -> None:
    """Forget what's loaded (the tests point HOME_DIR somewhere new)."""
    global _state
    with _lock:
        _state = None


def shown() -> list[tuple[str, Tool, bool]]:
    """The tools in the panel: (id, tool, connected)."""
    with _lock:
        return [(tool_id, CATALOG[tool_id], on) for tool_id, on in _load().items()]


def addable() -> list[tuple[str, Tool]]:
    """Tools from the catalog that aren't in the panel yet."""
    with _lock:
        state = _load()
        return [(tool_id, tool) for tool_id, tool in CATALOG.items() if tool_id not in state]


def set_connected(tool_id: str, on: bool) -> None:
    if tool_id not in CATALOG:
        raise KeyError(tool_id)
    with _lock:
        _load()[tool_id] = on
        _save()


def add(tool_id: str) -> None:
    """Put a tool from the catalog in the panel, connected."""
    set_connected(tool_id, True)


def remove(tool_id: str) -> None:
    """Take a tool out of the panel. It's then treated like any other app again."""
    with _lock:
        _load().pop(tool_id, None)
        _save()


def is_connected(tool_id: str) -> bool:
    """A tool not in the panel counts as connected: only a switched-off tool is off limits."""
    with _lock:
        return _load().get(tool_id, True)


def tool_for(ctx: context.Context | None) -> str | None:
    """Which listed tool, if any, this app or browser tab belongs to."""
    if ctx is None:
        return None
    with _lock:
        state = _load()
    for tool_id in state:
        tool = CATALOG[tool_id]
        if ctx.app in tool.apps or (ctx.url and any(host in ctx.url for host in tool.hosts)):
            return tool_id
    return None


def blocked(ctx: context.Context | None) -> str | None:
    """The name of the disconnected tool this context belongs to, or None if Ginger may look."""
    tool_id = tool_for(ctx)
    if tool_id is not None and not is_connected(tool_id):
        return CATALOG[tool_id].name
    return None


def describe(ctx: context.Context | None) -> str | None:
    """What Ginger is told about where you are, respecting connections. None if nothing is known."""
    if ctx is None:
        return None
    name = blocked(ctx)
    if name:
        return (f"You were in {name}, which isn't connected, so you can't see or work in it. If asked "
                f"about it, say {name} needs connecting first, in your panel (the arrow under you).")
    return ctx.describe()


def status(tool_id: str) -> tuple[str, str]:
    """(colour, words) for the panel: green connected, amber connected but needs setting up, red off."""
    if not is_connected(tool_id):
        return "red", "Not connected"
    if tool_id == "vscode" and context.IS_MAC and not shutil.which("code"):
        return "amber", "Connected · install the code command to open files at a line"
    return "green", "Connected"
