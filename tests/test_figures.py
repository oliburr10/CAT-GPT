import copy

import pytest

from catagent import examples, figures, study


def rna_figure():
    return copy.deepcopy(examples.RIBO_NOTES["solution"][1]["figure"])


def test_example_figures_are_valid():
    for step in examples.RIBO_NOTES["solution"]:
        if "figure" in step:
            assert figures.problems(step["figure"], "f") == []


def test_dot_bracket_is_parsed_or_explained():
    assert figures.pairs("((..))") == {0: 5, 5: 0, 1: 4, 4: 1}
    assert figures.pairs("(()") == "has 1 '(' that never close (the first at position 1)"
    assert figures.pairs("())") == "has a ')' at position 3 with no '(' before it"
    assert "may only contain" in figures.pairs("((x))")


def test_rna_mistakes_are_named():
    fig = rna_figure()
    fig["states"][0]["structure"] = fig["states"][0]["structure"][:-1]
    fig["regions"][0]["end"] = 999
    fig["ligand"]["near"] = [0]
    found = figures.problems(fig, "steps[2].figure")
    assert any("states[1].structure must be dot-bracket with exactly 103 characters" in p for p in found)
    assert "steps[2].figure.regions[1] must have 1 <= start <= end <= 103." in found
    assert "steps[2].figure.ligand.near must list base numbers between 1 and 103." in found
    assert figures.problems({"type": "rna", "sequence": "ACGT", "states": []}, "f") == [
        "f.sequence must be RNA letters A, C, G, U only (no T, spaces or numbers)."]


def test_only_watson_crick_and_wobble_pairs():
    found = figures.problems({"type": "rna", "sequence": "GCAAAAGA", "states": [
        {"name": "x", "note": "y", "structure": "((....))"}]}, "f")
    assert found == ["f.states[1].structure pairs bases that can't pair: 1-8 (G-A). Only A-U, G-C and G-U pair."]


def test_hairpin_loops_need_three_bases():
    found = figures.problems({"type": "rna", "sequence": "GGAACC", "states": [
        {"name": "x", "note": "y", "structure": "((..))"}]}, "f")
    assert found == ["f.states[1].structure has a hairpin loop shorter than 3 bases, which RNA can't form."]


def test_molecule_mistakes_are_named():
    fig = {"type": "molecule", "pdb": "4FE", "highlights": [{"residues": "a-b", "color": "teal", "label": ""}],
           "ligand": {"name": "x", "resn": "adenine"}}
    found = figures.problems(fig, "f")
    assert "f.pdb must be a 4-character PDB ID like 1Y26." in found
    assert "f.highlights[1].residues must be numbers or ranges like 13-19,64-71." in found
    assert any(p.startswith("f.highlights[1].color must be one of") for p in found)
    assert "f.highlights[1].label must be a non-empty string." in found
    assert any(p.startswith("f.ligand.resn must be") for p in found)


def test_notes_check_their_figures():
    notes = copy.deepcopy(examples.RIBO_NOTES)
    notes["solution"][1]["picture"] = r"\text{also a picture}"
    notes["solution"][0]["figure"]["pdb"] = "nope"
    found = study.problems(notes)
    assert "solution[2] has both picture and figure: keep one." in found
    assert "solution[1].figure.pdb must be a 4-character PDB ID like 1Y26." in found


@pytest.mark.skipif(not figures.energies_available(), reason="ViennaRNA isn't installed")
def test_energies_from_viennarna():
    notes = figures.add_energies(copy.deepcopy(examples.RIBO_NOTES))
    off, on = notes["solution"][1]["figure"]["states"]
    assert off["energy"] == pytest.approx(-30.7, abs=0.05)
    assert on["energy"] == pytest.approx(-24.5, abs=0.05)
    assert "energy" not in examples.RIBO_NOTES["solution"][1]["figure"]["states"][0]   # the example is untouched


def test_tex_export_writes_figures_as_text():
    tex = study.to_tex(examples.RIBO_NOTES)
    assert r"\texttt{" + examples._RIBO_OFF + "}" in tex
    assert r"PDB \texttt{4FEO}" in tex


def test_sampler_specs():
    assert figures.problems({"type": "sampler", "model": "ising", "size": 24, "theta": 0.3}, "f") == []
    found = figures.problems({"type": "sampler", "model": "potts", "size": 100, "theta": 0}, "f")
    assert found == ["f.model must be ising.", "f.size must be a whole number from 8 to 40.",
                     "f.theta must be a number with 0 < theta <= 1."]
    assert figures.problems({"type": "chart"}, "f") == ["f.type must be rna, molecule or sampler."]
    assert r"$24 \times 24$ lattice" in study.to_tex(examples.PAPER_NOTES)
