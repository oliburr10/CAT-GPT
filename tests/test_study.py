import copy
import json
import shutil
import subprocess

import pytest

from catagent import examples, study, tools


@pytest.mark.parametrize("name", sorted(examples.EXAMPLES))
def test_example_notes_are_valid(name):
    assert study.problems(examples.EXAMPLES[name]) == []


def test_problems_name_the_field_to_fix():
    notes = copy.deepcopy(examples.TRACE_NOTES)
    notes["solution"][1]["work"] = r"\sum_{i=1 \green{x}"
    notes["given"][0]["meaning"] = "costs $5"
    notes["colors"][0]["color"] = "yellow"
    del notes["takeaways"]["key_idea"]
    notes["find"]["formula"] = "$x = y$"
    notes["answer"] = "B"
    found = study.problems(notes)
    assert "solution[2].work has unbalanced braces." in found
    assert "given[1].meaning has an unmatched $." in found
    assert any(p.startswith("colors[1].color must be one of") for p in found)
    assert "takeaways.key_idea must be a non-empty string." in found
    assert "find.formula is a formula: leave out the $ signs." in found
    assert "answer must be an object with result and text." in found


def test_methods_must_be_listed_and_used():
    notes = copy.deepcopy(examples.ROLL_NOTES)
    notes["solution"][0]["uses"] = ["M9"]                       # cites a method that isn't there
    notes["methods"][1]["id"] = "M1"                            # a duplicate id
    notes["methods"].append({"id": "M6", "name": "Unused", "formula": "x", "says": "a", "why": "b"})
    found = study.problems(notes)
    assert "solution[1].uses M9, but there is no method M9: add it to methods." in found
    assert "methods[2].id M1 is used twice." in found
    assert "M6 is never used in the solution: use it in a block's uses, or leave it out." in found


def test_blocks_are_named_by_what_they_work_out():
    notes = copy.deepcopy(examples.ROLL_NOTES)
    notes["solution"][0]["title"] = "Step 1: the jump"
    notes["solution"][1]["uses"] = []
    assert "solution[1].title starts with a step number: name what the block works out instead, e.g. Speed at the edge." \
        in study.problems(notes)
    assert 'solution[2].uses must list the methods it uses, e.g. ["M1"].' in study.problems(notes)


def test_loose_latex_and_unexplained_colours():
    notes = copy.deepcopy(examples.TRACE_NOTES)
    notes["plan"] = r"Take A = \begin{bmatrix} 1 \end{bmatrix}"
    notes["solution"][0]["explain"] = "Each entry (AB)_{ii} is a dot product."
    notes["solution"][1]["work"] = r"\purple{x}"
    found = study.problems(notes)
    assert "plan has LaTeX outside $...$ (near '\\\\begin'): wrap every bit of maths in $...$." in found
    assert any(p.startswith("solution[1].explain has LaTeX outside $...$") for p in found)
    assert not any(p.startswith("asked") for p in study.problems({**examples.TRACE_NOTES, "asked": "A ∈ R^{n×m}, costs $5"}))
    assert "\\purple is used, but colors doesn't say what purple stands for. Add it, or don't use it." in found


def test_old_colours_and_too_many_highlights_are_named():
    notes = copy.deepcopy(examples.TRACE_NOTES)
    notes["solution"][0]["work"] = r"\beige{a} + \hl{x} + \hl{y}"
    notes["solution"][1]["work"] = r"\hl{z} + \hl{w}"
    found = study.problems(notes)
    assert any("uses \\beige, but the colours are blue, orange" in p for p in found)
    assert any(p.startswith("\\hl is used 5 times. Highlight at most 3") for p in found)


def test_options_need_exactly_one_correct():
    notes = copy.deepcopy(examples.PURITY_NOTES)
    notes["options"][0]["correct"] = True
    notes["options"][2]["correct"] = "no"
    found = study.problems(notes)
    assert "options must mark exactly one option as correct." in found
    assert "options[3].correct must be true or false." in found


def test_missing_sections():
    assert "solution must be a list of at least 1 object(s)." in study.problems({**examples.TRACE_NOTES, "solution": []})
    assert "methods must be a list of at least 1 object(s)." in study.problems({**examples.TRACE_NOTES, "methods": []})
    assert study.problems("notes") == ["The notes must be a JSON object."]


def test_stringified_fields_are_unpacked():
    """Some free models send lists as JSON strings."""
    sent = {**examples.ROLL_NOTES, "solution": json.dumps(examples.ROLL_NOTES["solution"]),
            "methods": json.dumps(examples.ROLL_NOTES["methods"])}
    assert study.problems(tools._unpack(sent)) == []


OLD_NOTES = {
    "title": "Old", "asked": "Prove it.", "short_answer": "Because.",
    "have": [{"label": "D1", "formula": "a = b", "meaning": "a fact"}],
    "goal": {"formula": "b = a", "meaning": "the goal"},
    "steps": [{"title": "Flip it", "uses": "(D1)", "formula": "b = a", "meaning": "symmetry",
               "picture": r"\text{pic}", "caption": "a picture"}],
    "solution": {"intro": "Let a = b.", "steps": [{"text": "So b = a."}], "key_idea": "Symmetry.", "watch_out": "Nothing."},
}


def test_notes_in_the_old_format_are_upgraded():
    assert study.is_old(OLD_NOTES) and not study.is_old(examples.TRACE_NOTES)
    new = study.upgrade(OLD_NOTES)
    assert new["methods"][0] == {"id": "M1", "name": "(D1)", "formula": "a = b", "says": "a fact", "why": ""}
    assert new["find"] == OLD_NOTES["goal"]
    assert new["solution"][0]["uses_text"] == "(D1)" and new["solution"][0]["picture"] == r"\text{pic}"
    assert new["answer"]["text"] == "Because."
    assert new["takeaways"] == {"key_idea": "Symmetry.", "mistakes": ["Nothing."]}
    assert [e["text"] for e in new["exam"]] == ["Let a = b.", "So b = a."]
    assert study.upgrade(examples.TRACE_NOTES) is examples.TRACE_NOTES


def test_tex_export_escapes_text_but_not_math():
    tex = study.to_tex(examples.TRACE_NOTES)
    assert r"\newcommand{\orange}[1]{{\color{noteorange}#1}}" in tex
    assert r"\newcommand{\beige}[1]{\orange{#1}}" in tex
    assert r"\section*{Methods}" in tex and r"\section*{Exam version}" in tex
    assert study._tex_text("50% of a_b, $a_{ij}$") == r"50\% of a\_b, $a_{ij}$"


@pytest.mark.skipif(not shutil.which("pdflatex"), reason="pdflatex isn't installed")
@pytest.mark.parametrize("name", sorted(examples.EXAMPLES) + ["old"])
def test_tex_export_compiles(tmp_path, name):
    notes = copy.deepcopy(OLD_NOTES if name == "old" else examples.EXAMPLES[name])
    notes["asked"] = "Prove that for A ∈ ℝ^{n×m} and B ∈ ℝ^{m×n}, Trace(AB) = Trace(BA) ≥ 0? (α, Σ, ∎) 50% & #1"
    (tmp_path / "notes.tex").write_text(study.to_tex(notes))
    run = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "notes.tex"],
                         cwd=tmp_path, capture_output=True, text=True, timeout=120, check=False)
    assert run.returncode == 0, run.stdout[-2000:]
