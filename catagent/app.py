"""Wires the cat, its input bar, its panel, its speech cloud, the Notepad and the agent together."""

import json
import sys

from PySide6.QtCore import QPoint, QRect, QTimer
from PySide6.QtWidgets import QApplication

from . import activity, clipboard, config, connections, context, costumes, providers
from .agent import AgentBridge
from .cat_widget import BADGE_SPACE, HEAD_X, CatWidget
from .command_bar import CommandBar

# Imported before the QApplication exists, as Qt WebEngine (which the Notepad uses) needs.
from .notepad import Notepad
from .panel import MARGIN as PANEL_MARGIN
from .panel import Panel
from .speech_cloud import SpeechCloud


def _hide_dock_icon() -> None:
    """Make the cat a background app with no Dock icon (needs pyobjc, optional)."""
    try:
        from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    except ImportError:
        return
    NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)


class CatApp:
    def __init__(self, app: QApplication):
        self.app = app
        self.watcher = context.ContextWatcher()
        self.agent = AgentBridge(self.watcher)
        self.cat = CatWidget()
        self.bar = CommandBar()
        self.panel = Panel()
        self.cloud = SpeechCloud()
        self._last_tip = ""
        self._turn_tip: tuple[str, str, str, int] | None = None  # a tip shown while working
        self._cloud_file: tuple[str, int] = ("", 0)               # what "Show me" opens
        self._permissions: list[tuple[str, str, str]] = []        # questions waiting for an answer
        self._hidden_for_capture: list = []
        self._watched_context = None
        self._notepad: Notepad | None = None                      # made the first time it's needed
        self._turn_from_notepad = False

        self.cat.keep_awake = lambda: self.bar.isVisible() or self.cloud.isVisible() or self.panel.isVisible()
        self.cat.clicked.connect(self.toggle_bar)
        self.cat.arrow_clicked.connect(self.toggle_panel)
        self.cat.moved.connect(self.follow_cat)
        self.cat.look_requested.connect(self.look_at_screen)
        self.cat.new_conversation_requested.connect(self.new_conversation)
        self.cat.notepad_requested.connect(lambda: self.notepad().open())
        self.cat.watch_toggled.connect(self.set_watch_mode)
        self.cat.auto_edit_toggled.connect(self.set_auto_edit)
        self.cat.stop_requested.connect(self.agent.stop_turn)
        self.cat.quit_requested.connect(self.quit)
        self.cat.costume_changed.connect(self.on_costume_changed)

        self.bar.submitted.connect(self.send)
        self.panel.visibility_changed.connect(self.cat.set_panel_open)
        self.panel.resized.connect(self.follow_cat)
        self.panel.project_changed.connect(self.on_project_changed)
        self.panel.notepad_requested.connect(self.open_notepad_from_panel)
        self.cloud.answered.connect(self.on_permission_answer)
        self.cloud.show_me.connect(lambda: context.open_in_editor(
            *self._cloud_file, use_vscode=connections.is_connected("vscode")))
        self.cloud.closed.connect(lambda: self.cat.set_alert(False))

        self.agent.busy_changed.connect(self.on_busy)
        self.agent.coding.connect(lambda: self.cat.set_coding(True))
        self.agent.finished.connect(self.on_finished)
        self.agent.failed.connect(self.on_failed)
        self.agent.notes_ready.connect(lambda notes: self.notepad().show_notes(notes))
        self.agent.costume_requested.connect(self.change_costume)
        self.agent.permission_requested.connect(self.on_permission)
        self.agent.tip.connect(self.on_tip)
        self.agent.hide_requested.connect(self.set_hidden_for_capture)

        self.watch_timer = QTimer()
        self.watch_timer.timeout.connect(self.watch_tick)
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._save_state)

    def start(self) -> None:
        self.watcher.start()
        self.agent.start()
        state = self._load_state()
        self.cat.set_costume(state.get("costume", "ginger"), animate=False)  # before placing: it sets the size
        screen = self.app.primaryScreen().availableGeometry()
        default = QPoint(screen.right() - self.cat.width() - 40, screen.bottom() - self.cat.height() - 120)
        pos = QPoint(*state["pos"]) if "pos" in state else default
        self.cat.move(self._clamp(QRect(pos, self.cat.size())))
        self.cat.show()
        if state.get("watch"):
            self.set_watch_mode(True)
        if state.get("auto_edit"):
            self.set_auto_edit(True)

    # ---- talking to the cat ------------------------------------------------------------------

    def toggle_bar(self) -> None:
        if self.bar.isVisible():
            self.bar.hide()
            return
        self.panel.hide()
        self.cat.set_alert(False)
        if not self._permissions:
            self.cloud.hide()
        self.follow_cat()
        self.bar.open()

    def toggle_panel(self) -> None:
        """The arrow under the cat: mode, project, connections and the Notepad."""
        if self.panel.isVisible():
            self.panel.hide()
            return
        self.bar.hide()
        if not self._permissions:
            self.cloud.hide()
        self.panel.open()
        self.follow_cat()

    def on_project_changed(self, name: str) -> None:
        if self._notepad is not None and self._notepad.project != name:
            self._notepad.set_project(name)

    def open_notepad_from_panel(self) -> None:
        self.panel.hide()
        self.notepad().open()

    def change_costume(self, request: str) -> str:
        """Dress up: request is a costume name or "random". Returns the costume put on."""
        costume = costumes.pick(request, self.cat.costume)
        self.cat.set_costume(costume)
        return costume

    def send(self, text: str, *, from_notepad: bool = False) -> None:
        request = None if from_notepad else costumes.parse_request(text)
        if request is not None:
            # "change into dragon", "change costume": no need to ask the AI, just do it.
            if request == self.cat.costume:
                self.say("Already on! ✓", "That's what I'm wearing right now. 🐾")
                return
            costume = self.change_costume(request)
            self.say("Costume changed ✓", costumes.SAYS[costume])
            return
        self._turn_from_notepad = from_notepad
        project = clipboard.current_project()
        notes = [f"Mode: Study mode. Project: {project} (its notes are in {config.NOTES_DIR / project})."]
        ctx = self.watcher.last()
        self.cat.set_coding(not from_notepad and activity.looks_like_coding(text, ctx.app if ctx else ""))
        where = connections.describe(ctx)
        if where is not None:
            notes.append(where)
        if self._last_tip:
            notes.append(f"Tip you popped up earlier: {self._last_tip}")
            self._last_tip = ""
        text = "<context>\n" + "\n".join(notes) + "\n</context>\n\n" + text
        self._turn_tip = None
        self.agent.send(text)

    def on_costume_changed(self, costume: str) -> None:
        if self.cat.isVisible():  # at startup the saved costume is put back before the cat is placed
            self.follow_cat()
            self._save_state(costume=costume)

    def new_conversation(self) -> None:
        self.agent.new_conversation()
        if self._notepad is not None:
            self._notepad.forget_conversation()

    def notepad(self) -> Notepad:
        if self._notepad is None:
            self._notepad = Notepad()
            self._notepad.asked.connect(lambda text: self.send(text, from_notepad=True))
            self._notepad.stop_requested.connect(self.agent.stop_turn)
            self._notepad.project_changed.connect(lambda name: self.panel.isVisible() and self.panel.refresh())
            self._notepad.set_busy(self.agent.busy)
        return self._notepad

    def look_at_screen(self) -> None:
        self.send("Take a look at my screen. What am I working on, and is there anything I should fix?")

    def on_busy(self, busy: bool) -> None:
        self.cat.set_busy(busy)
        if self._notepad is not None:
            self._notepad.set_busy(busy)
        if busy:
            self.cloud.hide()
        else:
            self._permissions.clear()  # anything still unanswered was cancelled

    def on_finished(self, done: str, reply: str) -> None:
        """Say what happened: "Code changed ✓", plus the cat's short reply."""
        title = f"{done} ✓" if done else ""
        file_path, line = "", 0
        if self._turn_tip:
            tip_title, tip_message, file_path, line = self._turn_tip
            title = title or tip_title
            reply = reply or tip_message
        if not title and not reply:
            title = "Done! ✓"
        if self._turn_from_notepad and self._notepad is not None:
            self._notepad.set_reply(reply or title)
        self.say(title, reply, file_path=file_path, line=line)

    def on_failed(self, error: str) -> None:
        if self._turn_from_notepad and self._notepad is not None:
            self._notepad.set_error(error)
        self.say("Oops!", error)

    def say(self, title: str, body: str = "", *, file_path: str = "", line: int = 0) -> None:
        self._cloud_file = (file_path, line)
        self.cloud.say(title, body, file_button=bool(file_path))
        self.follow_cat()
        self.cloud.show()
        self.cat.poke()

    # ---- permission questions -----------------------------------------------------------------

    def on_permission(self, request_id: str, question: str, details: str) -> None:
        self._permissions.append((request_id, question, details))
        if len(self._permissions) == 1:
            self._ask_next()

    def _ask_next(self) -> None:
        _, question, details = self._permissions[0]
        self.cloud.say(question, details, ask=True)
        self.follow_cat()
        self.cloud.show()

    def on_permission_answer(self, allow: bool) -> None:
        if not self._permissions:
            return
        request_id, _, _ = self._permissions.pop(0)
        self.agent.resolve_permission(request_id, allow)
        if self._permissions:
            self._ask_next()

    # ---- tips ----------------------------------------------------------------------------------

    def on_tip(self, title: str, message: str, file_path: str, line: int) -> None:
        where = f" ({file_path}:{line})" if file_path else ""
        self._last_tip = f"{title}: {message}{where}"
        if self.agent.busy:
            # While working on your request, save it for the cloud at the end.
            self._turn_tip = (title, message, file_path, line)
            return
        # A watch-mode tip: you didn't ask, so the cat gets your attention.
        self.cat.set_alert(True)
        self.say(f"{title} !", message, file_path=file_path, line=line)

    def set_hidden_for_capture(self, hidden: bool) -> None:
        if hidden:
            self._hidden_for_capture = [w for w in (self.cat, self.bar, self.panel, self.cloud) if w.isVisible()]
            for w in self._hidden_for_capture:
                w.hide()
        else:
            for w in self._hidden_for_capture:
                w.show()
            self._hidden_for_capture = []

    # ---- watch mode ----------------------------------------------------------------------

    def set_watch_mode(self, on: bool) -> None:
        if on and not context.IS_MAC:
            self.say("Sorry!", "Watch mode needs macOS.")
            on = False
        self.cat.set_watching(on)
        if on:
            self.watch_timer.start(config.WATCH_INTERVAL_SEC * 1000)
        else:
            self.watch_timer.stop()
        self._save_state(watch=on)

    def set_auto_edit(self, on: bool) -> None:
        """Let the cat edit files without asking. Commands other than tests still ask."""
        self.agent.auto_edit = on
        self.cat.set_auto_edit(on)
        self._save_state(auto_edit=on)

    def watch_tick(self) -> None:
        """Glance at the screen, but only when the user has moved on to something new and settled."""
        ctx = self.watcher.last()
        if ctx is None or ctx == self._watched_context or self.bar.isVisible():
            return
        if connections.blocked(ctx):
            return  # not connected: no peeking
        if self.watcher.seconds_since_change() < 20:
            return
        self._watched_context = ctx
        self.agent.watch_check(ctx.describe())

    # ---- layout ------------------------------------------------------------------------------

    def follow_cat(self) -> None:
        """Keep the input bar and panel just under the cat and the speech cloud just above its head."""
        cat = self.cat.frameGeometry()
        screen = self.app.screenAt(cat.center()) or self.app.primaryScreen()
        area = screen.availableGeometry()
        head_x = cat.left() + HEAD_X * config.SCALE

        bar = self.bar.size()
        y = cat.bottom() - 4
        if y + bar.height() > area.bottom():
            y = cat.top() + BADGE_SPACE - bar.height()  # no room below: put it above instead
        self.bar.move(self._clamp(QRect(QPoint(head_x - bar.width() // 2, y), bar), area))

        # The panel's window has see-through margins for its shadow, so line up the card itself.
        panel = self.panel.size()
        y = cat.bottom() + 2 - PANEL_MARGIN
        if y + panel.height() - PANEL_MARGIN > area.bottom():
            y = cat.top() + BADGE_SPACE - panel.height() + PANEL_MARGIN  # no room below: above instead
        card_area = area.adjusted(-PANEL_MARGIN, -PANEL_MARGIN, PANEL_MARGIN, PANEL_MARGIN)
        self.panel.move(self._clamp(QRect(QPoint(head_x - panel.width() // 2, y), panel), card_area))

        cloud = self.cloud.size()
        y = cat.top() + BADGE_SPACE + 2 * config.SCALE - cloud.height()
        self.cloud.move(self._clamp(QRect(QPoint(head_x - cloud.width() // 2, y), cloud), area))
        self.cloud.point_tail_at(head_x)
        self.save_timer.start(500)

    def _clamp(self, rect: QRect, area: QRect | None = None) -> QPoint:
        area = area or self.app.primaryScreen().availableGeometry()
        x = min(max(rect.left(), area.left()), area.right() - rect.width())
        y = min(max(rect.top(), area.top()), area.bottom() - rect.height())
        return QPoint(x, y)

    # ---- state ----------------------------------------------------------------------------

    def _load_state(self) -> dict:
        try:
            return json.loads(config.STATE_FILE.read_text())
        except (OSError, ValueError):
            return {}

    def _save_state(self, **changes) -> None:
        state = self._load_state()
        state["pos"] = [self.cat.x(), self.cat.y()]
        state.update(changes)
        config.HOME_DIR.mkdir(parents=True, exist_ok=True)
        config.STATE_FILE.write_text(json.dumps(state))

    def quit(self) -> None:
        self._save_state()
        if self._notepad is not None:
            self._notepad.close()  # saves what's open
        self.watcher.stop()
        self.agent.shutdown()
        self.app.quit()


def main() -> int:
    providers.env()  # pick the model and check the key now, rather than on the first request
    app = QApplication(sys.argv)
    app.setApplicationName(config.CAT_NAME)
    app.setQuitOnLastWindowClosed(False)
    _hide_dock_icon()
    cat_app = CatApp(app)
    cat_app.start()
    return app.exec()
