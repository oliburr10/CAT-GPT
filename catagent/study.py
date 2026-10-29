"""Study notes: the format Ginger writes them in, how they're checked, and the .tex export.

Notes read like a worked solution on a whiteboard, always in the same order:
  1. The question, and optionally a short answer to what the student is actually stuck on.
  2. Given: the definitions and facts you start from, each a formula with what it means, then the goal.
  3. Solution: every step is a derivation (formula, then the example written out) with an optional
     figure beside it, and says in words what it means.
  4. Write-up: the whole solution as you'd hand it in, plus the key idea and a common mistake.
  5. Optionally, for multiple choice, every option checked; and the final answer.

Formulas are LaTeX. Text fields are plain sentences that may contain $inline math$. Coloured ink ties
the formulas, the figures and the words together: \\blue{b_{ji}}, \\orange{a_{ij}}, \\green{(AB)_{ii}},
\\purple{...}, \\red{...}. \\hl{...} is a highlighter for the two or three results that matter most.
The Notepad (KaTeX) and the .tex export define them the same way.
"""

import re

# Ink colours, dark enough to read as text on white.
COLORS = {
    "blue": "2F6FDB",
    "orange": "C9760F",
    "green": "1E8A50",
    "purple": "7A4FD0",
    "red": "C23B32",
}
# Notes clipped before the colours were inks used these names; they still render.
OLD_COLORS = {"beige": "orange", "pink": "red"}
HIGHLIGHT = "FFE58F"
MAX_HIGHLIGHTS = 3

_TEXT = {"type": "string"}
_LATEX = {"type": "string", "description": "LaTeX, without surrounding $ signs."}

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Short title; may contain $inline math$."},
        "asked": {"type": "string", "description": "The question, as the user asked it."},
        "short_answer": {"type": "string", "description": "Optional: one or two sentences that answer what the "
                                                          "user is actually stuck on, before the full solution."},
        "colors": {
            "type": "array",
            "description": "What each highlight colour stands for, e.g. beige = entries of $A$.",
            "items": {
                "type": "object",
                "properties": {"color": {"type": "string", "enum": list(COLORS)}, "meaning": _TEXT},
                "required": ["color", "meaning"],
            },
        },
        "have": {
            "type": "array",
            "description": "What you have: the definitions and facts to start from.",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "description": "A short tag like D1, D2."},
                    "formula": _LATEX,
                    "meaning": _TEXT,
                },
                "required": ["label", "formula", "meaning"],
            },
        },
        "goal": {
            "type": "object",
            "properties": {"formula": _LATEX, "meaning": _TEXT},
            "required": ["formula", "meaning"],
        },
        "example": {"type": "string", "description": "The small concrete example the pictures use, if any."},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": _TEXT,
                    "uses": {"type": "string", "description": "Which facts or steps it uses, e.g. (D3) with k = i."},
                    "formula": _LATEX,
                    "picture": {"type": "string", "description": "Optional LaTeX figure, e.g. coloured matrices or a table."},
                    "caption": {"type": "string", "description": "Optional: one sentence under the figure."},
                    "expansion": {"type": "string", "description": "Optional LaTeX: the formula written out for the example."},
                    "meaning": _TEXT,
                },
                "required": ["title", "uses", "formula", "meaning"],
            },
        },
        "solution": {
            "type": "object",
            "properties": {
                "intro": _TEXT,
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"text": _TEXT, "formula": _LATEX},
                        "required": ["text"],
                    },
                },
                "key_idea": _TEXT,
                "watch_out": _TEXT,
            },
            "required": ["steps", "key_idea"],
        },
        "options": {
            "type": "array",
            "description": "Only for multiple choice: every option, what it really computes and why it is right or wrong.",
            "items": {
                "type": "object",
                "properties": {
                    "option": {"type": "string", "description": "The letter, e.g. A."},
                    "computes": _LATEX,
                    "value": {"type": "string", "description": "Optional: its value with the problem's numbers."},
                    "verdict": _TEXT,
                    "correct": {"type": "boolean"},
                },
                "required": ["option", "computes", "verdict", "correct"],
            },
        },
        "answer": {"type": "string", "description": "Optional LaTeX: the final answer in one line."},
    },
    "required": ["title", "asked", "have", "goal", "steps", "solution"],
}

RULES = """\
Study mode. When {user} wants to understand, learn, solve or prove something (maths, physics, \
statistics, any worked problem), don't explain it in your speech cloud: write study notes with \
write_study_notes, which opens them in the Notepad. Then reply with one short sentence.

The notes read like a worked solution on a classroom whiteboard, so {user} learns it rather than \
just seeing an answer:
- If {user} says what they're stuck on, answer exactly that first in short_answer, in one or two sentences.
- Given (have): every definition or fact the problem gives or needs, written as a formula, each \
with a plain-words meaning. The goal goes only in goal, not in have.
- Solve it step by step. Each step is one move: a formula that follows from the facts or earlier \
steps (say which in uses), the example written out in expansion, and what it means in plain words. \
Prefer a few clear steps over many tiny ones. Line derivations up with \\begin{{aligned}} ... &= ... \\end{{aligned}}.
- Use one small concrete example and continue the same figure (picture) through the steps, e.g. \
coloured matrices in a bmatrix or a small table, each with a one-sentence caption.
- Colour is ink, used for ideas: pick one colour per idea (say what each means in colors) and use \
it for that idea everywhere, in formulas, figures and text: \\blue{{...}}, \\orange{{...}}, \
\\green{{...}}, \\purple{{...}}, \\red{{...}}. In text, colour inside math, e.g. $\\orange{{\\text{{row }} i}}$.
- Highlight with \\hl{{...}} only the two or three results that matter most (at most three), never decoration.
- Finish with the write-up (solution): the whole solution as {user} would hand it in, in numbered \
steps, plus the key idea and a common mistake to watch out for.
- Multiple choice: fill options with every option, what it really computes (rewritten in the \
problem's own notation), its value if the numbers allow, and why it's right or wrong. Put the \
final result in answer.
- No quizzes or questions for {user} to answer. Text fields are plain sentences, and every bit of \
maths in them goes inside $...$ (write $(AB)_{{ii}}$, never (AB)_{{ii}}); no Markdown. Formulas, \
figures and expansions are LaTeX without $ signs, KaTeX-compatible.
- If {user} asks a follow-up about notes from the Notepad, either answer in one or two sentences, \
or, if a step needs more explaining, call write_study_notes again with the improved notes.
"""


def problems(notes: dict) -> list[str]:
    """What's wrong with a set of notes, in words the model can act on. Empty means fine."""
    found = []

    def text(value, where, verbatim=False):
        if not isinstance(value, str) or not value.strip():
            found.append(f"{where} must be a non-empty string.")
            return
        if verbatim:
            return  # the user's own words, shown as they typed them
        if value.count("$") % 2:
            found.append(f"{where} has an unmatched $.")
        else:
            outside = "".join(re.split(r"\$[^$]*\$", value))
            loose = re.search(r"\\[A-Za-z]+|[_^]\{", outside)
            if loose:
                found.append(f"{where} has LaTeX outside $...$ (near {loose.group()!r}): wrap every bit of maths in $...$.")
        _check_colors(value, where)

    def latex(value, where, optional=False):
        if optional and (value is None or value == ""):
            return
        if not isinstance(value, str) or not value.strip():
            found.append(f"{where} must be a non-empty LaTeX string.")
            return
        if value.strip().startswith("$"):
            found.append(f"{where} is a formula: leave out the $ signs.")
        depth = 0
        for ch in re.sub(r"\\[{}]", "", value):
            depth += {"{": 1, "}": -1}.get(ch, 0)
            if depth < 0:
                break
        if depth:
            found.append(f"{where} has unbalanced braces.")
        _check_colors(value, where)

    def _check_colors(value, where):
        for name in re.findall(r"\\(\w+)\{", value):
            if name in OLD_COLORS or name in ("yellow", "gray", "grey", "teal", "cyan", "black"):
                found.append(f"{where} uses \\{name}, but the colours are {', '.join(COLORS)}.")
            elif name in COLORS:
                used.add(name)
        highlights[0] += value.count("\\hl{")

    def items(value, where, minimum=1):
        if not isinstance(value, list) or len(value) < minimum or not all(isinstance(v, dict) for v in value):
            found.append(f"{where} must be a list of at least {minimum} object(s).")
            return []
        return value

    if not isinstance(notes, dict):
        return ["The notes must be a JSON object."]
    used: set[str] = set()
    highlights = [0]
    text(notes.get("title"), "title")
    text(notes.get("asked"), "asked", verbatim=True)
    if notes.get("short_answer"):
        text(notes["short_answer"], "short_answer")
    for i, c in enumerate(items(notes.get("colors", []), "colors", minimum=0), 1):
        if c.get("color") not in COLORS:
            found.append(f"colors[{i}].color must be one of {', '.join(COLORS)}.")
        text(c.get("meaning"), f"colors[{i}].meaning")
    for i, h in enumerate(items(notes.get("have"), "have"), 1):
        text(h.get("label"), f"have[{i}].label")
        if str(h.get("label", "")).strip("() ").lower() == "goal":
            found.append(f"have[{i}] is the goal: put it only in goal, not in have.")
        latex(h.get("formula"), f"have[{i}].formula")
        text(h.get("meaning"), f"have[{i}].meaning")
    goal = notes.get("goal")
    if isinstance(goal, dict):
        latex(goal.get("formula"), "goal.formula")
        text(goal.get("meaning"), "goal.meaning")
    else:
        found.append("goal must be an object with formula and meaning.")
    if notes.get("example"):
        text(notes["example"], "example")
    for i, s in enumerate(items(notes.get("steps"), "steps"), 1):
        text(s.get("title"), f"steps[{i}].title")
        text(s.get("uses"), f"steps[{i}].uses")
        latex(s.get("formula"), f"steps[{i}].formula")
        latex(s.get("picture"), f"steps[{i}].picture", optional=True)
        latex(s.get("expansion"), f"steps[{i}].expansion", optional=True)
        if s.get("caption"):
            text(s["caption"], f"steps[{i}].caption")
        text(s.get("meaning"), f"steps[{i}].meaning")
    solution = notes.get("solution")
    if isinstance(solution, dict):
        if solution.get("intro"):
            text(solution["intro"], "solution.intro")
        for i, s in enumerate(items(solution.get("steps"), "solution.steps"), 1):
            text(s.get("text"), f"solution.steps[{i}].text")
            latex(s.get("formula"), f"solution.steps[{i}].formula", optional=True)
        text(solution.get("key_idea"), "solution.key_idea")
        if solution.get("watch_out"):
            text(solution["watch_out"], "solution.watch_out")
    else:
        found.append("solution must be an object with steps and key_idea.")
    if notes.get("options"):
        rows = items(notes["options"], "options", minimum=2)
        for i, o in enumerate(rows, 1):
            text(o.get("option"), f"options[{i}].option")
            latex(o.get("computes"), f"options[{i}].computes")
            text(o.get("verdict"), f"options[{i}].verdict")
            if not isinstance(o.get("correct"), bool):
                found.append(f"options[{i}].correct must be true or false.")
        if rows and sum(o.get("correct") is True for o in rows) != 1:
            found.append("options must mark exactly one option as correct.")
    latex(notes.get("answer"), "answer", optional=True)
    if highlights[0] > MAX_HIGHLIGHTS:
        found.append(f"\\hl is used {highlights[0]} times. Highlight at most {MAX_HIGHLIGHTS} key results, so they stand out.")
    explained = {c.get("color") for c in notes.get("colors", []) if isinstance(c, dict)}
    for name in sorted(used - explained):
        found.append(f"\\{name} is used, but colors doesn't say what {name} stands for. Add it, or don't use it.")
    return found


# ---- LaTeX export -------------------------------------------------------------------------

# Maths symbols people type straight into a question ("A ∈ ℝ^{n×m}"). KaTeX shows them as they
# are; pdflatex needs to be told what they mean.
UNICODE_MATH = {
    "−": r"-", "∈": r"\in", "∉": r"\notin", "×": r"\times", "·": r"\cdot", "÷": r"\div", "±": r"\pm",
    "≤": r"\leq", "≥": r"\geq", "≠": r"\neq", "≈": r"\approx", "≡": r"\equiv", "∞": r"\infty",
    "→": r"\to", "←": r"\leftarrow", "⇒": r"\Rightarrow", "⟹": r"\implies", "⇔": r"\Leftrightarrow",
    "∀": r"\forall", "∃": r"\exists", "∑": r"\sum", "∏": r"\prod", "∫": r"\int", "√": r"\surd",
    "∂": r"\partial", "∇": r"\nabla", "⊂": r"\subset", "⊆": r"\subseteq", "∪": r"\cup", "∩": r"\cap",
    "∅": r"\emptyset", "ℝ": r"\mathbb{R}", "ℕ": r"\mathbb{N}", "ℤ": r"\mathbb{Z}", "ℚ": r"\mathbb{Q}",
    "ℂ": r"\mathbb{C}", "′": r"'", "∘": r"\circ", "⊗": r"\otimes", "⊕": r"\oplus", "∎": r"\blacksquare",
    **{chr(0x3B1 + i): "\\" + name for i, name in enumerate([
        "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda",
        "mu", "nu", "xi", "", "pi", "rho", "", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega",
    ]) if name},  # α to ω; omicron and final sigma are plain letters
    **dict(zip("ΓΔΘΛΞΠΣΦΨΩ", [r"\Gamma", r"\Delta", r"\Theta", r"\Lambda", r"\Xi", r"\Pi", r"\Sigma",
                               r"\Phi", r"\Psi", r"\Omega"])),
}

def _tex_text(value: str) -> str:
    """Escape a text field for LaTeX, leaving its $math$ alone."""
    parts = re.split(r"(\$[^$]*\$)", value or "")
    out = []
    for part in parts:
        if part.startswith("$") and part.endswith("$") and len(part) > 1:
            out.append(part)
        else:
            for ch, rep in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"),
                            ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                            ("^", r"\textasciicircum{}")):
                part = part.replace(ch, rep)
            out.append(part)
    return "".join(out)


def to_tex(notes: dict) -> str:
    """The notes as a standalone LaTeX document, laid out like the Notepad, colours included."""
    t = _tex_text
    lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[margin=2.5cm]{geometry}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{amsmath,amssymb,xcolor,booktabs}",
        r"\setlength{\fboxsep}{2pt}",
    ]
    for char, command in UNICODE_MATH.items():
        lines.append(rf"\DeclareUnicodeCharacter{{{ord(char):04X}}}{{\ensuremath{{{command}}}}}")
    for name, hex_code in COLORS.items():
        lines.append(rf"\definecolor{{note{name}}}{{HTML}}{{{hex_code}}}")
        lines.append(rf"\newcommand{{\{name}}}[1]{{{{\color{{note{name}}}#1}}}}")
    for old, new in OLD_COLORS.items():
        lines.append(rf"\newcommand{{\{old}}}[1]{{\{new}{{#1}}}}")
    lines += [
        rf"\definecolor{{notehl}}{{HTML}}{{{HIGHLIGHT}}}",
        r"\newcommand{\hl}[1]{\colorbox{notehl}{$\displaystyle #1$}}",
        r"\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}",
        rf"\title{{{t(notes['title'])}}}",
        r"\date{}",
        r"\begin{document}",
        r"\maketitle",
        rf"\textbf{{Question.}} {t(notes['asked'])}",
    ]
    if notes.get("short_answer"):
        lines.append(rf"\textbf{{Short answer.}} {t(notes['short_answer'])}")
    if notes.get("colors"):
        lines.append(r"\textbf{Colours.} " + "; ".join(
            rf"$\{c['color']}{{\blacksquare}}$ {t(c['meaning'])}" for c in notes["colors"]) + ".")
    lines.append(r"\section*{Given}")
    lines.append(r"\begin{description}")
    for h in notes["have"]:
        lines.append(rf"\item[({t(h['label'])})] $\displaystyle {h['formula']}$\\ {t(h['meaning'])}")
    lines.append(rf"\item[To show.] $\displaystyle {notes['goal']['formula']}$\\ {t(notes['goal']['meaning'])}")
    lines.append(r"\end{description}")
    lines.append(r"\section*{Solution}")
    if notes.get("example"):
        lines.append(t(notes["example"]))
    figure = 0
    for i, s in enumerate(notes["steps"], 1):
        lines.append(rf"\subsection*{{Step {i}.\quad {t(s['title'])}}}")
        lines.append(rf"\emph{{Uses {t(s['uses'])}.}}")
        lines.append(rf"\[ {s['formula']} \]")
        if s.get("expansion"):
            lines.append(rf"\[ {s['expansion']} \]")
        if s.get("picture"):
            figure += 1
            caption = rf" {t(s['caption'])}" if s.get("caption") else ""
            lines.append(rf"\begin{{center}}$\displaystyle {s['picture']}$\\[4pt] \small\textbf{{Figure {figure}.}}{caption}\end{{center}}")
        lines.append(t(s["meaning"]))
    sol = notes["solution"]
    lines.append(r"\section*{Write-up}")
    if sol.get("intro"):
        lines.append(t(sol["intro"]))
    lines.append(r"\begin{enumerate}")
    for s in sol["steps"]:
        lines.append(rf"\item {t(s['text'])}" + (rf" \[ {s['formula']} \]" if s.get("formula") else ""))
    lines.append(r"\end{enumerate}")
    lines.append(rf"\textbf{{Key idea.}} {t(sol['key_idea'])}")
    if sol.get("watch_out"):
        lines.append("\n" + rf"\textbf{{Watch out.}} {t(sol['watch_out'])}")
    if notes.get("options"):
        lines.append(r"\section*{Every option}")
        lines.append(r"\begin{tabular}{lllp{6.5cm}}\toprule Option & Computes & Value & Verdict \\ \midrule")
        for o in notes["options"]:
            mark = r"$\green{\checkmark}$" if o.get("correct") else ""
            lines.append(rf"{t(o['option'])} {mark} & ${o['computes']}$ & {t(o.get('value', ''))} & {t(o['verdict'])} \\")
        lines.append(r"\bottomrule\end{tabular}")
    if notes.get("answer"):
        lines.append(r"\section*{Answer}")
        lines.append(rf"\[ {notes['answer']} \]")
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"
