"""Study notes: the format Ginger writes them in, how they're checked, and the .tex export.

Notes always teach in the same order:
  1. What you have: the definitions and facts you start from, each as a formula with what it means.
  2. Solve it step by step: every step starts from a formula, continues the picture, and says what it means.
  3. Complete solution: the whole solution in one box, step by step.

Formulas are LaTeX. Text fields are plain sentences that may contain $inline math$. Colour
highlights tie the formulas, the pictures and the words together: \\beige{a_{ij}}, \\blue{b_{ji}},
\\green{(AB)_{ii}}, \\purple{...}, \\pink{...}. The Notepad (KaTeX) and the .tex export define them the same way.
"""

import re

COLORS = {
    "beige": "FDE7D3",
    "blue": "DCE8FB",
    "green": "E3F2E7",
    "purple": "EBE3FB",
    "pink": "FBE3EC",
}

_TEXT = {"type": "string"}
_LATEX = {"type": "string", "description": "LaTeX, without surrounding $ signs."}

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Short title; may contain $inline math$."},
        "asked": {"type": "string", "description": "The question, as the user asked it."},
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
                    "picture": {"type": "string", "description": "Optional LaTeX illustration, e.g. coloured matrices."},
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
    },
    "required": ["title", "asked", "have", "goal", "steps", "solution"],
}

RULES = """\
Study mode. When {user} wants to understand, learn, solve or prove something (maths, physics, \
statistics, any worked problem), don't explain it in your speech cloud: write study notes with \
write_study_notes, which opens them in the Notepad. Then reply with one short sentence.

How to write the notes, so {user} learns it rather than just seeing an answer:
- Start with what you have: every definition or fact the problem gives or needs, written as a \
formula, each with a plain-words meaning. The goal goes only in goal, not in have.
- Solve it step by step. Every step starts from a formula, says which facts or earlier steps it \
uses, and ends with what it means in plain words. Prefer a few clear steps over many tiny ones.
- Use one small concrete example (like n = 2, m = 3) and continue the same picture through the \
steps, e.g. coloured matrices in a bmatrix, so each step visibly builds on the last.
- Colour consistently: pick one colour per idea (say what each means in colors) and use that \
colour for that idea everywhere: in the formulas, in the pictures and in the text, with \
\\beige{{...}}, \\blue{{...}}, \\green{{...}}, \\purple{{...}}, \\pink{{...}}. For example, if beige \
means "entries of A", every entry of A is beige, in every step. In text, colour inside math, \
e.g. $\\beige{{\\text{{row }} i \\text{{ of }} A}}$.
- Finish with the complete solution, written properly, in numbered steps, plus the key idea and \
a common mistake to watch out for.
- No quizzes or questions for {user} to answer. Text fields are plain sentences, and every bit of \
maths in them goes inside $...$ (write $(AB)_{{ii}}$, never (AB)_{{ii}}); no Markdown. Formulas, \
pictures and expansions are LaTeX without $ signs, KaTeX-compatible.
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
            if name in ("red", "orange", "yellow", "gray", "grey", "teal", "cyan"):
                found.append(f"{where} uses \\{name}, but the colours are {', '.join(COLORS)}.")
            elif name in COLORS:
                used.add(name)

    def items(value, where, minimum=1):
        if not isinstance(value, list) or len(value) < minimum or not all(isinstance(v, dict) for v in value):
            found.append(f"{where} must be a list of at least {minimum} object(s).")
            return []
        return value

    if not isinstance(notes, dict):
        return ["The notes must be a JSON object."]
    used: set[str] = set()
    text(notes.get("title"), "title")
    text(notes.get("asked"), "asked", verbatim=True)
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
    explained = {c.get("color") for c in notes.get("colors", []) if isinstance(c, dict)}
    for name in sorted(used - explained):
        found.append(f"\\{name} is used, but colors doesn't say what {name} stands for. Add it, or don't use it.")
    return found


# ---- LaTeX export -------------------------------------------------------------------------

# Maths symbols people type straight into a question ("A ∈ ℝ^{n×m}"). KaTeX shows them as they
# are; pdflatex needs to be told what they mean.
UNICODE_MATH = {
    "∈": r"\in", "∉": r"\notin", "×": r"\times", "·": r"\cdot", "÷": r"\div", "±": r"\pm",
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
    """The notes as a standalone LaTeX document, colours included."""
    t = _tex_text
    lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[margin=2.5cm]{geometry}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{amsmath,amssymb,xcolor}",
        r"\setlength{\fboxsep}{1.5pt}",
    ]
    for char, command in UNICODE_MATH.items():
        lines.append(rf"\DeclareUnicodeCharacter{{{ord(char):04X}}}{{\ensuremath{{{command}}}}}")
    for name, hex_code in COLORS.items():
        lines.append(rf"\definecolor{{note{name}}}{{HTML}}{{{hex_code}}}")
        lines.append(rf"\newcommand{{\{name}}}[1]{{\colorbox{{note{name}}}{{$#1$}}}}")
    lines += [
        r"\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}",
        rf"\title{{{t(notes['title'])}}}",
        r"\date{}",
        r"\begin{document}",
        r"\maketitle",
        rf"\textbf{{You asked.}} {t(notes['asked'])}",
    ]
    if notes.get("colors"):
        lines.append(r"\textbf{Colours.} " + "; ".join(
            rf"\{c['color']}{{\phantom{{x}}}} {t(c['meaning'])}" for c in notes["colors"]) + ".")
    lines.append(r"\section*{1\quad What you have}")
    lines.append(r"\begin{description}")
    for h in notes["have"]:
        lines.append(rf"\item[({t(h['label'])})] $\displaystyle {h['formula']}$\\ {t(h['meaning'])}")
    lines.append(rf"\item[Goal] $\displaystyle {notes['goal']['formula']}$\\ {t(notes['goal']['meaning'])}")
    lines.append(r"\end{description}")
    lines.append(r"\section*{2\quad Solve it step by step}")
    if notes.get("example"):
        lines.append(t(notes["example"]))
    for i, s in enumerate(notes["steps"], 1):
        lines.append(rf"\subsection*{{Step {i}: {t(s['title'])}}}")
        lines.append(rf"\emph{{Uses {t(s['uses'])}.}}")
        lines.append(rf"\[ {s['formula']} \]")
        if s.get("picture"):
            lines.append(rf"\[ {s['picture']} \]")
        if s.get("expansion"):
            lines.append(rf"\[ {s['expansion']} \]")
        lines.append(rf"\textbf{{What it means:}} {t(s['meaning'])}")
    sol = notes["solution"]
    lines.append(r"\section*{3\quad Complete solution}")
    lines.append(r"\fbox{\begin{minipage}{0.95\linewidth}")
    if sol.get("intro"):
        lines.append(t(sol["intro"]))
    lines.append(r"\begin{enumerate}")
    for s in sol["steps"]:
        lines.append(rf"\item {t(s['text'])}" + (rf" \[ {s['formula']} \]" if s.get("formula") else ""))
    lines.append(r"\end{enumerate}")
    lines.append(rf"\textbf{{Key idea:}} {t(sol['key_idea'])}")
    if sol.get("watch_out"):
        lines.append("\n" + rf"\textbf{{Watch out:}} {t(sol['watch_out'])}")
    lines.append(r"\end{minipage}}")
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"
