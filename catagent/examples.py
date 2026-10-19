"""Example study notes, written the way Ginger writes them with write_study_notes.

`python -m catagent.notepad` opens the Notepad with these, so you can try it without a model.
"""

_A_ROW1 = r"\begin{bmatrix} \beige{a_{11}} & \beige{a_{12}} & \beige{a_{13}} \\ a_{21} & a_{22} & a_{23} \end{bmatrix}"
_B_COL1 = r"\begin{bmatrix} \blue{b_{11}} & b_{12} \\ \blue{b_{21}} & b_{22} \\ \blue{b_{31}} & b_{32} \end{bmatrix}"
_B_ROW1 = r"\begin{bmatrix} \blue{b_{11}} & \blue{b_{12}} \\ b_{21} & b_{22} \\ b_{31} & b_{32} \end{bmatrix}"
_A_COL1 = r"\begin{bmatrix} \beige{a_{11}} & a_{12} & a_{13} \\ \beige{a_{21}} & a_{22} & a_{23} \end{bmatrix}"


def _ab(i: int) -> str:
    return " + ".join(rf"\beige{{a_{{{i}{j}}}}}\blue{{b_{{{j}{i}}}}}" for j in (1, 2, 3))


def _ba(j: int) -> str:
    return " + ".join(rf"\blue{{b_{{{j}{i}}}}}\beige{{a_{{{i}{j}}}}}" for i in (1, 2))


TRACE_NOTES = {
    "title": r"$\operatorname{Trace}(AB) = \operatorname{Trace}(BA)$",
    "asked": r"Prove that for two matrices $A \in \mathbb{R}^{n\times m}$ and $B \in \mathbb{R}^{m\times n}$, "
             r"Trace(AB) = Trace(BA). I'm stuck.",
    "colors": [
        {"color": "beige", "meaning": "entries of $A$"},
        {"color": "blue", "meaning": "entries of $B$"},
        {"color": "green", "meaning": "diagonal entries, the ones the trace adds up"},
    ],
    "have": [
        {"label": "D1",
         "formula": r"\beige{A} \in \mathbb{R}^{n\times m},\ \blue{B} \in \mathbb{R}^{m\times n} \implies "
                    r"AB \in \mathbb{R}^{n\times n},\ BA \in \mathbb{R}^{m\times m}",
         "meaning": "The sizes. $AB$ and $BA$ are both square, but they can be different sizes, so we can't "
                    "compare the matrices themselves, only their traces."},
        {"label": "D2",
         "formula": r"\operatorname{Trace}(M) = \sum_{i} \green{M_{ii}}",
         "meaning": r"The trace. Add up the $\green{\text{diagonal entries}}$, where the row number equals the column number."},
        {"label": "D3",
         "formula": r"(AB)_{ik} = \sum_{j=1}^{m} \beige{a_{ij}}\,\blue{b_{jk}}",
         "meaning": r"Matrix multiplication. Entry $(i, k)$ of $AB$ takes $\beige{\text{row } i \text{ of } A}$ and "
                    r"$\blue{\text{column } k \text{ of } B}$, multiplies them entry by entry, and adds. "
                    r"The index $j$ walks along both."},
    ],
    "goal": {
        "formula": r"\operatorname{Trace}(AB) = \operatorname{Trace}(BA)",
        "meaning": "Show that the two diagonals add up to the same number. The plan: write both traces using "
                   "(D2) and (D3), then compare them term by term.",
    },
    "example": r"Each step uses an example with $n = 2$ and $m = 3$, so $A$ is $2 \times 3$ and $B$ is $3 \times 2$. "
               r"The colours match the formulas.",
    "steps": [
        {"title": "One diagonal entry of $AB$",
         "uses": "(D3) with $k = i$",
         "formula": r"\green{(AB)_{ii}} = \sum_{j=1}^{m} \beige{a_{ij}}\,\blue{b_{ji}}",
         "picture": _A_ROW1 + r" \cdot " + _B_COL1 + r" = \begin{bmatrix} \green{(AB)_{11}} & \cdot \\ \cdot & \cdot \end{bmatrix}",
         "expansion": r"\green{(AB)_{11}} = " + _ab(1),
         "meaning": r"The diagonal entry $\green{(AB)_{11}}$ comes from $\beige{\text{row 1 of } A}$ and "
                    r"$\blue{\text{column 1 of } B}$. Pair them up entry by entry, multiply and add. In every "
                    r"product the $A$ entry is $a_{ij}$ and its partner in $B$ is $b_{ji}$: the same two indices, swapped."},
        {"title": "Add up the whole diagonal of $AB$",
         "uses": "(D2) and step 1",
         "formula": r"\operatorname{Trace}(AB) = \sum_{i=1}^{n} \green{(AB)_{ii}} = \sum_{i=1}^{n}\sum_{j=1}^{m} \beige{a_{ij}}\,\blue{b_{ji}}",
         "picture": r"\begin{bmatrix} \green{(AB)_{11}} & \cdot \\ \cdot & \green{(AB)_{22}} \end{bmatrix} "
                    r"\;\longrightarrow\; \operatorname{Trace}(AB) = \green{(AB)_{11}} + \green{(AB)_{22}}",
         "expansion": r"\begin{aligned} \green{(AB)_{11}} &= " + _ab(1) + r" \\ \green{(AB)_{22}} &= " + _ab(2) + r" \end{aligned}",
         "meaning": r"The trace adds the $\green{\text{diagonal entries}}$, and each one is the sum from step 1. "
                    r"So $\operatorname{Trace}(AB)$ is just a list of products: every entry $\beige{a_{ij}}$ of $A$ "
                    r"times its partner $\blue{b_{ji}}$. Here that's 6 products, one for each entry of $A$."},
        {"title": "Do the same for $BA$",
         "uses": "(D2) and (D3) with the roles of $A$ and $B$ swapped",
         "formula": r"\operatorname{Trace}(BA) = \sum_{j=1}^{m} \green{(BA)_{jj}} = \sum_{j=1}^{m}\sum_{i=1}^{n} \blue{b_{ji}}\,\beige{a_{ij}}",
         "picture": _B_ROW1 + r" \cdot " + _A_COL1 + r" = \begin{bmatrix} \green{(BA)_{11}} & \cdot & \cdot \\ "
                    r"\cdot & \green{(BA)_{22}} & \cdot \\ \cdot & \cdot & \green{(BA)_{33}} \end{bmatrix}",
         "expansion": r"\begin{aligned} \green{(BA)_{11}} &= " + _ba(1) + r" \\ \green{(BA)_{22}} &= " + _ba(2)
                      + r" \\ \green{(BA)_{33}} &= " + _ba(3) + r" \end{aligned}",
         "meaning": r"Now $B$ comes first, so each diagonal entry $\green{(BA)_{jj}}$ takes $\blue{\text{row } j \text{ of } B}$ "
                    r"and $\beige{\text{column } j \text{ of } A}$. $BA$ is $3 \times 3$, so its diagonal has three entries "
                    r"instead of two, but look at the products: they're the same 6 pairs as in step 2."},
        {"title": "Compare the two sums",
         "uses": "steps 2 and 3",
         "formula": r"\sum_{i=1}^{n}\sum_{j=1}^{m} \beige{a_{ij}}\,\blue{b_{ji}} = \sum_{j=1}^{m}\sum_{i=1}^{n} \blue{b_{ji}}\,\beige{a_{ij}}",
         "picture": r"\begin{array}{cc|cc} \text{in } \operatorname{Trace}(AB) & \text{found in} & \text{in } \operatorname{Trace}(BA) & \text{found in} \\ \hline "
                    + r" \\ ".join(
                        rf"\beige{{a_{{{i}{j}}}}}\blue{{b_{{{j}{i}}}}} & (AB)_{{{i}{i}}} & \blue{{b_{{{j}{i}}}}}\beige{{a_{{{i}{j}}}}} & (BA)_{{{j}{j}}}"
                        for i in (1, 2) for j in (1, 2, 3))
                    + r" \end{array}",
         "meaning": r"Both traces add up exactly the same 6 products. Each $\beige{a}\blue{b}$ equals its $\blue{b}\beige{a}$ "
                    r"because ordinary numbers commute. They're only grouped differently: $\operatorname{Trace}(AB)$ groups "
                    r"them by the $\green{\text{2 diagonal entries of } AB}$, $\operatorname{Trace}(BA)$ by the "
                    r"$\green{\text{3 diagonal entries of } BA}$. A finite sum doesn't depend on how you group or order it, "
                    r"so the two totals are equal."},
    ],
    "solution": {
        "intro": r"Let $\beige{A} \in \mathbb{R}^{n\times m}$ and $\blue{B} \in \mathbb{R}^{m\times n}$, with entries $a_{ij}$ and $b_{ji}$.",
        "steps": [
            {"text": "By the definition of matrix multiplication, each diagonal entry of $AB$ is",
             "formula": r"\green{(AB)_{ii}} = \sum_{j=1}^{m} \beige{a_{ij}}\,\blue{b_{ji}}."},
            {"text": "Adding the diagonal entries gives",
             "formula": r"\operatorname{Trace}(AB) = \sum_{i=1}^{n}\sum_{j=1}^{m} \beige{a_{ij}}\,\blue{b_{ji}}."},
            {"text": r"In the same way, $(BA)_{jj} = \sum_i b_{ji}a_{ij}$, so",
             "formula": r"\operatorname{Trace}(BA) = \sum_{j=1}^{m}\sum_{i=1}^{n} \blue{b_{ji}}\,\beige{a_{ij}}."},
            {"text": r"Since $b_{ji}a_{ij} = a_{ij}b_{ji}$ and both are finite sums over the same pairs $(i, j)$, "
                     r"the order of summation can be swapped:",
             "formula": r"\sum_{j=1}^{m}\sum_{i=1}^{n} b_{ji}a_{ij} = \sum_{i=1}^{n}\sum_{j=1}^{m} a_{ij}b_{ji}."},
            {"text": r"By steps 2 to 4, $\operatorname{Trace}(AB) = \operatorname{Trace}(BA)$. $\blacksquare$"},
        ],
        "key_idea": r"Both traces are the same finite sum of the products $a_{ij}b_{ji}$, just grouped differently.",
        "watch_out": r"$AB$ and $BA$ are usually different matrices, here even different sizes. Only their traces agree.",
    },
}
