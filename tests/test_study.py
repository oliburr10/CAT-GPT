import copy
import json
import shutil
import subprocess

import pytest

from catagent import examples, study, tools


def test_example_notes_are_valid():
    assert study.problems(examples.TRACE_NOTES) == []


def test_problems_name_the_field_to_fix():
    notes = copy.deepcopy(examples.TRACE_NOTES)
    notes["steps"][1]["formula"] = r"\sum_{i=1 \green{x}"
    notes["have"][0]["meaning"] = "costs $5"
    notes["colors"][0]["color"] = "red"
    del notes["solution"]["key_idea"]
    notes["goal"]["formula"] = "$x = y$"
    found = study.problems(notes)
    assert "steps[2].formula has unbalanced braces." in found
    assert "have[1].meaning has an unmatched $." in found
    assert any(p.startswith("colors[1].color must be one of") for p in found)
    assert "solution.key_idea must be a non-empty string." in found
    assert "goal.formula is a formula: leave out the $ signs." in found


def test_loose_latex_goal_in_have_and_unexplained_colours():
    notes = copy.deepcopy(examples.TRACE_NOTES)
    notes["example"] = r"Take A = \begin{bmatrix} 1 \end{bmatrix}"
    notes["steps"][0]["meaning"] = "Each entry (AB)_{ii} is a dot product."
    notes["have"].append({"label": "Goal", "formula": "x", "meaning": "y"})
    notes["steps"][1]["picture"] = r"\purple{x}"
    found = study.problems(notes)
    assert "example has LaTeX outside $...$ (near '\\\\begin'): wrap every bit of maths in $...$." in found
    assert any(p.startswith("steps[1].meaning has LaTeX outside $...$") for p in found)
    assert "have[4] is the goal: put it only in goal, not in have." in found
    assert not any(p.startswith("asked") for p in study.problems({**examples.TRACE_NOTES, "asked": "A ∈ R^{n×m}, costs $5"}))
    assert "\\purple is used, but colors doesn't say what purple stands for. Add it, or don't use it." in found


def test_missing_sections():
    assert "steps must be a list of at least 1 object(s)." in study.problems({**examples.TRACE_NOTES, "steps": []})
    assert study.problems("notes") == ["The notes must be a JSON object."]


def test_stringified_fields_are_unpacked():
    """Some free models send lists as JSON strings."""
    sent = {**examples.TRACE_NOTES, "steps": json.dumps(examples.TRACE_NOTES["steps"])}
    assert study.problems(tools._unpack(sent)) == []


def test_tex_export_escapes_text_but_not_math():
    tex = study.to_tex(examples.TRACE_NOTES)
    assert r"\newcommand{\beige}[1]{\colorbox{notebeige}{$#1$}}" in tex
    assert r"\section*{3\quad Complete solution}" in tex
    assert study._tex_text("50% of a_b, $a_{ij}$") == r"50\% of a\_b, $a_{ij}$"


@pytest.mark.skipif(not shutil.which("pdflatex"), reason="pdflatex isn't installed")
def test_tex_export_compiles(tmp_path):
    notes = copy.deepcopy(examples.TRACE_NOTES)
    notes["asked"] = "Prove that for A ∈ ℝ^{n×m} and B ∈ ℝ^{m×n}, Trace(AB) = Trace(BA) ≥ 0? (α, Σ, ∎) 50% & #1"
    (tmp_path / "notes.tex").write_text(study.to_tex(notes))
    run = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "notes.tex"],
                         cwd=tmp_path, capture_output=True, text=True, timeout=120, check=False)
    assert run.returncode == 0, run.stdout[-2000:]
