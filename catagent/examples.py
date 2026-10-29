"""Example study notes, written the way Ginger writes them with write_study_notes.

`python -m catagent.notepad` opens the Notepad with these, so you can try it without a model.
"""

_A_ROW1 = r"\begin{bmatrix} \orange{a_{11}} & \orange{a_{12}} & \orange{a_{13}} \\ a_{21} & a_{22} & a_{23} \end{bmatrix}"
_B_COL1 = r"\begin{bmatrix} \blue{b_{11}} & b_{12} \\ \blue{b_{21}} & b_{22} \\ \blue{b_{31}} & b_{32} \end{bmatrix}"
_B_ROW1 = r"\begin{bmatrix} \blue{b_{11}} & \blue{b_{12}} \\ b_{21} & b_{22} \\ b_{31} & b_{32} \end{bmatrix}"
_A_COL1 = r"\begin{bmatrix} \orange{a_{11}} & a_{12} & a_{13} \\ \orange{a_{21}} & a_{22} & a_{23} \end{bmatrix}"


def _ab(i: int) -> str:
    return " + ".join(rf"\orange{{a_{{{i}{j}}}}}\blue{{b_{{{j}{i}}}}}" for j in (1, 2, 3))


def _ba(j: int) -> str:
    return " + ".join(rf"\blue{{b_{{{j}{i}}}}}\orange{{a_{{{i}{j}}}}}" for i in (1, 2))


TRACE_NOTES = {
    "title": r"$\operatorname{Trace}(AB) = \operatorname{Trace}(BA)$",
    "asked": r"Prove that for two matrices $A \in \mathbb{R}^{n\times m}$ and $B \in \mathbb{R}^{m\times n}$, "
             r"Trace(AB) = Trace(BA). I'm stuck.",
    "short_answer": r"Write both traces out as sums of products $\orange{a_{ij}}\blue{b_{ji}}$. They turn out to be "
                    r"the same products, only added in a different order.",
    "colors": [
        {"color": "orange", "meaning": "entries of $A$"},
        {"color": "blue", "meaning": "entries of $B$"},
        {"color": "green", "meaning": "diagonal entries, the ones the trace adds up"},
    ],
    "have": [
        {"label": "D1",
         "formula": r"\orange{A} \in \mathbb{R}^{n\times m},\ \blue{B} \in \mathbb{R}^{m\times n} \implies "
                    r"AB \in \mathbb{R}^{n\times n},\ BA \in \mathbb{R}^{m\times m}",
         "meaning": "The sizes. $AB$ and $BA$ are both square, but they can be different sizes, so we can't "
                    "compare the matrices themselves, only their traces."},
        {"label": "D2",
         "formula": r"\operatorname{Trace}(M) = \sum_{i} \green{M_{ii}}",
         "meaning": r"The trace. Add up the $\green{\text{diagonal entries}}$, where the row number equals the column number."},
        {"label": "D3",
         "formula": r"(AB)_{ik} = \sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{jk}}",
         "meaning": r"Matrix multiplication. Entry $(i, k)$ of $AB$ takes $\orange{\text{row } i \text{ of } A}$ and "
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
         "formula": r"\green{(AB)_{ii}} = \sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{ji}}",
         "picture": _A_ROW1 + r" \cdot " + _B_COL1 + r" = \begin{bmatrix} \green{(AB)_{11}} & \cdot \\ \cdot & \cdot \end{bmatrix}",
         "expansion": r"\green{(AB)_{11}} = " + _ab(1),
         "caption": r"Row 1 of $A$ meets column 1 of $B$ and gives the first diagonal entry.",
         "meaning": r"The diagonal entry $\green{(AB)_{11}}$ comes from $\orange{\text{row 1 of } A}$ and "
                    r"$\blue{\text{column 1 of } B}$. Pair them up entry by entry, multiply and add. In every "
                    r"product the $A$ entry is $a_{ij}$ and its partner in $B$ is $b_{ji}$: the same two indices, swapped."},
        {"title": "Add up the whole diagonal of $AB$",
         "uses": "(D2) and step 1",
         "formula": r"\operatorname{Trace}(AB) = \sum_{i=1}^{n} \green{(AB)_{ii}} = \sum_{i=1}^{n}\sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{ji}}",
         "picture": r"\begin{bmatrix} \green{(AB)_{11}} & \cdot \\ \cdot & \green{(AB)_{22}} \end{bmatrix} "
                    r"\;\longrightarrow\; \operatorname{Trace}(AB) = \green{(AB)_{11}} + \green{(AB)_{22}}",
         "caption": "The trace keeps only the diagonal of $AB$.",
         "expansion": r"\begin{aligned} \green{(AB)_{11}} &= " + _ab(1) + r" \\ \green{(AB)_{22}} &= " + _ab(2) + r" \end{aligned}",
         "meaning": r"The trace adds the $\green{\text{diagonal entries}}$, and each one is the sum from step 1. "
                    r"So $\operatorname{Trace}(AB)$ is just a list of products: every entry $\orange{a_{ij}}$ of $A$ "
                    r"times its partner $\blue{b_{ji}}$. Here that's 6 products, one for each entry of $A$."},
        {"title": "Do the same for $BA$",
         "uses": "(D2) and (D3) with the roles of $A$ and $B$ swapped",
         "formula": r"\operatorname{Trace}(BA) = \sum_{j=1}^{m} \green{(BA)_{jj}} = \sum_{j=1}^{m}\sum_{i=1}^{n} \blue{b_{ji}}\,\orange{a_{ij}}",
         "picture": _B_ROW1 + r" \cdot " + _A_COL1 + r" = \begin{bmatrix} \green{(BA)_{11}} & \cdot & \cdot \\ "
                    r"\cdot & \green{(BA)_{22}} & \cdot \\ \cdot & \cdot & \green{(BA)_{33}} \end{bmatrix}",
         "caption": "$BA$ is $3 \\times 3$, so its diagonal has three entries.",
         "expansion": r"\begin{aligned} \green{(BA)_{11}} &= " + _ba(1) + r" \\ \green{(BA)_{22}} &= " + _ba(2)
                      + r" \\ \green{(BA)_{33}} &= " + _ba(3) + r" \end{aligned}",
         "meaning": r"Now $B$ comes first, so each diagonal entry $\green{(BA)_{jj}}$ takes $\blue{\text{row } j \text{ of } B}$ "
                    r"and $\orange{\text{column } j \text{ of } A}$. $BA$ is $3 \times 3$, so its diagonal has three entries "
                    r"instead of two, but look at the products: they're the same 6 pairs as in step 2."},
        {"title": "Compare the two sums",
         "uses": "steps 2 and 3",
         "formula": r"\hl{\sum_{i=1}^{n}\sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{ji}} = \sum_{j=1}^{m}\sum_{i=1}^{n} \blue{b_{ji}}\,\orange{a_{ij}}}",
         "picture": r"\begin{array}{cc|cc} \text{in } \operatorname{Trace}(AB) & \text{found in} & \text{in } \operatorname{Trace}(BA) & \text{found in} \\ \hline "
                    + r" \\ ".join(
                        rf"\orange{{a_{{{i}{j}}}}}\blue{{b_{{{j}{i}}}}} & (AB)_{{{i}{i}}} & \blue{{b_{{{j}{i}}}}}\orange{{a_{{{i}{j}}}}} & (BA)_{{{j}{j}}}"
                        for i in (1, 2) for j in (1, 2, 3))
                    + r" \end{array}",
         "caption": "Every product in one trace appears exactly once in the other.",
         "meaning": r"Both traces add up exactly the same 6 products. Each $\orange{a}\blue{b}$ equals its $\blue{b}\orange{a}$ "
                    r"because ordinary numbers commute. They're only grouped differently: $\operatorname{Trace}(AB)$ groups "
                    r"them by the $\green{\text{2 diagonal entries of } AB}$, $\operatorname{Trace}(BA)$ by the "
                    r"$\green{\text{3 diagonal entries of } BA}$. A finite sum doesn't depend on how you group or order it, "
                    r"so the two totals are equal."},
    ],
    "solution": {
        "intro": r"Let $\orange{A} \in \mathbb{R}^{n\times m}$ and $\blue{B} \in \mathbb{R}^{m\times n}$, with entries $a_{ij}$ and $b_{ji}$.",
        "steps": [
            {"text": "By the definition of matrix multiplication, each diagonal entry of $AB$ is",
             "formula": r"\green{(AB)_{ii}} = \sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{ji}}."},
            {"text": "Adding the diagonal entries gives",
             "formula": r"\operatorname{Trace}(AB) = \sum_{i=1}^{n}\sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{ji}}."},
            {"text": r"In the same way, $(BA)_{jj} = \sum_i b_{ji}a_{ij}$, so",
             "formula": r"\operatorname{Trace}(BA) = \sum_{j=1}^{m}\sum_{i=1}^{n} \blue{b_{ji}}\,\orange{a_{ij}}."},
            {"text": r"Since $b_{ji}a_{ij} = a_{ij}b_{ji}$ and both are finite sums over the same pairs $(i, j)$, "
                     r"the order of summation can be swapped:",
             "formula": r"\sum_{j=1}^{m}\sum_{i=1}^{n} b_{ji}a_{ij} = \sum_{i=1}^{n}\sum_{j=1}^{m} a_{ij}b_{ji}."},
            {"text": r"By steps 2 to 4, $\operatorname{Trace}(AB) = \operatorname{Trace}(BA)$. $\blacksquare$"},
        ],
        "key_idea": r"Both traces are the same finite sum of the products $a_{ij}b_{ji}$, just grouped differently.",
        "watch_out": r"$AB$ and $BA$ are usually different matrices, here even different sizes. Only their traces agree.",
    },
    "answer": r"\operatorname{Trace}(AB) = \sum_{i,j} a_{ij}b_{ji} = \operatorname{Trace}(BA)",
}


# A multiple-choice exam question: the options table at the end checks every answer.
PURITY_NOTES = {
    "title": "Purity gain of a split",
    "asked": "Question 12. At the root of a decision tree there are 400 examples from class 1 and 100 from class 2. "
             "A split along x4 gives branch v1 with 175 (class 1) and 75 (class 2), and branch v2 with 225 and 25. "
             "Which expression computes the purity gain Δ = I(r) − Σ N(v_k)/N(r) I(v_k) with the entropy impurity? "
             "The solution says B. Why not C? C also has the root and both branches.",
    "short_answer": r"C leaves out the weights $\frac{N(v_k)}{N(r)} = \frac12$. Write the definition out with the "
                    r"counts and option B appears line by line.",
    "colors": [
        {"color": "blue", "meaning": "class 1"},
        {"color": "orange", "meaning": "class 2"},
        {"color": "green", "meaning": "the purity gain"},
    ],
    "have": [
        {"label": "D1", "formula": r"\Delta = I(r) - \sum_{k=1}^{K}\frac{N(v_k)}{N(r)}\,I(v_k)",
         "meaning": "The purity gain: the impurity at the root minus the weighted impurity of the branches."},
        {"label": "D2", "formula": r"I(z) = -\sum_{c=1}^{2} p(c\mid z)\log_2 p(c\mid z)",
         "meaning": "The entropy of a node, from the share of each class in it."},
        {"label": "D3", "formula": r"r:\ (\blue{400}, \orange{100}),\quad v_1:\ (\blue{175}, \orange{75}),\quad v_2:\ (\blue{225}, \orange{25})",
         "meaning": r"The counts of $\blue{\text{class 1}}$ and $\orange{\text{class 2}}$ in each node."},
    ],
    "goal": {"formula": r"\Delta \text{ written with sums of } p(c\mid\cdot)\log_2 p(c\mid\cdot)",
             "meaning": "Find which option equals the purity gain, and check it with the numbers."},
    "steps": [
        {"title": "Read off the probabilities", "uses": "(D3)",
         "formula": r"\begin{aligned} p(\cdot\mid r) &= \left(\tfrac{400}{500}, \tfrac{100}{500}\right) = (\blue{0.8}, \orange{0.2})\\ "
                    r"p(\cdot\mid v_1) &= \left(\tfrac{175}{250}, \tfrac{75}{250}\right) = (\blue{0.7}, \orange{0.3})\\ "
                    r"p(\cdot\mid v_2) &= \left(\tfrac{225}{250}, \tfrac{25}{250}\right) = (\blue{0.9}, \orange{0.1}) \end{aligned}",
         "picture": r"\begin{array}{l|cc|c} & \blue{\text{class }1} & \orange{\text{class }2} & N \\ \hline "
                    r"r & 400 & 100 & 500 \\ v_1 & 175 & 75 & 250 \\ v_2 & 225 & 25 & 250 \end{array}",
         "caption": "The counts. Each branch holds 250 of the 500 observations.",
         "meaning": "Divide each count by the size of its own node: 250 for a branch, not 500."},
        {"title": "Weight each branch by its size", "uses": "(D1) with $K = 2$",
         "formula": r"\frac{N(v_1)}{N(r)} = \frac{N(v_2)}{N(r)} = \frac{250}{500} = \frac12 "
                    r"\quad\Longrightarrow\quad \hl{\Delta = I(r) - \tfrac12 I(v_1) - \tfrac12 I(v_2)}",
         "meaning": "The weights are the share of the observations each branch gets, and they add up to 1. "
                    "This is the part option C forgets."},
        {"title": "Entropy of each node", "uses": "(D2) and step 1",
         "formula": r"\begin{aligned} I(r) &= -(0.8\log_2 0.8 + 0.2\log_2 0.2) = 0.722\\ "
                    r"I(v_1) &= -(0.7\log_2 0.7 + 0.3\log_2 0.3) = 0.881\\ "
                    r"I(v_2) &= -(0.9\log_2 0.9 + 0.1\log_2 0.1) = 0.469 \end{aligned}",
         "meaning": "$v_2$ is the purest node (90% class 1), so it has the lowest entropy."},
        {"title": "Compute the gain", "uses": "steps 2 and 3",
         "formula": r"\begin{aligned} \Delta &= 0.722 - \tfrac12(0.881) - \tfrac12(0.469)\\ &= 0.722 - 0.675 = \green{0.047} \end{aligned}",
         "meaning": "The gain is positive: after the split the nodes are purer on average. With entropy it can never be negative."},
        {"title": "Write it with sums", "uses": "step 2 and (D2)",
         "formula": r"\begin{aligned} \Delta &= -\sum_{c} p(c\mid r)\log_2 p(c\mid r)\\ "
                    r"&\qquad - \tfrac12\Big(-\sum_{c} p(c\mid v_1)\log_2 p(c\mid v_1)\Big)\\ "
                    r"&\qquad - \tfrac12\Big(-\sum_{c} p(c\mid v_2)\log_2 p(c\mid v_2)\Big) \end{aligned}",
         "expansion": r"\begin{aligned} \Delta = \sum_{c=1}^{2}\Big(&-p(c\mid r)\log_2 p(c\mid r)\\ "
                      r"&+ \tfrac12\, p(c\mid v_1)\log_2 p(c\mid v_1)\\ &+ \tfrac12\, p(c\mid v_2)\log_2 p(c\mid v_2)\Big) \end{aligned}",
         "meaning": r"Each $-\tfrac12$ meets the minus sign inside $I$ and becomes $+\tfrac12$. That is option B."},
    ],
    "solution": {
        "steps": [
            {"text": "Both branches hold 250 of the 500 observations, so by the definition of the purity gain",
             "formula": r"\Delta = I(r) - \tfrac12 I(v_1) - \tfrac12 I(v_2)."},
            {"text": r"Inserting the entropy $I(z) = -\sum_c p(c\mid z)\log_2 p(c\mid z)$ gives option B:",
             "formula": r"\begin{aligned} \Delta = \sum_{c=1}^{2}\Big(&-p(c\mid r)\log_2 p(c\mid r) + \tfrac12\, p(c\mid v_1)\log_2 p(c\mid v_1)\\ "
                        r"&+ \tfrac12\, p(c\mid v_2)\log_2 p(c\mid v_2)\Big). \end{aligned}"},
            {"text": r"With the numbers, $\Delta = 0.722 - \tfrac12(0.881) - \tfrac12(0.469) = 0.047 > 0$."},
        ],
        "key_idea": r"The branches are weighted by their share of the data, $\frac{N(v_k)}{N(r)}$.",
        "watch_out": "The minus sign in front of each branch cancels the minus sign inside the entropy.",
    },
    "options": [
        {"option": "A", "computes": r"I(r) + I(v_1)", "value": "1.603", "correct": False,
         "verdict": "Adds $v_1$, drops $v_2$ and the weights."},
        {"option": "B", "computes": r"I(r) - \tfrac12 I(v_1) - \tfrac12 I(v_2)", "value": "0.047", "correct": True,
         "verdict": r"The definition with both weights equal to $\frac12$."},
        {"option": "C", "computes": r"I(r) - I(v_1) - I(v_2)", "value": "−0.628", "correct": False,
         "verdict": r"Weights 1 instead of $\frac12$, so the gain goes negative."},
        {"option": "D", "computes": r"I(v_1) + I(v_2)", "value": "1.350", "correct": False,
         "verdict": "No root term."},
    ],
    "answer": r"\text{B}:\quad \Delta = I(r) - \tfrac12 I(v_1) - \tfrac12 I(v_2) \approx 0.047",
}
