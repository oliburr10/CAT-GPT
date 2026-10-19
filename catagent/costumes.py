"""Costumes for the cat: Ginger as itself, a Green Dragon onesie, and a Wizard with hat and wand.

Every costume has every frame the plain cat has (sitting, blinking, coding, sleeping, waking
up...), built from the plain frames in sprites.py: the costume recolours the fur, adds pieces
on top (horns, a hat, a wand) and may need extra rows above the head. All frames of a costume
are the same size, with the cat's feet on the bottom row.

Each costume also has a dressing-up animation, played when you pick it: DRESS_UP[costume] is a
list of (frame, seconds).
"""

import random
import re

from PySide6.QtGui import QPixmap

from . import sprites

WIDTH = sprites.WIDTH
SITTING = ["idle", "blink", "tail", "look_up", "yawn"]
CODING = ["code_a", "code_b", "code_glow"]
LYING = ["sleep_a", "sleep_b", "wake"]


def _pad(grid: list[str], rows: int) -> list[str]:
    return ["." * WIDTH] * rows + list(grid)


def _paint(grid: list[str], art: list[str], x: int, y: int) -> list[str]:
    """Draw `art` onto the grid with its top-left at (x, y). '.' in the art is see-through;
    anything falling off the grid is clipped."""
    out = [list(row) for row in grid]
    for dy, line in enumerate(art):
        for dx, ch in enumerate(line):
            gx, gy = x + dx, y + dy
            if ch != "." and 0 <= gy < len(out) and 0 <= gx < WIDTH:
                out[gy][gx] = ch
    return ["".join(row) for row in out]


def _recolor(grid: list[str], rule) -> list[str]:
    return ["".join(rule(x, y, ch) for x, ch in enumerate(row)) for y, row in enumerate(grid)]


# ---- Green Dragon ------------------------------------------------------------------------
# A green onesie with a hood: the cat's face peeks out, the hood has cream horns and an
# orange crest, the belly is pale yellow, the tail ends in a spade and little wings stick out.

DRAGON_HEADROOM = 3

_HORNS = [            # drawn over the top of the head, in the padded grid
    "K..............K....",
    "KAK...........KAK...",
    ".KAK.........KAK....",
    ".KaK..KZZK...KaK....",
    ".KRRK.KZK..KRRK.....",
]
_WING = [             # a little bat wing behind the right shoulder
    "....KK",
    "...KrK",
    "..KRrK",
    ".KRrRK",
    "KRKRKK",
    ".K.K..",
]
_SPADE = [            # the tail's tip
    ".KK.",
    "KZZK",
    "KZZK",
    ".KK.",
]
_SMALL_HORNS = ["K.....K", "KAK.KAK", ".KaKaK."]  # for the lying-down head, seen from the side
_SPARKLES = [         # stars twinkling around the cat when the costume goes on
    "...Y.............Y..",
    "..YYY..........YYY..",
    "...Y.............Y..",
]


def _dragon_sitting(frame: str, grid: list[str]) -> list[str]:
    coding = frame in CODING

    def rule(x, y, ch):
        face = 4 <= y <= 9 and 2 <= x <= 13
        if ch == "O":
            return "O" if face else "R"
        if ch == "D":
            return "D" if face else "r"
        if ch == "P" and y <= 2:
            return "R"                      # the ears become the hood's ear bumps
        if ch in "WS" and y >= 10:
            if coding and y >= 12 or y >= 16:
                return "R" if ch == "W" else "r"   # green paws and feet
            return "U" if ch == "W" else "u"       # pale belly scales
        return ch

    out = _pad(_recolor(grid, rule), DRAGON_HEADROOM)
    out = _paint(out, _HORNS, 0, 0)
    out = _paint(out, _WING, 14, DRAGON_HEADROOM + 4)
    if not coding:
        tail_top = 11 if frame == "tail" else 12
        out = _paint(out, _SPADE, 16, DRAGON_HEADROOM + tail_top - 2)
    return out


def _dragon_lying(frame: str, grid: list[str]) -> list[str]:
    def rule(x, y, ch):
        face = 12 <= y <= 14 and 1 <= x <= 8
        if ch == "O":
            return "O" if face else "R"
        if ch == "D":
            return "D" if face else "r"
        if ch == "P" and y <= 11:
            return "R"
        if ch in "WS":
            return "R" if ch == "W" else "r"
        return ch

    out = _pad(_recolor(grid, rule), DRAGON_HEADROOM)
    out = _paint(out, _SMALL_HORNS, 1, DRAGON_HEADROOM + 6)   # over the ears, which are on row 9
    back = 9 if frame == "sleep_b" else 10
    out = _paint(out, ["K.K.K", "ZKZKZ"], 12, DRAGON_HEADROOM + back - 2)  # spikes along the back
    return out


def _dragon_stretch(grid: list[str]) -> list[str]:
    def rule(x, y, ch):
        face = 12 <= y <= 15 and 1 <= x <= 8
        if ch == "O":
            return "O" if face else "R"
        if ch == "D":
            return "D" if face else "r"
        if ch == "P" and y <= 10:
            return "R"
        if ch in "WS":
            return "R" if ch == "W" else "r"
        return ch

    out = _pad(_recolor(grid, rule), DRAGON_HEADROOM)
    out = _paint(out, _SMALL_HORNS, 1, DRAGON_HEADROOM + 6)
    return out


def _dragon() -> dict[str, list[str]]:
    frames = {}
    for name in SITTING + CODING:
        frames[name] = _dragon_sitting(name, sprites.FRAMES[name])
    for name in LYING:
        frames[name] = _dragon_lying(name, sprites.FRAMES[name])
    frames["stretch"] = _dragon_stretch(sprites.FRAMES["stretch"])
    return frames


# ---- Wizard ------------------------------------------------------------------------------
# A tall black wizard's hat with a purple band and gold stars, and a wand with a sparkling tip.

WIZARD_HEADROOM = 9

_HAT = [              # its brim sits on the cat's forehead (base rows 2 and 3)
    "...........KKK......",
    "..........KBBK......",
    ".........KBbK.......",
    "........KBBbK.......",
    ".......KBYBbK.......",
    ".......KBBBbbK......",
    "......KBBBYBbK......",
    "......KBBBBBbK......",
    ".....KBYBBBBBbK.....",
    ".....KVVVVVVVVK.....",
    "KKKKKBBBBBBBBBBKKKK.",
    "KBBBBBBBBBBBBBBBBBK.",
    ".KKKKKKKKKKKKKKKKK..",
]
_WAND = [             # held up in the right paw; the white tip is where the sparkles come out
    "......G",
    ".....k.",
    "....k..",
    "...k...",
    "..k....",
    "KWWK...",
    "KWWK...",
    ".KK....",
]
WAND_X, WAND_Y = 12, 5   # where the wand goes, in plain-cat rows; its tip is at (WAND_X + 6, WAND_Y)
_TWINKLE_SMALL = [".Y.", "Y.Y", ".Y."]
_TWINKLE_BIG = ["..Y..", "..Y..", "YYGYY", "..Y..", "..Y.."]
_SMALL_HAT = [        # a sleepy, slumped version for when the cat is lying down
    "......KK",
    ".....KBK",
    "....KBYK",
    "...KBBbK",
    "..KBBBBbK",
    "KKVVVVVVKK",
    "KBBBBBBBBBK",
    ".KKKKKKKKK.",
]


def _wizard_sitting(frame: str, grid: list[str]) -> list[str]:
    out = _pad(grid, WIZARD_HEADROOM)
    out = _paint(out, _HAT, 0, WIZARD_HEADROOM + 3 - len(_HAT) + 1)
    if frame not in CODING:
        out = _with_wand(out, big=frame == "tail")  # every so often the wand sparkles
    return out


def _with_wand(grid: list[str], big: bool) -> list[str]:
    tip_x, tip_y = WAND_X + 6, WIZARD_HEADROOM + WAND_Y
    out = _paint(grid, _WAND, WAND_X, WIZARD_HEADROOM + WAND_Y)
    if big:
        return _paint(out, _TWINKLE_BIG, tip_x - 2, tip_y - 2)
    return _paint(out, _TWINKLE_SMALL, tip_x - 1, tip_y - 1)


def _wizard_lying(grid: list[str], head_top: int) -> list[str]:
    out = _pad(grid, WIZARD_HEADROOM)
    return _paint(out, _SMALL_HAT, 0, WIZARD_HEADROOM + head_top - len(_SMALL_HAT) + 2)


def _wizard() -> dict[str, list[str]]:
    frames = {}
    for name in SITTING + CODING:
        frames[name] = _wizard_sitting(name, sprites.FRAMES[name])
    for name in LYING:
        frames[name] = _wizard_lying(sprites.FRAMES[name], 9)
    frames["stretch"] = _wizard_lying(sprites.FRAMES["stretch"], 9)
    return frames


# ---- dressing up -------------------------------------------------------------------------

def _dragon_dress_up(dragon: dict[str, list[str]]) -> list[tuple[list[str], float]]:
    plain = _pad(sprites.FRAMES["idle"], DRAGON_HEADROOM)
    dressed = dragon["idle"]

    def pulled_up_to(row: int, base: list[str]) -> list[str]:
        """The suit pulled up as far as `row`: dragon below it, plain cat above."""
        return [d if y >= row else p for y, (p, d) in enumerate(zip(base, dressed))]

    looking_down = _pad(sprites.FRAMES["blink"], DRAGON_HEADROOM)
    hood_coming = _paint(pulled_up_to(DRAGON_HEADROOM + 10, plain), _HORNS, 0, -2)  # still above the head
    return [
        (_paint(_pad(sprites.FRAMES["look_up"], DRAGON_HEADROOM), _SPARKLES, 0, DRAGON_HEADROOM + 9), 0.5),
        (pulled_up_to(DRAGON_HEADROOM + 16, looking_down), 0.35),
        (pulled_up_to(DRAGON_HEADROOM + 13, looking_down), 0.35),
        (pulled_up_to(DRAGON_HEADROOM + 10, looking_down), 0.4),
        (hood_coming, 0.35),
        (dragon["blink"], 0.3),
        (_paint(dressed, _SPARKLES, 0, DRAGON_HEADROOM + 3), 0.45),
        (_paint(dressed, _SPARKLES, 0, DRAGON_HEADROOM + 1), 0.45),
        (dressed, 0.2),
    ]


def _wizard_dress_up(wizard: dict[str, list[str]]) -> list[tuple[list[str], float]]:
    plain = _pad(sprites.FRAMES["look_up"], WIZARD_HEADROOM)
    hat_on = _paint(plain, _HAT, 0, WIZARD_HEADROOM + 3 - len(_HAT) + 1)
    frames = []
    for drop, seconds in ((5, 0.3), (2, 0.22)):  # the hat floats down from above onto the cat's head
        falling = _paint(plain, _HAT, 0, WIZARD_HEADROOM + 3 - len(_HAT) + 1 - drop)
        if drop == 5:
            falling = _paint(falling, _TWINKLE_SMALL, 16, 2)
        frames.append((falling, seconds))
    squash = _pad(sprites.FRAMES["blink"], WIZARD_HEADROOM)
    frames.append((_paint(squash, _HAT, 0, WIZARD_HEADROOM + 3 - len(_HAT) + 1), 0.3))
    frames.append((_with_wand(hat_on, big=True), 0.45))
    frames.append((_with_wand(hat_on, big=False), 0.3))
    frames.append((wizard["tail"], 0.45))
    frames.append((wizard["idle"], 0.2))
    return frames


COSTUMES: dict[str, dict[str, list[str]]] = {
    "ginger": dict(sprites.FRAMES),
    "dragon": _dragon(),
    "wizard": _wizard(),
}
NAMES = {"ginger": "Ginger", "dragon": "Green Dragon", "wizard": "Wizard"}
DRESS_UP: dict[str, list[tuple[str, float]]] = {}

# Back to plain Ginger: a puff of sparkles and a happy blink.
_ginger_steps = [
    (_paint(sprites.FRAMES["look_up"], _SPARKLES, 0, 9), 0.45),
    (_paint(sprites.FRAMES["blink"], _SPARKLES, 0, 7), 0.35),
    (sprites.FRAMES["idle"], 0.2),
]
for _costume, _steps in (("ginger", _ginger_steps),
                         ("dragon", _dragon_dress_up(COSTUMES["dragon"])),
                         ("wizard", _wizard_dress_up(COSTUMES["wizard"]))):
    DRESS_UP[_costume] = []
    for _i, (_grid, _seconds) in enumerate(_steps):
        COSTUMES[_costume][f"dress_{_i}"] = _grid
        DRESS_UP[_costume].append((f"dress_{_i}", _seconds))


# ---- asking for a costume in the input bar --------------------------------------------------

ALIASES = {
    "dragon": "dragon", "green dragon": "dragon", "dragon costume": "dragon",
    "wizard": "wizard", "magician": "wizard", "wizard costume": "wizard", "magic cat": "wizard",
    "ginger": "ginger", "normal": "ginger", "yourself": "ginger", "a cat": "ginger", "cat": "ginger",
    "plain": "ginger", "no costume": "ginger", "regular": "ginger", "default": "ginger",
}
SAYS = {
    "dragon": "Rawr! I'm a dragon now. 🐉",
    "wizard": "Abracadabra! Wizard Ginger at your service. ✨",
    "ginger": "Back to plain old me. 🐾",
}
_ALIAS = "|".join(sorted((re.escape(a) for a in ALIASES), key=len, reverse=True))
_POLITE = r"(?:please\s+|can you\s+|could you\s+|now\s+|ginger,?\s+)*"
_END = r"(?:\s+(?:please|now|again))*\s*[.!?]*"
_RANDOM = re.compile(
    rf"^{_POLITE}(?:(?:change|switch|swap|new|random|another|different)\s+(?:your\s+|the\s+|a\s+)?costumes?"
    rf"(?:\s+(?:randomly|at random))?|random\s+costume|surprise me with a costume){_END}$")
_INTO = re.compile(
    rf"^{_POLITE}(?:(?:change|turn|switch|transform)\s+(?:back\s+)?(?:into|to)|dress\s+(?:up\s+)?as|"
    rf"(?:put on|wear)(?:\s+(?:the|your|a))?|be|become|go\s+back\s+to|back\s+to)\s+(?:a\s+|an\s+|the\s+|your\s+)?"
    rf"({_ALIAS})(?:\s+(?:costume|outfit|hat))?{_END}$")


def parse_request(text: str) -> str | None:
    """A costume from a short command like "change into dragon" or "change costume" (which gives
    "random"); None if the message is about something else, so it goes to the agent."""
    text = " ".join(text.lower().split())
    if len(text.split()) > 10:
        return None
    if _RANDOM.match(text):
        return "random"
    match = _INTO.match(text)
    return ALIASES[match.group(1)] if match else None


def pick(request: str, current: str) -> str:
    """Turn "random" into a real costume, never the one already on."""
    if request != "random":
        return request
    return random.choice([c for c in COSTUMES if c != current])


def height(costume: str) -> int:
    """Rows in this costume's frames: the plain cat's, plus room for horns or a hat."""
    return len(COSTUMES[costume]["idle"])


def render(costume: str, frame: str, scale: int) -> QPixmap:
    return sprites.render_grid(COSTUMES[costume][frame], scale)
