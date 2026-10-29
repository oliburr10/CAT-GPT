"""The Notepad: a window with Ginger's study notes and, beside them, the clipboard of saved clips.

The page itself is HTML (web/notepad.html, with KaTeX for the maths) in a Qt web view. It talks
to the NotepadBridge below through Qt's web channel: the page calls the bridge's slots when you
click something, and the bridge sends back the whole state, which the page redraws from.
"""

import functools
import json
import subprocess
import uuid
from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QWidget

from . import clipboard, config, context, figures, study
from .clipboard import ClipboardError

PAGE = Path(__file__).parent / "web" / "notepad.html"
SIDE_WIDTH = 300


def _answer(method):
    """Run a request from the page. Reply with the new state, or with what went wrong."""
    @functools.wraps(method)
    def run(self, *args):
        try:
            extra = method(self, *args) or {}
        except ClipboardError as e:
            return json.dumps({"error": str(e)})
        except OSError as e:
            return json.dumps({"error": f"Couldn't do that: {e.strerror or e}"})
        return json.dumps({"state": self._n.state(), **extra})
    return run


class NotepadBridge(QObject):
    """What the page can ask for. Every slot replies with JSON: {"state": ...} or {"error": "..."}."""

    stateChanged = Signal(str)

    def __init__(self, notepad: "Notepad"):
        super().__init__()
        self._n = notepad

    @Slot(result=str)
    @_answer
    def state(self):
        pass

    @Slot(str, result=str)
    @_answer
    def selectProject(self, name):
        self._n.set_project(name)

    @Slot(str, result=str)
    @_answer
    def makeProject(self, name):
        self._n.set_project(clipboard.make_project(name))

    @Slot(str, str, result=str)
    @_answer
    def makeFolder(self, parent, name):
        return {"path": clipboard.make_folder(self._n.project, parent, name)}

    @Slot(str, str, str, result=str)
    @_answer
    def addNote(self, folder, kind, text):
        text = text.strip()
        title = text.splitlines()[0][:120] if text else ""
        clipboard.save_clip(self._n.project, folder, {"kind": kind, "title": title, "text": text})

    @Slot(str, result=str)
    @_answer
    def clip(self, folder):
        self._n.clip_current(folder)

    @Slot(str, str, result=str)
    @_answer
    def moveClip(self, path, folder):
        self._n.move_clip(path, folder)

    @Slot(str, result=str)
    @_answer
    def deleteClip(self, path):
        self._n.delete_clip(path)

    @Slot(str, result=str)
    @_answer
    def openClip(self, path):
        self._n.open_clip(path)

    @Slot(str, result=str)
    @_answer
    def reveal(self, folder):
        self._n.reveal(folder)

    @Slot(bool, result=str)
    @_answer
    def setSideOpen(self, open_):
        self._n.set_side_open(open_)

    @Slot(str, result=str)
    @_answer
    def ask(self, text):
        self._n.ask(text)

    @Slot(result=str)
    @_answer
    def stop(self):
        self._n.stop_requested.emit()

    @Slot(result=str)
    @_answer
    def attach(self):
        self._n.attach()

    @Slot(result=str)
    @_answer
    def exportTex(self):
        self._n.export_tex()


class _Page(QWebEnginePage):
    """Keeps the Notepad on its own page; any web link opens in your browser instead."""

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if url.isLocalFile() or url.scheme() in ("qrc", "data", "about"):
            return True
        QDesktopServices.openUrl(url)
        return False


class Notepad(QWidget):
    asked = Signal(str)          # a message for the cat, already wrapped with the Notepad's context
    stop_requested = Signal()
    project_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config.CAT_NAME} · Notepad")
        self.setMinimumSize(860, 560)
        saved = self._load()
        self.project = clipboard.current_project()
        self.current: dict | None = saved.get("current")          # {"id", "kind", "title", "notes" | "text"}
        if self.current and study.is_old(self.current.get("notes")):
            self.current["notes"] = study.upgrade(self.current["notes"])
        self.current_path: str | None = saved.get("current_path")  # where it's clipped, if it is
        self.from_disk = saved.get("from_disk", True)              # not written in this conversation
        self.side_open = saved.get("side_open", True)
        self.busy = False            # the cat is working on something
        self.asking = False          # ... and it's what you asked from here
        self.reply = ""
        self.error = ""
        self.attached: list[str] = []

        self.view = QWebEngineView(self)
        self.view.setPage(_Page(self.view))
        # 3D figures download their structure from the Protein Data Bank (RCSB).
        settings = self.view.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.bridge = NotepadBridge(self)
        self.channel = QWebChannel(self.view.page())
        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)
        self.view.load(QUrl.fromLocalFile(str(PAGE)))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.resize(*saved.get("size", [1000 + (SIDE_WIDTH if self.side_open else 0), 820]))

    # ---- what the page shows -------------------------------------------------------------

    def state(self) -> dict:
        if self.current_path and self.current:
            try:
                if clipboard.read_clip(self.project, self.current_path).get("id") != self.current.get("id"):
                    self.current_path = None
            except ClipboardError:
                self.current_path = None   # moved or deleted in Finder
        return {
            "project": self.project,
            "projects": clipboard.projects(),
            "tree": clipboard.tree(self.project),
            "current": self.current,
            "currentPath": self.current_path,
            "busy": self.busy,
            "asking": self.asking,
            "reply": self.reply,
            "error": self.error,
            "attached": [Path(p).name for p in self.attached],
            "sideOpen": self.side_open,
            "catName": config.CAT_NAME,
        }

    def refresh(self) -> None:
        self.bridge.stateChanged.emit(json.dumps(self.state()))
        self._save()

    # ---- called by the app ------------------------------------------------------------------

    def open(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def show_notes(self, notes: dict) -> None:
        """New notes from the cat. They replace what's open; clipped notes stay safe in their files."""
        notes = figures.add_energies(notes)   # each RNA fold's free energy, if ViennaRNA is installed
        self.current = {"id": uuid.uuid4().hex, "kind": "solution", "title": notes["title"], "notes": notes}
        self.current_path = None
        self.from_disk = False
        self.error = ""
        self.refresh()
        self.open()

    def set_busy(self, busy: bool) -> None:
        self.busy = busy
        if not busy:
            self.asking = False
        self.refresh()

    def set_reply(self, text: str) -> None:
        self.reply, self.error = text, ""
        self.refresh()

    def set_error(self, text: str) -> None:
        self.error = text
        self.refresh()

    def forget_conversation(self) -> None:
        """The cat started a new conversation, so it no longer remembers writing the open notes."""
        self.from_disk = True

    # ---- called by the page ------------------------------------------------------------------

    def set_project(self, name: str) -> None:
        """Switch project. The cat's panel shows the same project, so it hears about it too."""
        clipboard.set_current_project(name)
        if name != self.project:
            self.project = name
            self.current_path = None
            self.project_changed.emit(name)
        self.refresh()

    def clip_current(self, folder: str) -> None:
        if not self.current:
            raise ClipboardError("There's no note open to clip.")
        self.current_path = clipboard.save_clip(self.project, folder, self.current)
        self.refresh()

    def move_clip(self, path: str, folder: str) -> None:
        new_path = clipboard.move_clip(self.project, path, folder)
        if path == self.current_path:
            self.current_path = new_path
        self.refresh()

    def delete_clip(self, path: str) -> None:
        clipboard.delete_clip(self.project, path)
        if path == self.current_path:
            self.current_path = None
        self.refresh()

    def open_clip(self, path: str) -> None:
        clip = clipboard.read_clip(self.project, path)
        if clip["kind"] == "solution":
            if study.is_old(clip.get("notes")):
                clip = {**clip, "notes": study.upgrade(clip["notes"])}   # written in the earlier format
            elif study.problems(clip.get("notes")):
                raise ClipboardError("That clip's notes are damaged, so they can't be shown.")
        self.current, self.current_path, self.from_disk = clip, path, True
        self.reply = self.error = ""
        self.refresh()

    def reveal(self, folder: str) -> None:
        path = config.NOTES_DIR / self.project / folder
        if context.IS_MAC:
            subprocess.run(["open", str(path)], check=False)
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def set_side_open(self, open_: bool) -> None:
        """Make room for the clipboard by widening the window, so it never covers the notes."""
        if open_ != self.side_open:
            screen = (self.screen() or QApplication.primaryScreen()).availableGeometry()
            frame = self.frameGeometry()
            if open_:
                grow = min(SIDE_WIDTH, max(0, screen.width() - frame.width()))
                left = min(frame.left(), screen.right() - frame.width() - grow)
                self.setGeometry(self.geometry().translated(left - frame.left(), 0).adjusted(0, 0, grow, 0))
            elif self.width() - SIDE_WIDTH >= self.minimumWidth():
                self.resize(self.width() - SIDE_WIDTH, self.height())
        self.side_open = open_
        self.refresh()

    def ask(self, text: str) -> None:
        text = text.strip()
        if not text or self.asking:
            return
        if self.busy:
            self.error = f"{config.CAT_NAME} is busy with something else. Ask again in a moment."
            self.refresh()
            return
        if self.attached:
            text += "\n\nAttached files:\n" + "\n".join(self.attached)
            self.attached = []
        notes = ["[Sent from the Notepad, in study mode.]"]
        if self.current:
            notes.append(f"The note open right now is \"{self.current['title']}\".")
            if self.from_disk:
                # The cat didn't write these in this conversation, so show it what they say.
                body = self.current.get("notes") or self.current.get("text", "")
                notes.append("Here it is:\n" + json.dumps(body, ensure_ascii=False))
        self.reply = self.error = ""
        self.asking = True
        self.asked.emit("\n".join(notes) + "\n\n" + text)

    def attach(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Attach a problem (an image or a file)", str(config.WORKSPACE))
        if path:
            self.attached.append(path)
        self.refresh()

    def export_tex(self) -> None:
        if not self.current or self.current["kind"] != "solution":
            raise ClipboardError("Open some study notes first.")
        stem = clipboard.safe_name(clipboard._plain_title(self.current["title"]))
        start = config.NOTES_DIR / self.project / (Path(self.current_path).parent if self.current_path else "") / f"{stem}.tex"
        path, _ = QFileDialog.getSaveFileName(self, "Export as LaTeX", str(start), "LaTeX (*.tex)")
        if path:
            Path(path).write_text(study.to_tex(self.current["notes"]), encoding="utf-8")
            self.set_reply(f"Saved {Path(path).name}. It compiles with pdflatex, or paste it into Overleaf.")

    # ---- saving -----------------------------------------------------------------------------

    def closeEvent(self, event):
        self._save()
        super().closeEvent(event)

    def _load(self) -> dict:
        try:
            return json.loads(config.NOTEPAD_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _save(self) -> None:
        config.HOME_DIR.mkdir(parents=True, exist_ok=True)
        config.NOTEPAD_FILE.write_text(json.dumps({
            "current": self.current, "current_path": self.current_path,
            "from_disk": True, "side_open": self.side_open, "size": [self.width(), self.height()],
        }, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    """`python -m catagent.notepad [trace|purity|roll|ribo]`: just the Notepad, on example notes.

    With no argument it opens the trace example if nothing is open yet; with one, it opens that
    example (ribo has the RNA fold and 3D molecule figures). To ask Ginger for new notes, run the
    whole app (python run.py).
    """
    import sys

    from . import examples

    app = QApplication(sys.argv)
    app.setApplicationName(config.CAT_NAME)
    notepad = Notepad()
    if len(sys.argv) > 1 and sys.argv[1] in examples.EXAMPLES:
        notepad.show_notes(examples.EXAMPLES[sys.argv[1]])
    elif notepad.current is None:
        notepad.show_notes(examples.TRACE_NOTES)
    notepad.asked.connect(lambda text: notepad.set_reply(
        "I'm not running yet. Start me with python run.py, then ask again from here."))
    notepad.open()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
