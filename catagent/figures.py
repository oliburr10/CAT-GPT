"""Figures in study notes that the Notepad draws itself, instantly and interactively.

The model never draws. It writes a small spec, this module checks it, and the Notepad page
(web/figures.js) draws it:

  rna       An RNA sequence and one or more ways it folds (dot-bracket), with coloured regions
            and an optional ligand. The Notepad lays out each fold and morphs between them, so a
            riboswitch visibly refolds. Base pairs are checked here: every pair must be A-U, G-C
            or G-U. If ViennaRNA is installed, each fold also gets its free energy.
  molecule  A 3D structure from the Protein Data Bank by its ID, with highlighted residues and
            a ligand, shown with 3Dmol.js. The page downloads the file from RCSB.
  sampler   An Ising model on a small lattice, sampled live by two Markov chains side by side:
            Gibbs (one random site at a time) and Gibbs-With-Gradients (a gradient-informed
            proposal, drawn as a heat map). For MCMC, Metropolis-Hastings and Ising models.
"""

import re

from .palette import COLORS

PAIRS = {("A", "U"), ("U", "A"), ("G", "C"), ("C", "G"), ("G", "U"), ("U", "G")}

_REGION = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Short label, e.g. SD, P1, switch."},
        "start": {"type": "integer", "description": "First base, counting from 1."},
        "end": {"type": "integer", "description": "Last base, inclusive."},
        "color": {"type": "string", "enum": list(COLORS)},
    },
    "required": ["name", "start", "end", "color"],
}

SCHEMA = {
    "type": "object",
    "description": "Optional figure the Notepad draws itself (instead of picture): an RNA fold, a 3D molecule or a live MCMC sampler.",
    "properties": {
        "type": {"type": "string", "enum": ["rna", "molecule", "sampler"]},
        # rna
        "sequence": {"type": "string", "description": "rna: the sequence, A C G U only, 5' to 3'."},
        "states": {
            "type": "array",
            "description": "rna: one or more folds of the same sequence, shown one at a time; the Notepad animates between them.",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "e.g. no adenine, + adenine."},
                    "structure": {"type": "string", "description": "Dot-bracket, same length as the sequence."},
                    "note": {"type": "string", "description": "One sentence: what this fold means, e.g. SD hidden: translation off."},
                    "ligand": {"type": "boolean", "description": "Whether the ligand is bound in this fold."},
                },
                "required": ["name", "structure", "note"],
            },
        },
        "regions": {"type": "array", "items": _REGION, "description": "rna: coloured stretches, e.g. the SD."},
        "ligand": {
            "type": "object",
            "description": "rna: the ligand's name and the bases it sits next to; molecule: its residue name in the PDB file.",
            "properties": {
                "name": {"type": "string"},
                "near": {"type": "array", "items": {"type": "integer"}, "description": "rna: base numbers around the binding pocket."},
                "resn": {"type": "string", "description": "molecule: residue name in the PDB file, e.g. ADE."},
            },
            "required": ["name"],
        },
        # molecule
        "pdb": {"type": "string", "description": "molecule: a 4-character PDB ID you are sure of, e.g. 1Y26."},
        "highlights": {
            "type": "array",
            "description": "molecule: residues to colour and label.",
            "items": {
                "type": "object",
                "properties": {
                    "chain": {"type": "string"},
                    "residues": {"type": "string", "description": "Residue numbers, e.g. 13-19 or 13-19,64-71."},
                    "color": {"type": "string", "enum": list(COLORS)},
                    "label": {"type": "string"},
                },
                "required": ["residues", "color", "label"],
            },
        },
        # sampler
        "model": {"type": "string", "enum": ["ising"], "description": "sampler: the model sampled."},
        "size": {"type": "integer", "description": "sampler: the lattice is size x size, 8 to 40."},
        "theta": {"type": "number", "description": "sampler: coupling strength, 0 < theta <= 1; about 0.3 shows domains forming."},
    },
    "required": ["type"],
}


def pairs(structure: str) -> dict[int, int] | str:
    """Dot-bracket to {i: j} (0-based, both ways), or a sentence saying what's wrong with it."""
    stack, out = [], {}
    for i, ch in enumerate(structure):
        if ch == "(":
            stack.append(i)
        elif ch == ")":
            if not stack:
                return f"has a ')' at position {i + 1} with no '(' before it"
            j = stack.pop()
            out[i], out[j] = j, i
        elif ch != ".":
            return f"may only contain ( ) and . (found {ch!r} at position {i + 1})"
    if stack:
        return f"has {len(stack)} '(' that never close (the first at position {stack[0] + 1})"
    return out


def problems(fig, where: str) -> list[str]:
    """What's wrong with a figure spec, in words the model can act on. Empty means fine."""
    if not isinstance(fig, dict):
        return [f"{where} must be an object."]
    kind = fig.get("type")
    if kind == "rna":
        return _rna_problems(fig, where)
    if kind == "molecule":
        return _molecule_problems(fig, where)
    if kind == "sampler":
        return _sampler_problems(fig, where)
    return [f"{where}.type must be rna, molecule or sampler."]


def _rna_problems(fig, where):
    found = []
    seq = fig.get("sequence")
    if not isinstance(seq, str) or not re.fullmatch(r"[ACGU]+", seq or ""):
        return [f"{where}.sequence must be RNA letters A, C, G, U only (no T, spaces or numbers)."]
    n = len(seq)
    states = fig.get("states")
    if not isinstance(states, list) or not states or not all(isinstance(s, dict) for s in states):
        return [f"{where}.states must be a list of at least one fold."]
    for k, st in enumerate(states, 1):
        at = f"{where}.states[{k}]"
        for key in ("name", "note"):
            if not isinstance(st.get(key), str) or not st[key].strip():
                found.append(f"{at}.{key} must be a non-empty string.")
        s = st.get("structure")
        if not isinstance(s, str) or len(s) != n:
            found.append(f"{at}.structure must be dot-bracket with exactly {n} characters, one per base "
                         f"(it has {len(s) if isinstance(s, str) else 'none'}).")
            continue
        p = pairs(s)
        if isinstance(p, str):
            found.append(f"{at}.structure {p}.")
            continue
        bad = [(i, j) for i, j in p.items() if i < j and (seq[i], seq[j]) not in PAIRS]
        if bad:
            shown = ", ".join(f"{i + 1}-{j + 1} ({seq[i]}-{seq[j]})" for i, j in bad[:4])
            found.append(f"{at}.structure pairs bases that can't pair: {shown}. Only A-U, G-C and G-U pair.")
        if any(j - i < 4 for i, j in p.items() if i < j):
            found.append(f"{at}.structure has a hairpin loop shorter than 3 bases, which RNA can't form.")
    for k, r in enumerate(fig.get("regions") or [], 1):
        at = f"{where}.regions[{k}]"
        if not isinstance(r, dict):
            found.append(f"{at} must be an object.")
            continue
        if r.get("color") not in COLORS:
            found.append(f"{at}.color must be one of {', '.join(COLORS)}.")
        if not (isinstance(r.get("start"), int) and isinstance(r.get("end"), int) and 1 <= r["start"] <= r["end"] <= n):
            found.append(f"{at} must have 1 <= start <= end <= {n}.")
    lig = fig.get("ligand")
    if lig is not None:
        if not isinstance(lig, dict) or not isinstance(lig.get("name"), str) or not lig["name"].strip():
            found.append(f"{where}.ligand needs a name.")
        elif not lig.get("near") or not all(isinstance(i, int) and 1 <= i <= n for i in lig["near"]):
            found.append(f"{where}.ligand.near must list base numbers between 1 and {n}.")
    return found


def _molecule_problems(fig, where):
    found = []
    if not re.fullmatch(r"[0-9][A-Za-z0-9]{3}", str(fig.get("pdb", ""))):
        found.append(f"{where}.pdb must be a 4-character PDB ID like 1Y26.")
    for k, hl in enumerate(fig.get("highlights") or [], 1):
        at = f"{where}.highlights[{k}]"
        if not isinstance(hl, dict):
            found.append(f"{at} must be an object.")
            continue
        if not re.fullmatch(r"-?\d+(--?\d+)?(,-?\d+(--?\d+)?)*", str(hl.get("residues", "")).replace(" ", "")):
            found.append(f"{at}.residues must be numbers or ranges like 13-19,64-71.")
        if hl.get("color") not in COLORS:
            found.append(f"{at}.color must be one of {', '.join(COLORS)}.")
        if not isinstance(hl.get("label"), str) or not hl["label"].strip():
            found.append(f"{at}.label must be a non-empty string.")
    lig = fig.get("ligand")
    if lig is not None and not (isinstance(lig, dict) and re.fullmatch(r"[A-Z0-9]{1,3}", str(lig.get("resn", "")))):
        found.append(f"{where}.ligand.resn must be the ligand's residue name in the PDB file, 1 to 3 capitals, e.g. ADE.")
    return found


def _sampler_problems(fig, where):
    found = []
    if fig.get("model", "ising") != "ising":
        found.append(f"{where}.model must be ising.")
    size = fig.get("size")
    if not (isinstance(size, int) and not isinstance(size, bool) and 8 <= size <= 40):
        found.append(f"{where}.size must be a whole number from 8 to 40.")
    theta = fig.get("theta")
    if not (isinstance(theta, (int, float)) and not isinstance(theta, bool) and 0 < theta <= 1):
        found.append(f"{where}.theta must be a number with 0 < theta <= 1.")
    return found


# ---- energies -----------------------------------------------------------------------------

def energies_available() -> bool:
    try:
        import RNA  # noqa: F401  (ViennaRNA, optional)
    except ImportError:
        return False
    return True


def add_energies(notes: dict) -> dict:
    """Give every RNA fold its free energy from ViennaRNA, if it's installed. Returns the notes."""
    if not energies_available():
        return notes
    import RNA

    for block in notes.get("solution") or []:
        fig = block.get("figure") if isinstance(block, dict) else None
        if not isinstance(fig, dict) or fig.get("type") != "rna":
            continue
        compound = RNA.fold_compound(fig["sequence"])
        for state in fig["states"]:
            state["energy"] = round(compound.eval_structure(state["structure"]), 1)
    return notes
