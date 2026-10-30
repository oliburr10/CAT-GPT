"""Study notes: the format Ginger writes them in, how they're checked, and the .tex export.

Notes get to the point first, then show every tool before using it:
  1. The problem, and the answer straight away: the result and the key insight.
  2. Given and Find: what you have, and exactly what you must find or show.
  3. Methods: every concept, definition or formula the solution uses (M1, M2, ...), with what
     it says and why it applies here. Nothing is used that isn't listed.
  4. Plan: the route from Given to Find in a sentence or two.
  5. Solution: blocks named after what they work out ("Speed at the edge"), never "Step 1".
     Each names the methods it uses, shows the derivation, explains it and ends in a result.
     A block may carry a figure.
  6. Checks, the takeaways (key idea, common mistakes), and the exam version to hand in.
  For multiple choice, every option is checked too.

Formulas are LaTeX. Text fields are plain sentences that may contain $inline math$. Coloured ink ties
the formulas, the figures and the words together: \\blue{b_{ji}}, \\orange{a_{ij}}, \\green{(AB)_{ii}},
\\purple{...}, \\red{...}. \\hl{...} is a highlighter for the two or three results that matter most.
The Notepad (KaTeX) and the .tex export define them the same way.

Notes written in the earlier format (have, goal, steps) still open: upgrade() converts them.
"""

import re

from . import figures
from .palette import COLORS, HIGHLIGHT, OLD_COLORS

MAX_HIGHLIGHTS = 3

_TEXT = {"type": "string"}
_LATEX = {"type": "string", "description": "LaTeX, without surrounding $ signs."}

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Short title; may contain $inline math$."},
        "asked": {"type": "string", "description": "The question, as the user asked it."},
        "answer": {
            "type": "object",
            "description": "The answer, straight away.",
            "properties": {
                "result": {**_LATEX, "description": "The final result in one line of LaTeX."},
                "text": {**_TEXT, "description": "One or two sentences: the key insight, or exactly what the user is stuck on."},
            },
            "required": ["result", "text"],
        },
        "colors": {
            "type": "array",
            "description": "What each ink colour stands for, e.g. orange = entries of $A$.",
            "items": {
                "type": "object",
                "properties": {"color": {"type": "string", "enum": list(COLORS)}, "meaning": _TEXT},
                "required": ["color", "meaning"],
            },
        },
        "given": {
            "type": "array",
            "description": "Everything the problem gives: quantities, data, assumptions.",
            "items": {
                "type": "object",
                "properties": {
                    "symbol": {**_LATEX, "description": "e.g. h_1, or A \\in \\mathbb{R}^{n\\times m}."},
                    "value": {**_LATEX, "description": "Optional, e.g. 0.0500\\ \\text{m}."},
                    "meaning": _TEXT,
                },
                "required": ["symbol", "meaning"],
            },
        },
        "find": {
            "type": "object",
            "description": "Exactly what must be found or shown.",
            "properties": {"formula": _LATEX, "meaning": _TEXT},
            "required": ["formula", "meaning"],
        },
        "methods": {
            "type": "array",
            "description": "Every concept, definition, theorem or formula the solution uses.",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "M1, M2, ... in the order they are first used."},
                    "name": {"type": "string", "description": "e.g. Energy conservation."},
                    "formula": _LATEX,
                    "says": {**_TEXT, "description": "What the formula says, in plain words, with what each symbol means."},
                    "why": {**_TEXT, "description": "Why it applies to this problem, or when to reach for it."},
                },
                "required": ["id", "name", "formula", "says", "why"],
            },
        },
        "plan": {**_TEXT, "description": "The route from given to find in one or two sentences, naming the methods."},
        "solution": {
            "type": "array",
            "description": "The worked solution, in blocks.",
            "items": {
                "type": "object",
                "properties": {
                    "title": {**_TEXT, "description": "What this block works out, e.g. Speed at the edge. Never Step 1."},
                    "uses": {"type": "array", "items": {"type": "string"}, "description": "Method ids, e.g. [\"M2\"]."},
                    "work": {**_LATEX, "description": "The derivation, lined up at = with \\begin{aligned}."},
                    "expansion": {**_LATEX, "description": "Optional: the same written out for the example or numbers."},
                    "result": {**_LATEX, "description": "What this block found, in one line."},
                    "explain": {**_TEXT, "description": "One or two sentences: what happened and why."},
                    "picture": {**_LATEX, "description": "Optional LaTeX figure, e.g. coloured matrices or a table."},
                    "figure": figures.SCHEMA,
                    "caption": {**_TEXT, "description": "Optional: one sentence under the figure."},
                },
                "required": ["title", "uses", "work", "result", "explain"],
            },
        },
        "checks": {"type": "array", "items": _TEXT, "description": "Quick ways to see the answer is right."},
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
        "takeaways": {
            "type": "object",
            "properties": {
                "key_idea": {**_TEXT, "description": "The one idea to remember."},
                "mistakes": {"type": "array", "items": _TEXT, "description": "Common mistakes, and how to avoid them."},
            },
            "required": ["key_idea", "mistakes"],
        },
        "exam": {
            "type": "array",
            "description": "The clean solution as the user would hand it in.",
            "items": {"type": "object", "properties": {"text": _TEXT, "formula": _LATEX}, "required": ["text"]},
        },
    },
    "required": ["title", "asked", "answer", "given", "find", "methods", "plan", "solution", "takeaways", "exam"],
}

RULES = """\
Study mode. When {user} wants to understand, learn, solve or prove something (maths, physics, \
statistics, biology, any worked problem), don't explain it in your speech cloud: write study notes \
with write_study_notes, which opens them in the Notepad. Then reply with one short sentence.

The notes get to the point at once and explain every tool before it is used:
- answer: the final result first, in one line (result), and one or two sentences on the key \
insight (text). If {user} says what they're stuck on, answer exactly that here.
- given: everything the problem gives, each as a symbol, its value if it has one, and what it \
means. find: exactly what must be found or shown.
- methods: every concept, definition, theorem or formula the solution uses, one per entry, \
M1, M2, ... in the order they are first used: its name, the formula, what it says in plain words \
with what each symbol means (says), and why it applies to this problem (why). The solution may \
use nothing that isn't listed, and every method must be used.
- plan: the route from given to find in one or two sentences, naming the methods.
- solution: blocks in order. Title each block by what it works out ("Speed at the edge", "The \
trace of AB"), never "Step 1". List the methods it uses (uses, e.g. ["M2", "M3"]), show the work \
as a derivation lined up at the = signs with \\begin{{aligned}} ... &= ... \\end{{aligned}}, give its \
result in one line, and explain in one or two sentences what happened and why. Prefer a few \
substantial blocks over many tiny ones. Optional: expansion (the same with the numbers or a \
small example), and a figure: either picture (LaTeX: coloured matrices, a small table) or \
figure, which the Notepad draws itself, each with a one-sentence caption.
  - figure type rna, for anything about RNA folding (riboswitches, attenuators, hairpins, \
tRNA): the sequence, one or more folds in dot-bracket (each with a name, a note and whether the \
ligand is bound), coloured regions (e.g. the SD in orange) and the ligand with the bases around \
its pocket. The Notepad animates between the folds. Pairs must be A-U, G-C or G-U; design a short \
model sequence if you don't know a real one, and say so in the caption.
  - figure type molecule, for a real 3D structure: a PDB ID you are certain of, residues to \
highlight with labels, and the ligand's residue name. Never guess a PDB ID.
  - figure type sampler, for MCMC, Metropolis-Hastings, Gibbs sampling or the Ising model: \
model ising, the lattice size (8 to 40) and the coupling theta (about 0.3 shows domains). The \
Notepad runs Gibbs and Gibbs-With-Gradients side by side, live, with the proposal as a heat map.
- checks: quick ways to see the answer is right: units, a limit or special case, a number.
- takeaways: the key idea in one sentence, and the common mistakes with how to avoid them.
- exam: the clean solution as {user} would hand it in, in a few numbered lines.
- Multiple choice: fill options with every option, what it really computes (rewritten in the \
problem's own notation), its value if the numbers allow, and why it's right or wrong.
- Colour is ink, used for ideas: pick one colour per idea (say what each means in colors) and use \
it for that idea everywhere, in formulas, figures and text: \\blue{{...}}, \\orange{{...}}, \
\\green{{...}}, \\purple{{...}}, \\red{{...}}. In text, colour inside math, e.g. $\\orange{{\\text{{row }} i}}$. \
Highlight with \\hl{{...}} only the two or three results that matter most (at most three).
- No quizzes or questions for {user} to answer. Text fields are plain sentences, and every bit of \
maths in them goes inside $...$ (write $(AB)_{{ii}}$, never (AB)_{{ii}}); no Markdown. Formulas, \
figures and expansions are LaTeX without $ signs, KaTeX-compatible.
- If {user} asks a follow-up about notes from the Notepad, either answer in one or two sentences, \
or, if a block needs more explaining, call write_study_notes again with the improved notes.
"""

_METHOD_ID = re.compile(r"M[1-9]\d*")


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

    def obj(value, where, keys):
        if not isinstance(value, dict):
            found.append(f"{where} must be an object with {' and '.join(keys)}.")
            return {}
        return value

    if not isinstance(notes, dict):
        return ["The notes must be a JSON object."]
    used: set[str] = set()
    highlights = [0]
    text(notes.get("title"), "title")
    text(notes.get("asked"), "asked", verbatim=True)

    answer = obj(notes.get("answer"), "answer", ["result", "text"])
    if answer:
        latex(answer.get("result"), "answer.result")
        text(answer.get("text"), "answer.text")

    for i, c in enumerate(items(notes.get("colors", []), "colors", minimum=0), 1):
        if c.get("color") not in COLORS:
            found.append(f"colors[{i}].color must be one of {', '.join(COLORS)}.")
        text(c.get("meaning"), f"colors[{i}].meaning")

    for i, g in enumerate(items(notes.get("given"), "given"), 1):
        latex(g.get("symbol"), f"given[{i}].symbol")
        latex(g.get("value"), f"given[{i}].value", optional=True)
        text(g.get("meaning"), f"given[{i}].meaning")

    find = obj(notes.get("find"), "find", ["formula", "meaning"])
    if find:
        latex(find.get("formula"), "find.formula")
        text(find.get("meaning"), "find.meaning")

    ids = []
    for i, m in enumerate(items(notes.get("methods"), "methods"), 1):
        mid = m.get("id")
        if not isinstance(mid, str) or not _METHOD_ID.fullmatch(mid):
            found.append(f"methods[{i}].id must be M1, M2, ... (got {mid!r}).")
        elif mid in ids:
            found.append(f"methods[{i}].id {mid} is used twice.")
        else:
            ids.append(mid)
        text(m.get("name"), f"methods[{i}].name")
        latex(m.get("formula"), f"methods[{i}].formula")
        text(m.get("says"), f"methods[{i}].says")
        text(m.get("why"), f"methods[{i}].why")

    text(notes.get("plan"), "plan")

    cited = set()
    for i, b in enumerate(items(notes.get("solution"), "solution"), 1):
        at = f"solution[{i}]"
        text(b.get("title"), f"{at}.title")
        if isinstance(b.get("title"), str) and re.match(r"\s*(step|part)\s*\d", b["title"], re.I):
            found.append(f"{at}.title starts with a step number: name what the block works out instead, "
                         f"e.g. Speed at the edge.")
        uses = b.get("uses")
        if not isinstance(uses, list) or not uses or not all(isinstance(u, str) for u in uses):
            found.append(f"{at}.uses must list the methods it uses, e.g. [\"M1\"].")
        else:
            for u in uses:
                if u not in ids:
                    found.append(f"{at}.uses {u}, but there is no method {u}: add it to methods.")
                cited.add(u)
        latex(b.get("work"), f"{at}.work")
        latex(b.get("expansion"), f"{at}.expansion", optional=True)
        latex(b.get("result"), f"{at}.result")
        text(b.get("explain"), f"{at}.explain")
        latex(b.get("picture"), f"{at}.picture", optional=True)
        if b.get("caption"):
            text(b["caption"], f"{at}.caption")
        if b.get("figure") is not None:
            found.extend(figures.problems(b["figure"], f"{at}.figure"))
            if b.get("picture"):
                found.append(f"{at} has both picture and figure: keep one.")
            states = b["figure"].get("states") if isinstance(b["figure"], dict) else None
            for k, st in enumerate(states or [], 1):
                if isinstance(st, dict) and isinstance(st.get("note"), str):
                    text(st["note"], f"{at}.figure.states[{k}].note")
    for mid in ids:
        if mid not in cited:
            found.append(f"{mid} is never used in the solution: use it in a block's uses, or leave it out.")

    for i, c in enumerate(notes.get("checks") or [], 1):
        text(c, f"checks[{i}]")

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

    take = obj(notes.get("takeaways"), "takeaways", ["key_idea", "mistakes"])
    if take:
        text(take.get("key_idea"), "takeaways.key_idea")
        mistakes = take.get("mistakes")
        if not isinstance(mistakes, list) or not mistakes:
            found.append("takeaways.mistakes must list at least one common mistake.")
        else:
            for i, m in enumerate(mistakes, 1):
                text(m, f"takeaways.mistakes[{i}]")

    for i, e in enumerate(items(notes.get("exam"), "exam"), 1):
        text(e.get("text"), f"exam[{i}].text")
        latex(e.get("formula"), f"exam[{i}].formula", optional=True)

    if highlights[0] > MAX_HIGHLIGHTS:
        found.append(f"\\hl is used {highlights[0]} times. Highlight at most {MAX_HIGHLIGHTS} key results, so they stand out.")
    explained = {c.get("color") for c in notes.get("colors", []) if isinstance(c, dict)}
    for name in sorted(used - explained):
        found.append(f"\\{name} is used, but colors doesn't say what {name} stands for. Add it, or don't use it.")
    return found


def is_old(notes) -> bool:
    """Notes in the earlier format: have, goal and steps instead of given, find and methods."""
    return isinstance(notes, dict) and "steps" in notes and "methods" not in notes


def upgrade(notes: dict) -> dict:
    """Notes in the earlier format, rewritten in today's, so clipped notes keep opening.

    The old facts (have) become methods, the old steps become solution blocks, and the old
    complete solution becomes the exam version. Fields the old format didn't have stay empty.
    """
    if not is_old(notes):
        return notes
    old_sol = notes.get("solution") or {}
    methods = [{"id": f"M{i}", "name": f"({h.get('label', i)})", "formula": h.get("formula", ""),
                "says": h.get("meaning", ""), "why": ""} for i, h in enumerate(notes.get("have") or [], 1)]
    blocks = []
    for s in notes.get("steps") or []:
        block = {"title": s.get("title", ""), "uses": [], "uses_text": s.get("uses", ""),
                 "work": s.get("formula", ""), "result": "", "explain": s.get("meaning", "")}
        for key in ("expansion", "picture", "figure", "caption"):
            if s.get(key):
                block[key] = s[key]
        blocks.append(block)
    exam = ([{"text": old_sol["intro"]}] if old_sol.get("intro") else []) + list(old_sol.get("steps") or [])
    new = {
        "title": notes.get("title", ""),
        "asked": notes.get("asked", ""),
        "answer": {"result": notes.get("answer", ""), "text": notes.get("short_answer") or old_sol.get("key_idea", "")},
        "colors": notes.get("colors", []),
        "given": [],
        "find": notes.get("goal") or {"formula": "", "meaning": ""},
        "methods": methods,
        "plan": notes.get("example", ""),
        "solution": blocks,
        "takeaways": {"key_idea": old_sol.get("key_idea", ""),
                      "mistakes": [old_sol["watch_out"]] if old_sol.get("watch_out") else []},
        "exam": exam,
    }
    if notes.get("options"):
        new["options"] = notes["options"]
    return new


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
    notes = upgrade(notes)
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
        rf"\textbf{{Problem.}} {t(notes['asked'])}",
    ]
    answer = notes.get("answer") or {}
    if answer.get("result"):
        lines.append(rf"\textbf{{Answer.}} $\displaystyle {answer['result']}$")
    if answer.get("text"):
        lines.append(t(answer["text"]))
    if notes.get("colors"):
        lines.append(r"\textbf{Colours.} " + "; ".join(
            rf"$\{c['color']}{{\blacksquare}}$ {t(c['meaning'])}" for c in notes["colors"]) + ".")
    if notes.get("given"):
        lines.append(r"\section*{Given}")
        lines.append(r"\begin{itemize}")
        for g in notes["given"]:
            value = rf" = {g['value']}" if g.get("value") else ""
            lines.append(rf"\item $\displaystyle {g['symbol']}{value}$: {t(g['meaning'])}")
        lines.append(r"\end{itemize}")
    find = notes.get("find") or {}
    if find.get("formula"):
        lines.append(rf"\textbf{{Find.}} $\displaystyle {find['formula']}$. {t(find.get('meaning', ''))}")
    lines.append(r"\section*{Methods}")
    for m in notes["methods"]:
        lines.append(rf"\textbf{{{t(m['id'])} {t(m['name'])}.}} \[ {m['formula']} \]")
        lines.append(t(m["says"]) + (rf" \emph{{Why here:}} {t(m['why'])}" if m.get("why") else ""))
    if notes.get("plan"):
        lines.append(rf"\textbf{{Plan.}} {t(notes['plan'])}")
    lines.append(r"\section*{Solution}")
    figure = 0
    for b in notes["solution"]:
        uses = ", ".join(b.get("uses") or []) or b.get("uses_text", "")
        lines.append(rf"\subsection*{{{t(b['title'])}}}")
        if uses:
            lines.append(rf"\emph{{Uses {t(uses)}.}}")
        lines.append(rf"\[ {b['work']} \]")
        if b.get("expansion"):
            lines.append(rf"\[ {b['expansion']} \]")
        if b.get("figure") or b.get("picture"):
            figure += 1
            caption = rf" {t(b['caption'])}" if b.get("caption") else ""
            body = _figure_tex(b["figure"]) if b.get("figure") else rf"$\displaystyle {b['picture']}$"
            lines.append(rf"\begin{{center}}{body}\\[4pt] \small\textbf{{Figure {figure}.}}{caption}\end{{center}}")
        lines.append(t(b["explain"]))
        if b.get("result"):
            lines.append(rf"\textbf{{Result:}} $\displaystyle {b['result']}$")
    if notes.get("checks"):
        lines.append(r"\section*{Checks}")
        lines.append(r"\begin{itemize}" + "".join(rf"\item {t(c)}" for c in notes["checks"]) + r"\end{itemize}")
    if notes.get("options"):
        lines.append(r"\section*{Every option}")
        lines.append(r"\begin{tabular}{lllp{6.5cm}}\toprule Option & Computes & Value & Verdict \\ \midrule")
        for o in notes["options"]:
            mark = r"$\green{\checkmark}$" if o.get("correct") else ""
            lines.append(rf"{t(o['option'])} {mark} & ${o['computes']}$ & {t(o.get('value', ''))} & {t(o['verdict'])} \\")
        lines.append(r"\bottomrule\end{tabular}")
    take = notes.get("takeaways") or {}
    lines.append(r"\section*{Takeaways}")
    if take.get("key_idea"):
        lines.append(rf"\textbf{{Key idea.}} {t(take['key_idea'])}")
    if take.get("mistakes"):
        lines.append(r"\textbf{Common mistakes.}\begin{itemize}" + "".join(rf"\item {t(m)}" for m in take["mistakes"]) + r"\end{itemize}")
    if notes.get("exam"):
        lines.append(r"\section*{Exam version}")
        lines.append(r"\begin{enumerate}")
        for e in notes["exam"]:
            lines.append(rf"\item {t(e['text'])}" + (rf" \[ {e['formula']} \]" if e.get("formula") else ""))
        lines.append(r"\end{enumerate}")
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"


def _figure_tex(fig: dict) -> str:
    """A figure the Notepad draws, for the .tex export: the folds as text, or where to find the structure."""
    if fig.get("type") == "rna":
        rows = [rf"\texttt{{{fig['sequence']}}}"]
        for st in fig["states"]:
            energy = rf" ($\Delta G = {st['energy']}$ kcal/mol)" if "energy" in st else ""
            rows.append(rf"\texttt{{{st['structure']}}}\quad {_tex_text(st['name'])}{energy}")
        return r"{\footnotesize " + r"\\ ".join(rows) + "}"
    if fig.get("type") == "sampler":
        return (rf"Ising model on a ${fig['size']} \times {fig['size']}$ lattice, $\theta = {fig['theta']}$, sampled by "
                r"Gibbs and by Gibbs-With-Gradients. Open the notes in the Notepad to watch the chains run.")
    return rf"3D structure: PDB \texttt{{{fig['pdb']}}}. Open the notes in the Notepad to turn it around."
