"""The Notepad's clipboard: projects, folders and clipped notes, kept as real files.

Everything lives under config.NOTES_DIR (~/Ginger by default), so you can also browse it in
Finder:

    ~/Ginger/Math 1/Week 1/Questions/Trace(AB) = Trace(BA).json

Each top-level folder is a project. Inside a project, folders are plain directories and every
clip is one JSON file: {"id", "kind", "title", "created", and "notes" or "text"}. Paths passed
in and out of this module are relative to the project, like "Week 1/Questions".
"""

import json
import re
import shutil
import time
import uuid
from pathlib import Path

from . import config

KINDS = ("solution", "note", "idea")
CLIP_SUFFIX = ".json"
DEFAULT_PROJECT = "Study"


class ClipboardError(ValueError):
    """Something the user can fix, like a name that's already taken. The message says what."""


def safe_name(name: str) -> str:
    """Turn a title into a file or folder name that works in Finder."""
    name = re.sub(r"[/\\:]", "-", name)
    name = re.sub(r"\s+", " ", name).strip().lstrip(".")
    if not name:
        raise ClipboardError("Give it a name first.")
    return name[:80].rstrip()


def _natural(name: str) -> list:
    """Sort key that puts "Week 2" before "Week 10"."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", name)]


def projects() -> list[str]:
    root = config.NOTES_DIR
    if not root.is_dir():
        return []
    return sorted((p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")), key=_natural)


def make_project(name: str) -> str:
    name = safe_name(name)
    path = config.NOTES_DIR / name
    if path.exists():
        raise ClipboardError(f"There's already a project called {name}.")
    path.mkdir(parents=True)
    return name


def current_project() -> str:
    """The project you're working in, shared by the cat's panel and the Notepad."""
    try:
        name = (config.HOME_DIR / "project.txt").read_text(encoding="utf-8").strip()
    except OSError:
        name = ""
    return ensure_project(name)


def set_current_project(name: str) -> None:
    if name not in projects():
        raise ClipboardError(f"There's no project called {name}.")
    config.HOME_DIR.mkdir(parents=True, exist_ok=True)
    (config.HOME_DIR / "project.txt").write_text(name, encoding="utf-8")


def ensure_project(name: str = "") -> str:
    """The project to show: the one asked for if it exists, else the first, else a new one."""
    existing = projects()
    if name in existing:
        return name
    if existing:
        return existing[0]
    (config.NOTES_DIR / DEFAULT_PROJECT).mkdir(parents=True, exist_ok=True)
    return DEFAULT_PROJECT


def _project_dir(project: str) -> Path:
    path = config.NOTES_DIR / safe_name(project)
    if not path.is_dir():
        raise ClipboardError(f"There's no project called {project}.")
    return path


def _resolve(project: str, rel: str) -> Path:
    """A path inside the project, refusing anything that would step outside it."""
    base = _project_dir(project).resolve()
    path = (base / rel).resolve()
    if path != base and base not in path.parents:
        raise ClipboardError("That path is outside the project.")
    return path


def _rel(project: str, path: Path) -> str:
    return path.resolve().relative_to(_project_dir(project).resolve()).as_posix()


def tree(project: str) -> list[dict]:
    """The project's folders and clips, nested: folders first (in natural order), then clips (oldest first)."""
    base = _project_dir(project)

    def walk(folder: Path) -> list[dict]:
        folders, clips = [], []
        for entry in folder.iterdir():
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                folders.append({"type": "folder", "name": entry.name, "path": _rel(project, entry),
                                "children": walk(entry)})
            elif entry.suffix == CLIP_SUFFIX:
                clip = _read(entry)
                if clip is not None:
                    clips.append({"type": "clip", "name": clip["title"], "kind": clip["kind"],
                                  "path": _rel(project, entry), "created": clip.get("created", 0)})
        folders.sort(key=lambda f: _natural(f["name"]))
        clips.sort(key=lambda c: (c["created"], _natural(c["name"])))
        return folders + clips

    return walk(base)


def make_folder(project: str, parent: str, name: str) -> str:
    folder = _resolve(project, parent)
    if not folder.is_dir():
        raise ClipboardError("That folder doesn't exist any more.")
    path = folder / safe_name(name)
    if path.exists():
        raise ClipboardError(f"{path.name} already exists there.")
    path.mkdir()
    return _rel(project, path)


def save_clip(project: str, folder: str, clip: dict) -> str:
    """Write a clip into a folder and return its path. A clip with the same id is replaced."""
    if clip.get("kind") not in KINDS:
        raise ClipboardError(f"A clip's kind must be one of {', '.join(KINDS)}.")
    target = _resolve(project, folder)
    if not target.is_dir():
        raise ClipboardError("That folder doesn't exist any more.")
    clip = {**clip, "id": clip.get("id") or uuid.uuid4().hex, "created": clip.get("created") or time.time()}
    clip["title"] = clip.get("title", "").strip() or "Untitled"
    stem = safe_name(_plain_title(clip["title"]))
    path = target / f"{stem}{CLIP_SUFFIX}"
    n = 2
    while path.exists() and (_read(path) or {}).get("id") != clip["id"]:
        path = target / f"{stem} {n}{CLIP_SUFFIX}"
        n += 1
    path.write_text(json.dumps(clip, ensure_ascii=False, indent=2), encoding="utf-8")
    return _rel(project, path)


def read_clip(project: str, path: str) -> dict:
    clip = _read(_resolve(project, path))
    if clip is None:
        raise ClipboardError("That clip can't be opened. It may have been moved or deleted.")
    return clip


def move_clip(project: str, path: str, folder: str) -> str:
    source = _resolve(project, path)
    clip = read_clip(project, path)
    if source.parent == _resolve(project, folder):
        return _rel(project, source)
    new_path = save_clip(project, folder, clip)
    source.unlink()
    return new_path


def delete_clip(project: str, path: str) -> None:
    source = _resolve(project, path)
    if source.suffix != CLIP_SUFFIX or not source.is_file():
        raise ClipboardError("That clip doesn't exist any more.")
    source.unlink()


def delete_folder(project: str, path: str) -> None:
    """Delete an empty folder. Folders with clips in them are kept, so nothing is lost by accident."""
    folder = _resolve(project, path)
    if folder == _project_dir(project).resolve() or not folder.is_dir():
        raise ClipboardError("That folder doesn't exist any more.")
    if any(folder.rglob(f"*{CLIP_SUFFIX}")):
        raise ClipboardError(f"{folder.name} still has clips in it. Move or delete them first.")
    shutil.rmtree(folder)


def _read(path: Path) -> dict | None:
    try:
        clip = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(clip, dict) or clip.get("kind") not in KINDS or not isinstance(clip.get("title"), str):
        return None
    return clip


def _plain_title(title: str) -> str:
    """A note title may contain LaTeX ($\\operatorname{Tr}(AB)$); file names get a plain version."""
    title = title.replace("$", "")
    title = re.sub(r"\\(operatorname|mathrm|text|mathbf|mathit)\{([^{}]*)\}", r"\2", title)
    title = re.sub(r"\\([A-Za-z]+)", r"\1", title)
    return title.replace("{", "").replace("}", "")
