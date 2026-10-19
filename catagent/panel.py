"""The panel that opens from the arrow under the cat: mode, project, connections and the Notepad.

It's a frosted box like the design. On a Mac it puts a real macOS blur (NSVisualEffectView)
behind a see-through card. If that isn't possible (no pyobjc, not a Mac, or CAT_FROSTED=0),
the card is just drawn nearly opaque, which looks the same apart from the blur.
"""

import sys

from PySide6.QtCore import QByteArray, Qt, Signal
from PySide6.QtGui import QAction, QColor, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import clipboard, config, connections, context
from .cat_widget import floating_window_flags
from .clipboard import ClipboardError

WIDTH = 368       # the card, as in the design
MARGIN = 26       # see-through room around the card for its shadow
RADIUS = 18
MODES = [("Study", "Study mode", "Learn step by step in the Notepad")]
DOTS = {  # status colour: (dot, halo with alpha)
    "green": ("#2E9E4A", (46, 158, 74, 46)),
    "amber": ("#D99A1E", (217, 154, 30, 51)),
    "red": ("#D93A2F", (217, 58, 47, 41)),
}

ICONS = {
    "down": '<path d="M6 9l6 6 6-6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "notepad": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/>',
}

STYLE = """
#card { background: rgba(246, 246, 248, %ALPHA%); border: 1px solid rgba(255, 255, 255, 0.75); border-radius: 18px; }
QLabel { color: #1C1C1E; font-size: 14px; background: transparent; border: none; }
QLabel[role="caption"] { color: #55555B; font-size: 11px; }
QLabel[role="hint"] { color: #55555B; font-size: 12px; }
QLabel[role="value"] { font-size: 14px; font-weight: 600; }
QLabel[role="project"] { font-size: 16px; font-weight: 700; }
QLabel[role="title"] { font-size: 13px; font-weight: 700; }
QLabel[role="name"] { font-weight: 600; }
QLabel[role="error"] { color: #B42318; font-size: 12px; }
Tile { background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 10px; }
Tile:hover { background: rgba(255, 255, 255, 0.92); }
Tile[selected="true"] { background: #E8F0FD; border-color: rgba(10, 91, 196, 0.18); }
Tile:focus { border: 2px solid #0A5BC4; }
#menu, #form { background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 12px; }
#connections { background: rgba(255, 255, 255, 0.55); border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 14px; }
#row { background: rgba(255, 255, 255, 0.7); border: none; border-radius: 10px; }
QPushButton { font-size: 13px; font-weight: 600; color: #1C1C1E; }
QPushButton#small { min-height: 34px; padding: 0 12px; border-radius: 8px; border: 1px solid rgba(0, 0, 0, 0.12); background: #FFFFFF; }
QPushButton#small:hover { background: #F5F5F7; }
QPushButton#square { min-width: 46px; max-width: 46px; border-radius: 10px; border: 1px solid rgba(0, 0, 0, 0.08); background: rgba(255, 255, 255, 0.7); }
QPushButton#square:hover { background: rgba(255, 255, 255, 0.92); }
QPushButton#link { min-height: 40px; padding: 0 8px; border: none; border-radius: 10px; background: transparent; color: #0A5BC4; font-size: 14px; text-align: left; }
QPushButton#link:hover { background: rgba(255, 255, 255, 0.6); }
QPushButton#dark { min-height: 46px; border: none; border-radius: 12px; background: #1C1C1E; color: #FFFFFF; font-size: 15px; }
QPushButton#dark:hover { background: #333336; }
QPushButton#plain { min-height: 36px; padding: 0 14px; border-radius: 9px; border: 1px solid rgba(0, 0, 0, 0.12); background: #FFFFFF; font-size: 14px; font-weight: 400; }
QPushButton#create { min-height: 36px; padding: 0 14px; border-radius: 9px; border: none; background: #1C1C1E; color: #FFFFFF; font-size: 14px; }
QPushButton:focus { outline: none; border: 2px solid #0A5BC4; }
QLineEdit { min-height: 40px; padding: 0 12px; border-radius: 9px; border: 1px solid rgba(0, 0, 0, 0.14); background: #FFFFFF; color: #1C1C1E; font-size: 15px; selection-background-color: #F5C99B; }
QLineEdit:focus { border: 2px solid #0A5BC4; }
"""


def icon(name: str, color: str = "#1C1C1E", size: int = 16, stroke: float = 2.4) -> QPixmap:
    """One of the line icons from the design, drawn sharp on Retina screens."""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" '
           f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')
    scale = 2
    pixmap = QPixmap(size * scale, size * scale)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(svg.encode())).render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(scale)
    return pixmap


def label(text: str = "", role: str = "") -> QLabel:
    widget = QLabel(text)
    if role:
        widget.setProperty("role", role)
    widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    return widget


def icon_label(name: str, color: str = "#1C1C1E", size: int = 16, stroke: float = 2.4) -> QLabel:
    widget = QLabel()
    widget.setPixmap(icon(name, color, size, stroke))
    widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    return widget


class Tile(QFrame):
    """A rounded box that works as a button: click it, or Tab to it and press Space or Return."""

    clicked = Signal()

    def __init__(self, accessible_name: str = ""):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)  # a focus ring for the keyboard, not after a click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(accessible_name)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clicked.emit()
        else:
            super().keyPressEvent(event)


class Dot(QLabel):
    """The green, amber or red status circle, with a soft halo."""

    def __init__(self, color: str):
        super().__init__()
        self.setFixedSize(16, 16)
        fill, halo = DOTS[color]
        self._fill, self._halo = QColor(fill), QColor(*halo)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._halo)
        p.drawEllipse(0, 0, 16, 16)
        p.setBrush(self._fill)
        p.drawEllipse(3, 3, 10, 10)
        p.end()


def _clear(layout: QLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()


class Panel(QWidget):
    notepad_requested = Signal()
    project_changed = Signal(str)
    visibility_changed = Signal(bool)
    resized = Signal()

    def __init__(self):
        super().__init__(None, floating_window_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)
        self.setWindowTitle(f"{config.CAT_NAME}'s panel")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # so opening it doesn't put a focus ring on a box
        self.frosted = False
        self._tried_frost = False
        self.setStyleSheet(STYLE.replace("%ALPHA%", "0.97"))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        outer.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)  # the window follows the content
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedWidth(WIDTH)
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(30, 35, 50, 60))
        self.card.setGraphicsEffect(shadow)
        outer.addWidget(self.card)

        body = QVBoxLayout(self.card)
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(14)

        # Mode | Project | +
        row = QHBoxLayout()
        row.setSpacing(8)
        self.mode_tile = self._two_line_tile("Mode", MODES[0][0], "value", "Choose a mode")
        self.mode_tile.clicked.connect(lambda: self._toggle(self.modes_box))
        row.addWidget(self.mode_tile)
        self.project_tile = self._two_line_tile("Project", "", "project", "Choose a project")
        self.project_tile.clicked.connect(lambda: self._toggle(self.projects_box))
        row.addWidget(self.project_tile, 1)
        plus = QPushButton()
        plus.setObjectName("square")
        plus.setIcon(icon("plus", size=18))
        plus.setAccessibleName("Create a new project")
        plus.setToolTip("New project")
        plus.setCursor(Qt.CursorShape.PointingHandCursor)
        plus.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)  # as tall as its neighbours
        plus.clicked.connect(self._start_adding)
        row.addWidget(plus)
        body.addLayout(row)

        self.modes_box = self._menu_box()
        for _, title, sub in MODES:
            item = Tile(title)
            item.set_selected(True)
            line = QHBoxLayout(item)
            line.setContentsMargins(10, 6, 10, 6)
            words = QVBoxLayout()
            words.setSpacing(0)
            words.addWidget(label(title, "name"))
            words.addWidget(label(sub, "hint"))
            line.addLayout(words, 1)
            line.addWidget(icon_label("check", "#0A5BC4", 16, 2.8))
            item.clicked.connect(lambda: self.modes_box.hide())
            self.modes_box.layout().addWidget(item)
        more = label("More modes will appear here.", "hint")
        more.setContentsMargins(10, 4, 10, 4)
        self.modes_box.layout().addWidget(more)
        body.addWidget(self.modes_box)

        self.projects_box = self._menu_box()
        body.addWidget(self.projects_box)

        self.form = QFrame()
        self.form.setObjectName("form")
        form = QVBoxLayout(self.form)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(8)
        name_label = QLabel("New project name")
        name_label.setProperty("role", "hint")
        form.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Math 1")
        self.name_input.setAccessibleName("New project name")
        self.name_input.returnPressed.connect(self._create_project)
        name_label.setBuddy(self.name_input)
        form.addWidget(self.name_input)
        self.form_error = label("", "error")
        self.form_error.hide()
        form.addWidget(self.form_error)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("plain")
        cancel.clicked.connect(self.form.hide)
        create = QPushButton("Create")
        create.setObjectName("create")
        create.clicked.connect(self._create_project)
        buttons.addWidget(cancel)
        buttons.addWidget(create)
        form.addLayout(buttons)
        self.form.hide()
        body.addWidget(self.form)

        # Connections
        card = QFrame()
        card.setObjectName("connections")
        conn = QVBoxLayout(card)
        conn.setContentsMargins(12, 12, 12, 8)
        conn.setSpacing(8)
        head = QHBoxLayout()
        head.addWidget(label("Connections", "title"))
        head.addStretch(1)
        head.addWidget(label(f"What {config.CAT_NAME} can see and use", "hint"))
        conn.addLayout(head)
        self.rows = QVBoxLayout()
        self.rows.setSpacing(6)
        conn.addLayout(self.rows)
        self.catalog_box = QFrame()
        self.catalog = QGridLayout(self.catalog_box)  # two columns of names, so the list stays short
        self.catalog.setContentsMargins(0, 0, 0, 0)
        self.catalog.setSpacing(6)
        self.catalog_box.hide()
        conn.addWidget(self.catalog_box)
        self.add_tool = QPushButton("  Add a tool")
        self.add_tool.setObjectName("link")
        self.add_tool.setIcon(icon("plus", "#0A5BC4", 16))
        self.add_tool.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_tool.clicked.connect(lambda: self._toggle(self.catalog_box))
        conn.addWidget(self.add_tool)
        body.addWidget(card)

        notepad = QPushButton("  Open Notepad")
        notepad.setObjectName("dark")
        notepad.setIcon(icon("notepad", "#FFFFFF", 18, 2))
        notepad.setCursor(Qt.CursorShape.PointingHandCursor)
        notepad.clicked.connect(self.notepad_requested.emit)
        body.addWidget(notepad)

        self.refresh()

    # ---- building blocks -------------------------------------------------------------------

    def _two_line_tile(self, caption: str, value: str, role: str, accessible: str) -> Tile:
        tile = Tile(accessible)
        lines = QVBoxLayout(tile)
        lines.setContentsMargins(10, 7, 10, 7)
        lines.setSpacing(1)
        lines.addWidget(label(caption, "caption"))
        value_row = QHBoxLayout()
        value_row.setSpacing(4)
        tile.value = label(value, role)
        value_row.addWidget(tile.value)
        value_row.addWidget(icon_label("down", size=12, stroke=2.6))
        value_row.addStretch(1)
        lines.addLayout(value_row)
        return tile

    def _menu_box(self) -> QFrame:
        box = QFrame()
        box.setObjectName("menu")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)
        box.hide()
        return box

    def _toggle(self, box: QFrame) -> None:
        """Open one drop-down at a time."""
        opening = box.isHidden()
        for other in (self.modes_box, self.projects_box, self.form, self.catalog_box):
            other.hide()
        box.setVisible(opening)

    # ---- what it shows -----------------------------------------------------------------------

    def refresh(self) -> None:
        """Re-read the projects and connections; the Notepad or a file in Finder may have changed them."""
        current = clipboard.current_project()
        self.project_tile.value.setText(self._elide(current))
        self.project_tile.setToolTip(current)

        layout = self.projects_box.layout()
        _clear(layout)
        for name in clipboard.projects():
            item = Tile(name)
            item.set_selected(name == current)
            line = QHBoxLayout(item)
            line.setContentsMargins(10, 8, 10, 8)
            line.addWidget(label(name, "name"), 1)
            if name == current:
                line.addWidget(icon_label("check", "#0A5BC4", 16, 2.8))
            item.clicked.connect(lambda name=name: self._choose_project(name))
            layout.addWidget(item)

        _clear(self.rows)
        for tool_id, tool, on in connections.shown():
            color, words = connections.status(tool_id)
            row = QFrame()
            row.setObjectName("row")
            row.setMinimumHeight(44)
            row.setToolTip(tool.does)
            line = QHBoxLayout(row)
            line.setContentsMargins(8, 4, 4, 4)
            line.setSpacing(10)
            line.addWidget(Dot(color))
            words_box = QVBoxLayout()
            words_box.setSpacing(0)
            words_box.addWidget(label(tool.name, "name"))
            status = label(words, "hint")
            status.setWordWrap(True)
            words_box.addWidget(status)
            line.addLayout(words_box, 1)
            button = QPushButton("Disconnect" if on else "Connect")
            button.setObjectName("small")
            button.setAccessibleName(f"{'Disconnect' if on else 'Connect'} {tool.name}")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, t=tool_id, on=on: self._set_connected(t, not on))
            line.addWidget(button)
            remove = QAction(f"Remove {tool.name} from the list", row)
            remove.triggered.connect(lambda checked=False, t=tool_id: self._remove_tool(t))
            row.addAction(remove)
            row.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
            self.rows.addWidget(row)

        _clear(self.catalog)
        extra = connections.addable()
        for i, (tool_id, tool) in enumerate(extra):
            item = Tile(f"Add {tool.name}")
            item.setToolTip(tool.does)
            line = QHBoxLayout(item)
            line.setContentsMargins(8, 7, 8, 7)
            line.setSpacing(6)
            line.addWidget(icon_label("plus", "#0A5BC4", 12, 2.6))
            line.addWidget(label(tool.name, "name"), 1)
            item.clicked.connect(lambda t=tool_id: self._add_tool(t))
            self.catalog.addWidget(item, i // 2, i % 2)
        self.add_tool.setVisible(bool(extra))
        if not extra:
            self.catalog_box.hide()

    def _elide(self, text: str) -> str:
        metrics = self.project_tile.value.fontMetrics()
        return metrics.elidedText(text, Qt.TextElideMode.ElideRight, 190)

    # ---- actions ---------------------------------------------------------------------------

    def _choose_project(self, name: str) -> None:
        clipboard.set_current_project(name)
        self.projects_box.hide()
        self.refresh()
        self.project_changed.emit(name)

    def _start_adding(self) -> None:
        self._toggle(self.form)
        if self.form.isVisible():
            self.form_error.hide()
            self.name_input.clear()
            self.name_input.setFocus()

    def _create_project(self) -> None:
        try:
            name = clipboard.make_project(self.name_input.text())
        except ClipboardError as e:
            self.form_error.setText(str(e))
            self.form_error.show()
            return
        self.form.hide()
        self._choose_project(name)

    def _set_connected(self, tool_id: str, on: bool) -> None:
        connections.set_connected(tool_id, on)
        self.refresh()

    def _add_tool(self, tool_id: str) -> None:
        connections.add(tool_id)
        self.catalog_box.hide()
        self.refresh()

    def _remove_tool(self, tool_id: str) -> None:
        connections.remove(tool_id)
        self.refresh()

    # ---- showing ---------------------------------------------------------------------------

    def open(self) -> None:
        for box in (self.modes_box, self.projects_box, self.form, self.catalog_box):
            box.hide()
        self.refresh()
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._tried_frost:
            self._tried_frost = True
            self.frosted = _frost(self, MARGIN, RADIUS)
            if self.frosted:
                self.setStyleSheet(STYLE.replace("%ALPHA%", "0.62"))
        self.visibility_changed.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()  # a drop-down opened or closed; the app keeps it by the cat

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)


def _frost(widget: QWidget, inset: int, radius: int) -> bool:
    """Put a real macOS blur behind the card. Returns False (and changes nothing) if it can't."""
    if not context.IS_MAC or not config.FROSTED:
        return False
    try:
        import objc
        from AppKit import (
            NSAppearance,
            NSBezierPath,
            NSColor,
            NSEdgeInsetsMake,
            NSImage,
            NSInsetRect,
            NSVisualEffectView,
            NSWindowBelow,
        )
    except ImportError:
        return False
    try:
        qt_view = objc.objc_object(c_void_p=int(widget.winId()))
        frame_view = qt_view.superview()
        if frame_view is None:
            return False

        def draw(rect):
            NSColor.blackColor().set()
            NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(rect, radius, radius).fill()
            return True

        side = 2 * radius + 1
        mask = NSImage.imageWithSize_flipped_drawingHandler_((side, side), False, draw)
        mask.setCapInsets_(NSEdgeInsetsMake(radius, radius, radius, radius))
        mask.setResizingMode_(1)  # stretch the middle, keep the rounded corners

        blur = NSVisualEffectView.alloc().initWithFrame_(NSInsetRect(qt_view.frame(), inset, inset))
        blur.setAutoresizingMask_(2 | 16)  # keep the same inset as the window grows and shrinks
        blur.setBlendingMode_(0)           # blur what's behind the window
        blur.setMaterial_(6)               # popover
        blur.setState_(1)                  # always active, even while another app is in front
        blur.setAppearance_(NSAppearance.appearanceNamed_("NSAppearanceNameAqua"))
        blur.setMaskImage_(mask)
        frame_view.addSubview_positioned_relativeTo_(blur, NSWindowBelow, qt_view)
        return True
    except Exception as e:  # an AppKit change shouldn't take the cat down; fall back to the plain card
        print(f"Frosted panel unavailable, using a plain one: {e}", file=sys.stderr)
        return False
