"""Example study notes, written the way Ginger writes them with write_study_notes.

`python -m catagent.notepad [trace|purity|roll|ribo]` opens the Notepad with one of these, so you
can try it without a model.
"""

# ---- a proof: Trace(AB) = Trace(BA) ---------------------------------------------------------

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
    "answer": {
        "result": r"\operatorname{Trace}(AB) = \sum_{i=1}^{n}\sum_{j=1}^{m} a_{ij}\,b_{ji} = \operatorname{Trace}(BA)",
        "text": r"Write both traces out as sums of products $\orange{a_{ij}}\blue{b_{ji}}$. They turn out to be the "
                r"same products, only added in a different order.",
    },
    "colors": [
        {"color": "orange", "meaning": "entries of $A$"},
        {"color": "blue", "meaning": "entries of $B$"},
        {"color": "green", "meaning": "diagonal entries, the ones the trace adds up"},
    ],
    "given": [
        {"symbol": r"\orange{A} \in \mathbb{R}^{n\times m}", "meaning": r"an $n \times m$ matrix with entries $\orange{a_{ij}}$"},
        {"symbol": r"\blue{B} \in \mathbb{R}^{m\times n}", "meaning": r"an $m \times n$ matrix with entries $\blue{b_{ji}}$"},
        {"symbol": r"AB \in \mathbb{R}^{n\times n},\ BA \in \mathbb{R}^{m\times m}",
         "meaning": "both products are square, but usually of different sizes"},
    ],
    "find": {"formula": r"\operatorname{Trace}(AB) = \operatorname{Trace}(BA)",
             "meaning": "Show that the diagonals of $AB$ and $BA$ add up to the same number, for every $n$ and $m$."},
    "methods": [
        {"id": "M1", "name": "Matrix multiplication",
         "formula": r"(AB)_{ik} = \sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{jk}}",
         "says": r"Entry $(i, k)$ of $AB$ pairs $\orange{\text{row } i \text{ of } A}$ with $\blue{\text{column } k \text{ of } B}$, "
                 r"multiplies them entry by entry and adds. The index $j$ walks along both.",
         "why": "The trace only needs the diagonal entries of $AB$ and $BA$, and this is how to write them out."},
        {"id": "M2", "name": "The trace",
         "formula": r"\operatorname{Trace}(M) = \sum_{i} \green{M_{ii}}",
         "says": r"Add up the $\green{\text{diagonal entries}}$, where the row number equals the column number.",
         "why": "It turns each trace into a sum we can compare term by term."},
        {"id": "M3", "name": "Reordering a finite sum",
         "formula": r"\sum_{i}\sum_{j} x_{ij} = \sum_{j}\sum_{i} x_{ij}, \qquad ab = ba",
         "says": "A finite sum gives the same total in any order or grouping, and two numbers can be multiplied in either order.",
         "why": "The two traces will turn out to be the same double sum, written in a different order."},
    ],
    "plan": r"Write each trace as a double sum of products (M1, M2), then show both sums contain exactly the "
            r"same terms (M3). The example uses $n = 2$ and $m = 3$, with colours matching the formulas.",
    "solution": [
        {"title": "One diagonal entry of $AB$",
         "uses": ["M1"],
         "work": r"\green{(AB)_{ii}} = \sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{ji}}",
         "expansion": r"\green{(AB)_{11}} = " + _ab(1),
         "picture": _A_ROW1 + r" \cdot " + _B_COL1 + r" = \begin{bmatrix} \green{(AB)_{11}} & \cdot \\ \cdot & \cdot \end{bmatrix}",
         "caption": r"Row 1 of $A$ meets column 1 of $B$ and gives the first diagonal entry.",
         "result": r"\green{(AB)_{ii}} = \sum_j \orange{a_{ij}}\,\blue{b_{ji}}",
         "explain": r"Put $k = i$ in matrix multiplication. In every product the $A$ entry is $a_{ij}$ and its partner "
                    r"in $B$ is $b_{ji}$: the same two indices, swapped."},
        {"title": "The trace of $AB$",
         "uses": ["M2", "M1"],
         "work": r"\operatorname{Trace}(AB) = \sum_{i=1}^{n} \green{(AB)_{ii}} = \sum_{i=1}^{n}\sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{ji}}",
         "expansion": r"\begin{aligned} \green{(AB)_{11}} &= " + _ab(1) + r" \\ \green{(AB)_{22}} &= " + _ab(2) + r" \end{aligned}",
         "result": r"\operatorname{Trace}(AB) = \sum_{i}\sum_{j} a_{ij}\,b_{ji}",
         "explain": r"The trace adds the $n$ diagonal entries, and each is the sum above. So $\operatorname{Trace}(AB)$ "
                    r"is a list of products: every entry $\orange{a_{ij}}$ of $A$ times its partner $\blue{b_{ji}}$, here 6 of them."},
        {"title": "The trace of $BA$",
         "uses": ["M2", "M1"],
         "work": r"\operatorname{Trace}(BA) = \sum_{j=1}^{m} \green{(BA)_{jj}} = \sum_{j=1}^{m}\sum_{i=1}^{n} \blue{b_{ji}}\,\orange{a_{ij}}",
         "expansion": r"\begin{aligned} \green{(BA)_{11}} &= " + _ba(1) + r" \\ \green{(BA)_{22}} &= " + _ba(2)
                      + r" \\ \green{(BA)_{33}} &= " + _ba(3) + r" \end{aligned}",
         "picture": _B_ROW1 + r" \cdot " + _A_COL1 + r" = \begin{bmatrix} \green{(BA)_{11}} & \cdot & \cdot \\ "
                    r"\cdot & \green{(BA)_{22}} & \cdot \\ \cdot & \cdot & \green{(BA)_{33}} \end{bmatrix}",
         "caption": r"$BA$ is $3 \times 3$, so its diagonal has three entries.",
         "result": r"\operatorname{Trace}(BA) = \sum_{j}\sum_{i} b_{ji}\,a_{ij}",
         "explain": r"The same two methods with $B$ first. $BA$ is $m \times m$, so its diagonal has $m$ entries instead of $n$, "
                    r"but look at the products: they are the same 6 pairs."},
        {"title": "The two sums are the same",
         "uses": ["M3"],
         "work": r"\hl{\sum_{i=1}^{n}\sum_{j=1}^{m} \orange{a_{ij}}\,\blue{b_{ji}} = \sum_{j=1}^{m}\sum_{i=1}^{n} \blue{b_{ji}}\,\orange{a_{ij}}}",
         "picture": r"\begin{array}{cc|cc} \text{in } \operatorname{Trace}(AB) & \text{found in} & \text{in } \operatorname{Trace}(BA) & \text{found in} \\ \hline "
                    + r" \\ ".join(
                        rf"\orange{{a_{{{i}{j}}}}}\blue{{b_{{{j}{i}}}}} & (AB)_{{{i}{i}}} & \blue{{b_{{{j}{i}}}}}\orange{{a_{{{i}{j}}}}} & (BA)_{{{j}{j}}}"
                        for i in (1, 2) for j in (1, 2, 3))
                    + r" \end{array}",
         "caption": "Every product in one trace appears exactly once in the other.",
         "result": r"\operatorname{Trace}(AB) = \operatorname{Trace}(BA)",
         "explain": r"Each $\orange{a}\blue{b}$ equals its $\blue{b}\orange{a}$, and both sums run over the same pairs $(i, j)$. "
                    r"They are only grouped differently: by the 2 diagonal entries of $AB$, or by the 3 of $BA$."},
    ],
    "checks": [
        r"With $n = m = 1$ both sides are $a_{11}b_{11}$.",
        r"$\operatorname{Trace}(AB)$ adds $n$ diagonal entries and $\operatorname{Trace}(BA)$ adds $m$, "
        r"yet both contain the same $nm$ products.",
    ],
    "takeaways": {
        "key_idea": r"Both traces are the same finite sum of the products $a_{ij}b_{ji}$, just grouped differently.",
        "mistakes": [
            r"Concluding that $AB = BA$: they are usually different matrices, here even different sizes. Only their traces agree.",
            r"Pairing the wrong entries: in $(AB)_{ii}$ the partner of $a_{ij}$ is $b_{ji}$, not $b_{ij}$.",
        ],
    },
    "exam": [
        {"text": r"Let $A \in \mathbb{R}^{n\times m}$ and $B \in \mathbb{R}^{m\times n}$. By the definition of matrix "
                 r"multiplication, each diagonal entry of $AB$ is",
         "formula": r"(AB)_{ii} = \sum_{j=1}^{m} a_{ij}\,b_{ji}, \quad\text{so}\quad \operatorname{Trace}(AB) = \sum_{i=1}^{n}\sum_{j=1}^{m} a_{ij}\,b_{ji}."},
        {"text": r"In the same way, $(BA)_{jj} = \sum_i b_{ji}a_{ij}$, so",
         "formula": r"\operatorname{Trace}(BA) = \sum_{j=1}^{m}\sum_{i=1}^{n} b_{ji}\,a_{ij}."},
        {"text": r"Since $b_{ji}a_{ij} = a_{ij}b_{ji}$ and both are finite sums over the same pairs $(i, j)$, the order of "
                 r"summation can be swapped, so $\operatorname{Trace}(AB) = \operatorname{Trace}(BA)$. $\blacksquare$"},
    ],
}


# ---- multiple choice: the purity gain of a split ---------------------------------------------

PURITY_NOTES = {
    "title": "Purity gain of a split",
    "asked": "Question 12. At the root of a decision tree there are 400 examples from class 1 and 100 from class 2. "
             "A split along x4 gives branch v1 with 175 (class 1) and 75 (class 2), and branch v2 with 225 and 25. "
             "Which expression computes the purity gain Δ = I(r) − Σ N(v_k)/N(r) I(v_k) with the entropy impurity? "
             "The solution says B. Why not C? C also has the root and both branches.",
    "answer": {
        "result": r"\text{B}:\quad \Delta = I(r) - \tfrac12 I(v_1) - \tfrac12 I(v_2) \approx 0.047",
        "text": r"C leaves out the weights $\frac{N(v_k)}{N(r)} = \frac12$. Write the definition out with the counts "
                r"and option B appears line by line.",
    },
    "colors": [
        {"color": "blue", "meaning": "class 1"},
        {"color": "orange", "meaning": "class 2"},
        {"color": "green", "meaning": "the purity gain"},
    ],
    "given": [
        {"symbol": "r", "value": r"(\blue{400}, \orange{100})", "meaning": "the root: 500 examples"},
        {"symbol": "v_1", "value": r"(\blue{175}, \orange{75})", "meaning": "the first branch: 250 examples"},
        {"symbol": "v_2", "value": r"(\blue{225}, \orange{25})", "meaning": "the second branch: 250 examples"},
        {"symbol": "I", "meaning": "the impurity measure, here entropy"},
    ],
    "find": {"formula": r"\green{\Delta}", "meaning": "Which option is the purity gain of this split, and why the others aren't."},
    "methods": [
        {"id": "M1", "name": "Class probabilities in a node",
         "formula": r"p(c \mid z) = \frac{N_c(z)}{N(z)}",
         "says": r"The share of node $z$'s examples that belong to class $c$.",
         "why": "Entropy is computed from these shares, not from the raw counts."},
        {"id": "M2", "name": "Purity gain",
         "formula": r"\Delta = I(r) - \sum_{k=1}^{K}\frac{N(v_k)}{N(r)}\,I(v_k)",
         "says": "The impurity at the root minus the impurity of the branches, each weighted by its share of the examples.",
         "why": "It is the quantity the question asks for; the weights are what separates B from C."},
        {"id": "M3", "name": "Entropy",
         "formula": r"I(z) = -\sum_{c=1}^{2} p(c\mid z)\,\log_2 p(c\mid z)",
         "says": "How mixed a node is: 0 when it holds one class only, 1 for a 50/50 mix of two classes.",
         "why": "The question uses entropy as the impurity measure."},
    ],
    "plan": "Turn the counts into class shares (M1), work out the branch weights in the purity gain (M2), write the "
            "entropy in (M3) and match the result to an option. Then check it with the numbers.",
    "solution": [
        {"title": "Class shares in each node",
         "uses": ["M1"],
         "work": r"\begin{aligned} p(\cdot\mid r) &= \left(\tfrac{400}{500}, \tfrac{100}{500}\right) = (\blue{0.8}, \orange{0.2})\\ "
                 r"p(\cdot\mid v_1) &= \left(\tfrac{175}{250}, \tfrac{75}{250}\right) = (\blue{0.7}, \orange{0.3})\\ "
                 r"p(\cdot\mid v_2) &= \left(\tfrac{225}{250}, \tfrac{25}{250}\right) = (\blue{0.9}, \orange{0.1}) \end{aligned}",
         "picture": r"\begin{array}{l|cc|c} & \blue{\text{class }1} & \orange{\text{class }2} & N \\ \hline "
                    r"r & 400 & 100 & 500 \\ v_1 & 175 & 75 & 250 \\ v_2 & 225 & 25 & 250 \end{array}",
         "caption": "The counts. Each branch holds 250 of the 500 examples.",
         "result": r"(0.8, 0.2),\ (0.7, 0.3),\ (0.9, 0.1)",
         "explain": "Divide each count by the size of its own node: 250 for a branch, not 500."},
        {"title": "The branch weights",
         "uses": ["M2"],
         "work": r"\begin{aligned} \frac{N(v_1)}{N(r)} &= \frac{N(v_2)}{N(r)} = \frac{250}{500} = \frac12\\[4pt] "
                 r"\Delta &= I(r) - \tfrac12 I(v_1) - \tfrac12 I(v_2) \end{aligned}",
         "result": r"\hl{\Delta = I(r) - \tfrac12 I(v_1) - \tfrac12 I(v_2)}",
         "explain": "Each branch gets half the examples, so each is weighted by $\\frac12$. The weights always add up to 1: "
                    "this is the part option C forgets."},
        {"title": "The gain written with sums",
         "uses": ["M2", "M3"],
         "work": r"\begin{aligned} \Delta &= -\sum_{c} p(c\mid r)\log_2 p(c\mid r)\\ "
                 r"&\qquad - \tfrac12\Big(-\sum_{c} p(c\mid v_1)\log_2 p(c\mid v_1)\Big)\\ "
                 r"&\qquad - \tfrac12\Big(-\sum_{c} p(c\mid v_2)\log_2 p(c\mid v_2)\Big) \end{aligned}",
         "expansion": r"\begin{aligned} \Delta = \sum_{c=1}^{2}\Big(&-p(c\mid r)\log_2 p(c\mid r)\\ "
                      r"&+ \tfrac12\, p(c\mid v_1)\log_2 p(c\mid v_1)\\ &+ \tfrac12\, p(c\mid v_2)\log_2 p(c\mid v_2)\Big) \end{aligned}",
         "result": r"\text{option B}",
         "explain": r"Each $-\tfrac12$ meets the minus sign inside the entropy and becomes $+\tfrac12$. Collecting "
                    r"everything under one sum gives B exactly."},
        {"title": "The value of the gain",
         "uses": ["M3"],
         "work": r"\begin{aligned} I(r) &= -(0.8\log_2 0.8 + 0.2\log_2 0.2) = 0.722\\ "
                 r"I(v_1) &= -(0.7\log_2 0.7 + 0.3\log_2 0.3) = 0.881\\ "
                 r"I(v_2) &= -(0.9\log_2 0.9 + 0.1\log_2 0.1) = 0.469\\ "
                 r"\Delta &= 0.722 - \tfrac12(0.881) - \tfrac12(0.469) = \green{0.047} \end{aligned}",
         "result": r"\green{\Delta \approx 0.047}",
         "explain": "$v_2$ is the purest node (90% class 1), so it has the lowest entropy. The gain is positive: after "
                    "the split the nodes are purer on average."},
    ],
    "checks": [
        r"$\Delta = 0.047 > 0$. With entropy and weights that add up to 1, a gain can never be negative.",
        r"Option C gives $0.722 - 0.881 - 0.469 = -0.628$, which is impossible for a gain.",
    ],
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
    "takeaways": {
        "key_idea": r"The branches are weighted by their share of the examples, $\frac{N(v_k)}{N(r)}$.",
        "mistakes": [
            "Dropping the weights, as option C does.",
            r"Losing a sign: $-\tfrac12 I(v)$ becomes $+\tfrac12\sum p\log_2 p$, because the entropy has its own minus sign.",
        ],
    },
    "exam": [
        {"text": "Both branches hold 250 of the 500 examples, so by the definition of the purity gain",
         "formula": r"\Delta = I(r) - \tfrac12 I(v_1) - \tfrac12 I(v_2)."},
        {"text": r"Inserting the entropy $I(z) = -\sum_c p(c\mid z)\log_2 p(c\mid z)$ gives option B:",
         "formula": r"\begin{aligned} \Delta = \sum_{c=1}^{2}\Big(&-p(c\mid r)\log_2 p(c\mid r) + \tfrac12\, p(c\mid v_1)\log_2 p(c\mid v_1)\\ "
                    r"&+ \tfrac12\, p(c\mid v_2)\log_2 p(c\mid v_2)\Big). \end{aligned}"},
        {"text": r"With the numbers, $\Delta = 0.722 - \tfrac12(0.881) - \tfrac12(0.469) = 0.047 > 0$."},
    ],
}


# ---- physics with several formulas: a rolling ball, a ramp and a jump ------------------------

ROLL_NOTES = {
    "title": "Launch speed for a rolling ball",
    "asked": "A small, solid, uniform ball is shot from point P so that it rolls smoothly along a horizontal path, "
             "up a ramp and onto a plateau. Then it leaves the plateau horizontally and lands on a game board a "
             "horizontal distance d from the edge. h1 = 5.00 cm, h2 = 1.60 cm. With what speed must it be shot at P "
             "to land at d = 6.00 cm?",
    "answer": {
        "result": r"v_P = \sqrt{v^2 + \tfrac{10}{7}\, g h_1} \approx 1.34\ \text{m/s}",
        "text": r"Work backwards. The jump fixes the speed at the edge, $v = 1.05$ m/s. Energy conservation for a "
                r"rolling ball, whose kinetic energy is $\tfrac{7}{10}Mv^2$, then takes you back to $P$.",
    },
    "colors": [
        {"color": "blue", "meaning": "energy of moving forward"},
        {"color": "purple", "meaning": "energy of spinning"},
        {"color": "green", "meaning": "height (potential energy)"},
    ],
    "given": [
        {"symbol": "h_1", "value": r"0.0500\ \text{m}", "meaning": "the climb from the path at $P$ up to the plateau"},
        {"symbol": "h_2", "value": r"0.0160\ \text{m}", "meaning": "the drop from the plateau to the game board"},
        {"symbol": "d", "value": r"0.0600\ \text{m}", "meaning": "how far from the edge the ball must land"},
        {"symbol": "g", "value": r"9.8\ \text{m/s}^2", "meaning": "gravity"},
        {"symbol": r"\text{ball}", "meaning": "small, solid and uniform; it rolls without slipping until it leaves the plateau"},
    ],
    "find": {"formula": r"v_P", "meaning": "The speed the ball needs at $P$."},
    "methods": [
        {"id": "M1", "name": "Horizontal launch",
         "formula": r"x = v\,t, \qquad y = \tfrac12\, g\, t^2",
         "says": r"Across, the speed $v$ stays the same. Downwards, the ball starts from rest and falls a distance $y$ in time $t$.",
         "why": r"The ball leaves the plateau horizontally: the drop $h_2$ fixes the flight time, and $d$ then fixes the speed."},
        {"id": "M2", "name": "Kinetic energy of a rolling body",
         "formula": r"K = \blue{\tfrac12 M v^2} + \purple{\tfrac12 I \omega^2}",
         "says": r"A rolling body carries energy by moving forward ($M$, $v$) and by spinning ($I$, $\omega$).",
         "why": "The ball rolls, so part of its energy is spin. Leaving it out is the classic mistake."},
        {"id": "M3", "name": "Rolling without slipping",
         "formula": r"v = \omega R",
         "says": r"The point touching the ground doesn't slide, so the spin rate $\omega$ is tied to the speed $v$ by the radius $R$.",
         "why": r"It lets us write the spin energy in terms of $v$."},
        {"id": "M4", "name": "Moment of inertia of a solid ball",
         "formula": r"I = \tfrac25\, M R^2",
         "says": "How hard a solid, uniform ball is to spin up, for mass $M$ and radius $R$.",
         "why": "The ball is solid and uniform."},
        {"id": "M5", "name": "Conservation of mechanical energy",
         "formula": r"K_1 + U_1 = K_2 + U_2, \qquad \green{U = M g h}",
         "says": "With no slipping and no air drag, kinetic plus potential energy stays the same.",
         "why": r"Between $P$ and the edge the ball only rolls and climbs $h_1$, so no energy is lost."},
    ],
    "plan": r"Solve the end first: the jump gives the speed at the edge (M1). Then find the kinetic energy of a "
            r"rolling ball (M2, M3, M4), and use energy conservation from $P$ to the edge (M5) to get $v_P$.",
    "solution": [
        {"title": "Speed at the edge",
         "uses": ["M1"],
         "work": r"\begin{aligned} h_2 = \tfrac12 g t^2 \;&\Rightarrow\; t = \sqrt{\frac{2h_2}{g}} = \sqrt{\frac{2(0.0160)}{9.8}} = 0.0571\ \text{s}\\[2pt] "
                 r"d = v\,t \;&\Rightarrow\; v = \frac{d}{t} = \frac{0.0600}{0.0571} = 1.05\ \text{m/s} \end{aligned}",
         "result": r"v = 1.05\ \text{m/s}",
         "explain": r"The ball leaves horizontally, so it falls $h_2$ from rest: that alone sets the flight time. "
                    r"In that time it must cover $d$ sideways."},
        {"title": "Kinetic energy of the rolling ball",
         "uses": ["M2", "M3", "M4"],
         "work": r"\begin{aligned} K &= \blue{\tfrac12 M v^2} + \purple{\tfrac12 \big(\tfrac25 M R^2\big)\big(\tfrac{v}{R}\big)^2}\\[2pt] "
                 r"&= \blue{\tfrac{5}{10} M v^2} + \purple{\tfrac{2}{10} M v^2} \end{aligned}",
         "result": r"\hl{K = \tfrac{7}{10}\, M v^2}",
         "explain": r"The radius cancels, so the size of the ball doesn't matter. Two sevenths of the kinetic energy is spin."},
        {"title": "Speed at $P$",
         "uses": ["M5", "M2"],
         "work": r"\begin{aligned} \tfrac{7}{10} M v_P^2 &= \tfrac{7}{10} M v^2 + \green{M g h_1}\\[2pt] "
                 r"v_P^2 &= v^2 + \tfrac{10}{7}\, g h_1 = (1.05)^2 + \tfrac{10}{7}(9.8)(0.0500)\\[2pt] "
                 r"&= 1.1025 + 0.700 = 1.8025\ \text{m}^2/\text{s}^2 \end{aligned}",
         "result": r"\hl{v_P \approx 1.34\ \text{m/s}}",
         "explain": r"Take $U = 0$ on the path. At $P$ all the energy is kinetic; at the edge part of it has become "
                    r"height. The mass cancels too."},
    ],
    "checks": [
        r"$v_P = 1.34 > v = 1.05$ m/s: the ball must be faster at $P$, because it slows down while climbing $h_1$.",
        r"Units: $\sqrt{(\text{m/s})^2 + (\text{m/s}^2)(\text{m})} = \text{m/s}$.",
        r"Without the spin ($K = \tfrac12 M v^2$) you'd get $1.44$ m/s. Rolling needs less, because the spin energy also pays for the climb.",
    ],
    "takeaways": {
        "key_idea": r"Solve the end of the trip first, then go back with energy, remembering that a rolling ball's "
                    r"kinetic energy is $\tfrac{7}{10}Mv^2$, not $\tfrac12 Mv^2$.",
        "mistakes": [
            r"Leaving out the spin energy, which gives $1.44$ m/s.",
            r"Mixing up the heights: $h_2$ is the drop for the jump, $h_1$ the climb for energy conservation.",
            "Converting centimetres in some places only: put every length in metres first.",
        ],
    },
    "exam": [
        {"text": r"Jump, launched horizontally from height $h_2$:",
         "formula": r"t = \sqrt{2h_2/g} = 0.0571\ \text{s}, \qquad v = d/t = 1.05\ \text{m/s}."},
        {"text": r"Rolling without slipping, with $I = \tfrac25 MR^2$ and $\omega = v/R$:",
         "formula": r"K = \tfrac12 Mv^2 + \tfrac12 I\omega^2 = \tfrac{7}{10}Mv^2."},
        {"text": r"Energy conservation from $P$ to the edge, rising $h_1$:",
         "formula": r"\tfrac{7}{10}Mv_P^2 = \tfrac{7}{10}Mv^2 + Mgh_1 \;\Rightarrow\; v_P = \sqrt{v^2 + \tfrac{10}{7}gh_1} = 1.34\ \text{m/s}."},
    ],
}


# ---- biology with figures the Notepad draws: translational sequestering ----------------------
# A real 3D riboswitch, and a model riboswitch that refolds. The model is the 4FEO aptamer (PDB
# numbering 15-81 becomes 1-67 here) followed by a designed expression platform: the anti-SD
# (64-71) overlaps P1's 3' strand, then SD and AUG.

_APTAMER = "GGACAUAUAAACGCGUGGAUAUGGCACGCGAGUUUCUACCGGGCACCGUAAAUGUCCGAUUAUGUCC"
_RIBO_SEQ = _APTAMER + "UCCU" + "AAUAAUA" + "AGGAGGAC" + "UUAAAAUG" + "GCUAAAGAA"
_APTAMER_FOLD = "(((((((....((((((.......)))))).........((((((.......))))))..)))))))"   # P1, P2, P3
_RIBO_ON = _APTAMER_FOLD + "." * 36                                                    # SD free
_RIBO_OFF = "." * 7 + _APTAMER_FOLD[7:60] + "..." + "(" * 8 + "." * 7 + ")" * 8 + "." * 17   # P1 open, anti-SD:SD

RIBO_NOTES = {
    "title": "Translational sequestering",
    "asked": "Explain translational sequestering by riboswitches. What do the sequestor and antisequestor do, "
             "and how can a metabolite switch translation on or off?",
    "answer": {
        "result": r"\text{ligand} \;\Rightarrow\; \text{which helix forms} \;\Rightarrow\; \orange{\text{SD}} \text{ free (ON) or hidden (OFF)}",
        "text": r"The riboswitch can hide the ribosome binding site ($\orange{\text{SD}}$) in a hairpin, the sequestor. "
                r"A $\green{\text{switch}}$ stretch can pair either with the SD or with the aptamer, never both, and the "
                r"ligand decides which by holding the aptamer closed.",
    },
    "colors": [
        {"color": "orange", "meaning": "the ribosome binding site (SD) and start codon"},
        {"color": "green", "meaning": "the switch: P1's 3' strand, which can also pair with the SD"},
        {"color": "blue", "meaning": "P1's 5' strand"},
        {"color": "red", "meaning": "the bases that hold the ligand"},
    ],
    "given": [
        {"symbol": r"\text{mRNA } 5'\text{ end}", "meaning": "holds a riboswitch: an aptamer that binds the ligand, and an expression platform"},
        {"symbol": r"\orange{\text{SD}},\ \orange{\text{AUG}}", "meaning": "the ribosome binding site and the start codon, just after the riboswitch"},
        {"symbol": r"\text{ligand}", "meaning": "a small metabolite; here DAP (2,6-diaminopurine), an adenine analogue"},
    ],
    "find": {"formula": r"\text{ligand} \;\longrightarrow\; \text{translation ON or OFF}",
             "meaning": "How binding one small molecule decides whether the ribosome can start, and why the same idea can switch genes on or off."},
    "methods": [
        {"id": "M1", "name": "How bacterial translation starts",
         "formula": r"\text{30S} + \orange{\text{SD}} \;\longrightarrow\; \text{start at } \orange{\text{AUG}}",
         "says": "The small ribosomal subunit finds a gene by base-pairing with the Shine-Dalgarno sequence a few bases before the start codon.",
         "why": "Anything that pairs up the SD first stops translation before it begins."},
        {"id": "M2", "name": "Base pairing is exclusive",
         "formula": r"\text{A-U},\ \text{G-C},\ \text{G-U}; \quad \text{one partner per base}",
         "says": "Each base pairs with one partner at a time, so two helices that need the same bases can't both form.",
         "why": "The riboswitch works by offering the switch stretch two possible partners."},
        {"id": "M3", "name": "The sequestor",
         "formula": r"\text{sequestor} = \green{\text{switch}} : \orange{\text{SD}}",
         "says": "A hairpin that pairs the SD with a complementary stretch, hiding it from the ribosome.",
         "why": "This is the OFF state of the riboswitch in the notes."},
        {"id": "M4", "name": "The antisequestor",
         "formula": r"\text{antisequestor}: \text{takes the } \green{\text{switch}}",
         "says": "Any helix that uses the switch stretch stops the sequestor from forming, which frees the SD.",
         "why": "Here the aptamer's helix P1 is the antisequestor."},
        {"id": "M5", "name": "The most stable fold wins",
         "formula": r"\Delta G_{\text{fold}} \text{ lowest} \;\Rightarrow\; \text{most of the RNA folds that way}",
         "says": r"An RNA spends most of its time in the fold with the lowest free energy $\Delta G$. A bound ligand lowers the energy of the fold that holds it.",
         "why": "It explains why the ligand is needed to flip the switch."},
    ],
    "plan": "Look at the aptamer and its pocket (M2), compare the two ways the RNA can fold (M3, M4, M5), then see "
            "what the ribosome finds in each (M1). Finally the same parts, wired differently, give an OFF switch.",
    "solution": [
        {"title": "The aptamer: a pocket made of RNA",
         "uses": ["M2"],
         "work": r"\text{P1} + \text{P2} + \text{P3} + \text{ligand} \;\longrightarrow\; \text{closed aptamer}",
         "figure": {
             "type": "molecule", "pdb": "4FEO",
             "highlights": [
                 {"chain": "B", "residues": "15-21", "color": "blue", "label": "P1, 5' strand"},
                 {"chain": "B", "residues": "75-81", "color": "green", "label": "P1, 3' strand (switch)"},
                 {"chain": "B", "residues": "22,47,51,74", "color": "red", "label": "pocket"},
             ],
             "ligand": {"name": "DAP", "resn": "6AP"},
         },
         "caption": "A real purine riboswitch aptamer (PDB 4FEO, the xpt-pbuX riboswitch of B. subtilis, "
                    "mutated so it binds 2,6-diaminopurine, an adenine analogue). Drag it to turn it.",
         "result": r"\text{ligand bound} \;\Rightarrow\; \blue{\text{P1}} : \green{\text{switch}} \text{ locked}",
         "explain": r"Three helices fold around the ligand, and four bases ($\red{\text{U22, U47, U51, U74}}$) hold it "
                    r"by base pairing. The ligand also locks helix P1, so the $\green{\text{switch}}$ is busy as long as the ligand is bound."},
        {"title": "Two folds of the same RNA",
         "uses": ["M2", "M3", "M4", "M5"],
         "work": r"\underbrace{\green{\text{switch}} : \orange{\text{SD}}}_{\text{no ligand: OFF}} "
                 r"\;\rightleftharpoons\; \underbrace{\blue{\text{P1}} : \green{\text{switch}}}_{\text{ligand bound: ON}}",
         "figure": {
             "type": "rna",
             "sequence": _RIBO_SEQ,
             "states": [
                 {"name": "no ligand", "structure": _RIBO_OFF, "ligand": False,
                  "note": "The switch pairs with the SD (the sequestor), so the ribosome can't bind: translation OFF."},
                 {"name": "+ DAP", "structure": _RIBO_ON, "ligand": True,
                  "note": "DAP closes P1, the switch is taken, and the SD is single-stranded: translation ON."},
             ],
             "regions": [
                 {"name": "P1", "start": 1, "end": 7, "color": "blue"},
                 {"name": "switch", "start": 61, "end": 71, "color": "green"},
                 {"name": "SD", "start": 79, "end": 86, "color": "orange"},
                 {"name": "AUG", "start": 92, "end": 94, "color": "orange"},
             ],
             "ligand": {"name": "DAP", "near": [8, 33, 37, 60]},
         },
         "caption": "A model riboswitch: the aptamer above followed by a designed expression platform. "
                    "Pick a fold, or press Refold to watch it switch.",
         "result": r"\text{ligand} \;\Rightarrow\; \text{ON fold}",
         "explain": r"The same 103 bases can fold two ways, because the $\green{\text{switch}}$ can pair with only one partner. "
                    r"On its own the OFF fold is about $6$ kcal/mol more stable, so the SD stays hidden. Binding the ligand "
                    r"pays for that difference, and the RNA refolds with the SD free."},
        {"title": "What the ribosome finds",
         "uses": ["M1", "M3"],
         "work": r"\begin{aligned} \text{no ligand:}&\quad \orange{\text{SD}} \text{ paired} \;\Rightarrow\; \text{30S can't bind} \;\Rightarrow\; \text{OFF}\\ "
                 r"\text{ligand:}&\quad \orange{\text{SD}} \text{ free} \;\Rightarrow\; \text{30S binds} \;\Rightarrow\; \text{ON} \end{aligned}",
         "result": r"\hl{\text{ligand} \Rightarrow \text{translation ON}}",
         "explain": "Nothing chemical happens to the ribosome: it simply can't pair with an SD that is already paired. "
                    "The mRNA is made either way; only its translation is switched."},
        {"title": "The same parts as an OFF switch",
         "uses": ["M4"],
         "work": r"\text{ligand stabilises an } \text{anti}^{k}\text{sequestor} \;\Rightarrow\; "
                 r"\begin{cases} k \text{ odd: ON} \\ k \text{ even: OFF} \end{cases}",
         "picture": r"\begin{array}{l|c|c} & \text{no ligand} & \text{ligand bound} \\ \hline "
                    r"\text{ON switch (here, adenine } \textit{add}\text{)} & \text{OFF} & \text{ON} \\ "
                    r"\text{OFF switch (TPP } \textit{thiM}\text{, B}_{12}\ \textit{btuB}\text{)} & \text{ON} & \text{OFF} \end{array}",
         "caption": "The same parts give either logic, depending on which helix the ligand stabilises.",
         "result": r"\text{aptamer} = \text{anti-antisequestor} \;\Rightarrow\; \text{ligand turns it OFF}",
         "explain": "In an OFF switch the aptamer takes a stretch that would otherwise block the sequestor (an "
                    "anti-antisequestor), so the ligand turns translation off: typical feedback for genes that make the ligand."},
    ],
    "checks": [
        "In Figure 2 the SD is a ladder (paired) in the OFF fold and a loose strand in the ON fold.",
        r"The energies agree: without the ligand the OFF fold ($-30.7$ kcal/mol) beats the ON fold ($-24.5$ kcal/mol).",
    ],
    "takeaways": {
        "key_idea": "A riboswitch is a set of base pairings that exclude each other, and the ligand picks one of them.",
        "mistakes": [
            "Thinking the ligand acts on the ribosome. It only changes how the mRNA folds.",
            "Mixing it up with transcription control: terminator riboswitches use the same logic, but there the hairpin "
            "stops RNA polymerase instead of hiding the SD.",
        ],
    },
    "exam": [
        {"text": "Bacterial translation starts when the 30S subunit base-pairs with the Shine-Dalgarno sequence before the AUG."},
        {"text": "In translational sequestering, the riboswitch's expression platform can fold the SD into a hairpin, "
                 "the sequestor, so the ribosome can't bind."},
        {"text": "The sequestor competes with other helices for the same bases. Binding the ligand stabilises the "
                 "aptamer, and so decides which helix forms:",
         "formula": r"\text{ligand} \Rightarrow \text{aptamer} \Rightarrow \text{fold} \Rightarrow \text{SD free (ON) or hidden (OFF)}."},
        {"text": "If the aptamer is the antisequestor, the ligand turns the gene on; if it is the anti-antisequestor, off."},
    ],
}

# ---- A research paper: Gibbs-With-Gradients ---------------------------------------------------
# Grathwohl, Swersky, Hashemi, Duvenaud and Maddison, "Oops I Took A Gradient: Scalable Sampling for
# Discrete Distributions", ICML 2021 (arXiv 2102.04509). The worked numbers in the one-step example
# were computed for the small softplus model given there; the results table is from the paper.

PAPER_NOTES = {
    "title": "Gibbs-With-Gradients: sampling discrete data with a gradient",
    "asked": "Explain this paper in simple terms with all its formulas: Oops I Took A Gradient: Scalable Sampling "
             "for Discrete Distributions (Grathwohl et al., ICML 2021).",
    "answer": {
        "result": r"\green{q(i\mid x)} = \operatorname{Softmax}\Big(\tfrac{\blue{\tilde d(x)}}{2}\Big)_i,\qquad "
                  r"\blue{\tilde d(x)} = -(2x-1)\odot\blue{\nabla_x f(x)}",
        "text": r"To sample a discrete distribution well, MCMC should propose the changes that matter, but scoring every "
                r"possible change costs one evaluation of $f$ per change, $D$ in all. The paper notices that $f$ is "
                r"almost always a differentiable formula, so one gradient estimates all $D$ changes at once. A softmax of "
                r"those estimates is a proposal that costs a constant number of evaluations and is provably within a "
                r"factor $\red{c}$ of the best local proposal.",
    },
    "colors": [
        {"color": "blue", "meaning": r"the gradient $\nabla_x f$ and the estimates $\tilde d$ built from it, the paper's new ingredient"},
        {"color": "orange", "meaning": r"true changes in log-probability, $\Delta = f(x') - f(x)$"},
        {"color": "green", "meaning": r"proposal distributions $q$"},
        {"color": "purple", "meaning": r"normalising constants $Z$, which are never computed"},
        {"color": "red", "meaning": r"the efficiency constant $c$ of Theorem 1"},
    ],
    "given": [
        {"symbol": r"p(x) = \dfrac{e^{f(x)}}{\purple{Z}}",
         "meaning": r"The distribution to sample. $f$ is the unnormalised log-probability, which we can evaluate; "
                    r"$\purple{Z} = \sum_x e^{f(x)}$ is unknown."},
        {"symbol": r"x \in \{0,1\}^D",
         "meaning": r"Binary data with $D$ dimensions: pixels, spins, bits. Categorical data, $x \in \{1,\dots,K\}^D$, is one-hot encoded."},
        {"symbol": r"f : \mathbb{R}^D \to \mathbb{R}",
         "meaning": r"The key observation: the formula for $f$ also accepts real inputs and is differentiable, as for Ising "
                    r"and Potts models, RBMs, HMMs and neural networks."},
        {"symbol": r"\|\nabla f(x) - \nabla f(y)\| \le L\,\|x - y\|",
         "meaning": r"Smoothness with constant $L$: the gradient changes at most at rate $L$. Needed only for the guarantee."},
        {"symbol": r"H(x)",
         "meaning": r"The Hamming ball around $x$: the states one local move away. In the paper, flip one bit, so $H(x)$ has $D$ states."},
    ],
    "find": {"formula": r"\begin{gathered}\green{q(x'\mid x)}:\ \ O(1) \text{ cost per step}\\ \text{efficiency} \ge \red{c}\cdot\text{best}\end{gathered}",
             "meaning": r"A Metropolis-Hastings proposal that knows which dimensions are worth changing, costs a constant "
                        r"number of evaluations of $f$ per step instead of $D$, and loses at most a constant factor $\red{c}$."},
    "methods": [
        {"id": "M1", "name": "Unnormalised models, and why $Z$ is the problem",
         "formula": r"\begin{gathered}\log p(x) = f(x) - \log\purple{Z}\\ \purple{Z} = \sum_{x\in\{0,1\}^D} e^{f(x)}\end{gathered}",
         "says": r"$f(x)$ scores how likely $x$ is and $\purple{Z}$ turns scores into probabilities. The sum has $2^D$ "
                 r"terms ($2^{784}$ for one MNIST image), so it is never computed: a usable method may only need "
                 r"differences $f(x') - f(x)$, in which $\purple{Z}$ cancels.",
         "why": "Every model in the paper has this form: categorical, Poisson, HMM, RBM, Ising, Potts and deep energy-based models."},
        {"id": "M2", "name": "Gibbs sampling",
         "formula": r"\begin{gathered}x_i \sim p(x_i \mid x_{-i})\\ p(x_i = 1 \mid x_{-i}) = \sigma\big(f(x^{i\leftarrow 1}) - f(x^{i\leftarrow 0})\big)\end{gathered}",
         "says": r"Pick a dimension $i$, keep all the others ($x_{-i}$) fixed, and redraw $x_i$ from its conditional. "
                 r"$x^{i\leftarrow 1}$ is $x$ with $x_i$ set to 1, and $\sigma(t) = 1/(1+e^{-t})$ is the sigmoid. With $K$ "
                 r"categories it costs $K$ evaluations of $f$.",
         "why": "It is the simplest generic sampler, the one the paper improves on, and its weakness motivates the paper."},
        {"id": "M3", "name": "Metropolis-Hastings acceptance",
         "formula": r"A(x \to x') = \min\Big\{ e^{\orange{f(x') - f(x)}}\,\frac{\green{q(x \mid x')}}{\green{q(x' \mid x)}},\ 1 \Big\}",
         "says": r"Propose $x'$ from any proposal $\green{q(x' \mid x)}$, accept it with probability $A$, otherwise stay at $x$. "
                 r"The chain then samples $p$ exactly in the long run. $p(x')/p(x) = e^{\orange{f(x') - f(x)}}$ needs no "
                 r"$\purple{Z}$, and the ratio of $\green{q}$ corrects for a proposal that prefers some moves.",
         "why": r"Gibbs-With-Gradients is a Metropolis-Hastings sampler: the whole paper is about choosing $\green{q}$."},
        {"id": "M4", "name": "Locally informed proposals",
         "formula": r"\green{q_\tau(x' \mid x)} \propto e^{\orange{(f(x') - f(x))}/\tau}\;\mathbf{1}\big(x' \in H(x)\big)",
         "says": r"Among the nearby states $H(x)$, propose each in proportion to how much it raises the log-probability, "
                 r"softened by a temperature $\tau > 0$. $\mathbf{1}(\cdot)$ is 1 inside the Hamming ball and 0 outside.",
         "why": r"This is the ideal the paper approximates. With $\tau = 2$ it is the best proposal of its kind (Zanella, 2020)."},
        {"id": "M5", "name": "First-order Taylor expansion",
         "formula": r"\orange{f(x') - f(x)} \approx \blue{\nabla_x f(x)^{\top}}(x' - x)",
         "says": r"Near $x$ a differentiable function is close to its tangent plane: the change in $f$ is about the gradient "
                 r"times the step. With smoothness constant $L$ the error is at most $\tfrac{L}{2}\|x' - x\|^2$.",
         "why": r"It turns one gradient into estimates of all $D$ differences $\orange{f(x') - f(x)}$ at once."},
        {"id": "M6", "name": "Softmax and categorical sampling",
         "formula": r"\operatorname{Softmax}(v)_i = \frac{e^{v_i}}{\sum_{j=1}^{D} e^{v_j}}",
         "says": r"Turns any $D$ scores $v_i$ into probabilities that are positive and sum to 1, giving larger scores "
                 r"exponentially more weight. Drawing $i$ with these probabilities is a categorical draw.",
         "why": r"It turns the estimated differences into a proposal over which bit to flip; its normaliser has only $D$ terms."},
        {"id": "M7", "name": "Measuring a sampler: asymptotic variance and spectral gap",
         "formula": r"\begin{gathered}\operatorname{var}_p(h, Q) = \lim_{T\to\infty}\frac{1}{T}\operatorname{var}\Big(\sum_{t=1}^{T} h(x_t)\Big)\\ \operatorname{Gap}(Q) = 1 - \lambda_2\end{gathered}",
         "says": r"$Q(x', x)$ is the transition kernel, the probability of moving from $x$ to $x'$ in one step. The asymptotic "
                 r"variance says how noisy the chain's average of a function $h$ is (lower is better). $\lambda_2$ is the "
                 r"second-largest eigenvalue of the transition matrix; a larger gap $1 - \lambda_2$ means faster mixing.",
         "why": "Theorem 1 states its guarantee in exactly these two quantities."},
        {"id": "M8", "name": "Comparing two Markov chains (Zanella, 2020)",
         "formula": r"\begin{gathered}Q_1(x', x) \ge \red{c}\,Q_2(x', x) \text{ for all } x' \ne x \;\Rightarrow\\ \operatorname{Gap}(Q_1) \ge \red{c}\operatorname{Gap}(Q_2)\\ \operatorname{var}_p(h, Q_1) \le \frac{\operatorname{var}_p(h, Q_2)}{\red{c}} + \frac{1-\red{c}}{\red{c}}\operatorname{var}_p(h)\end{gathered}",
         "says": r"If one $p$-reversible chain makes every move $x \to x'$ with $x' \ne x$ at least $\red{c}$ times as often as "
                 r"another, it is at least $\red{c}$ times as efficient. $\operatorname{var}_p(h)$ is the ordinary variance of $h$ under $p$.",
         "why": "It reduces Theorem 1 to comparing the two chains one move at a time."},
        {"id": "M9", "name": "Scoring samplers in experiments: ESS and MMD",
         "formula": r"\begin{gathered}\text{ESS} = \frac{T}{1 + 2\sum_{k\ge 1}\rho_k}\\ \text{MMD}^2 = \mathbb{E}\,k(x, x') + \mathbb{E}\,k(y, y') - 2\,\mathbb{E}\,k(x, y)\end{gathered}",
         "says": r"Effective sample size: $T$ correlated samples with autocorrelations $\rho_k$ are worth ESS independent ones "
                 r"(higher is better). Maximum mean discrepancy: how far the sampler's samples $x$ are from true samples $y$, "
                 r"through a similarity kernel $k$ (lower is better); the paper uses $k(x, x') = e^{-\text{Hamming}(x, x')/D}$.",
         "why": "Every sampling plot in the paper reports one of these two."},
        {"id": "M10", "name": "Maximum likelihood for energy-based models",
         "formula": r"\nabla_\theta \log p_\theta(x) = \nabla_\theta f_\theta(x) - \mathbb{E}_{x'\sim p_\theta}\big[\nabla_\theta f_\theta(x')\big]",
         "says": r"To fit parameters $\theta$, push $f_\theta$ up on the data and down on samples from the model. The second term "
                 r"is the gradient of $\log\purple{Z_\theta}$, an expectation estimated with MCMC samples.",
         "why": "A better sampler gives a better estimate of this gradient, which is why Gibbs-With-Gradients can train models Gibbs cannot."},
    ],
    "plan": r"Start from the setting (M1) and the two generic samplers it allows, Gibbs (M2) and Metropolis-Hastings (M3). "
            r"The best local proposal (M4) needs $D$ evaluations of $f$; a Taylor expansion (M5) estimates them all from one "
            r"gradient and a softmax (M6) turns the estimates into the Gibbs-With-Gradients proposal. Theorem 1 (M7, M8) bounds "
            r"what the approximation costs, and the experiments (M9, M10) show what it buys.",
    "solution": [
        {"title": "Why discrete sampling is expensive",
         "uses": ["M1", "M2"],
         "work": r"\begin{aligned}"
                 r"\purple{Z} &= \sum_{x\in\{0,1\}^D} e^{f(x)}\\"
                 r"p(x_i = 1 \mid x_{-i}) &= \frac{e^{f(x^{i\leftarrow 1})}/\purple{Z}}{e^{f(x^{i\leftarrow 1})}/\purple{Z} + e^{f(x^{i\leftarrow 0})}/\purple{Z}}\\"
                 r"&= \sigma\big(f(x^{i\leftarrow 1}) - f(x^{i\leftarrow 0})\big)"
                 r"\end{aligned}",
         "result": r"\purple{Z} \text{ cancels, but } i \text{ is chosen blindly}",
         "explain": r"$\purple{Z}$ cancels from every conditional, so Gibbs works without it. But it picks dimensions blindly. "
                    r"On MNIST most pixels are background or deep inside a stroke and almost never change, so most updates waste "
                    r"an evaluation of $f$. Only pixels at a digit's edge are worth trying, and which ones those are depends on the whole image $x$.",
         "picture": r"\begin{array}{ll}"
                    r"\text{model} & \log p(x) + \log\purple{Z}\\ \hline"
                    r"\text{Categorical} & x^{\top}\theta\\"
                    r"\text{Poisson} & x\log\lambda - \log\Gamma(x+1)\\"
                    r"\text{HMM} & \sum_{t} x_{t+1}^{\top}A x_t - \frac{(w^{\top}x_t - y_t)^2}{2\sigma^2}\\"
                    r"\text{RBM} & \sum_i \operatorname{softplus}(Wx + b)_i + c^{\top}x\\"
                    r"\text{Ising} & x^{\top}Wx + b^{\top}x\\"
                    r"\text{Potts} & \sum_{i} h_i^{\top}x_i + \sum_{i,j} x_i^{\top}J_{ij}x_j\\"
                    r"\text{Deep EBM} & f_\theta(x)"
                    r"\end{array}",
         "caption": "The paper's Table 1: common discrete models are all written as formulas that are differentiable in $x$. That is the structure the paper uses."},
        {"title": "Metropolis-Hastings, with a choice of which bit to flip",
         "uses": ["M3"],
         "work": r"\begin{aligned}"
                 r"\green{q(x' \mid x)} &= \sum_i \green{q(i)}\;\mathbf{1}\big(x' = \operatorname{flip}(x, i)\big) && \text{pick } i,\ \text{flip bit } i\\"
                 r"\frac{p(x')}{p(x)} &= \frac{e^{f(x')}/\purple{Z}}{e^{f(x)}/\purple{Z}} = e^{\orange{f(x') - f(x)}}\\"
                 r"A &= \min\Big\{ e^{\orange{f(x') - f(x)}}\,\frac{\green{q(x \mid x')}}{\green{q(x' \mid x)}},\ 1 \Big\}"
                 r"\end{aligned}",
         "result": r"\text{a good proposal should depend on } x:\ \ \green{q(i \mid x)}",
         "explain": r"Metropolis-Hastings lets you prefer some bits, through $\green{q(i)}$, and still sample $p$ exactly, "
                    r"because the ratio of proposals corrects the bias. Earlier work tuned a fixed $\green{q(i)}$. The paper's point is "
                    r"that the best choice depends on the current $x$, like the edge pixels of a digit."},
        {"title": "The best local proposal, and why the temperature is 2",
         "uses": ["M3", "M4"],
         "work": r"\begin{aligned}"
                 r"\green{q_\tau(x' \mid x)} &= \frac{e^{\orange{\Delta}/\tau}}{\purple{Z(x)}},\quad \green{q_\tau(x \mid x')} = \frac{e^{-\orange{\Delta}/\tau}}{\purple{Z(x')}} && \orange{\Delta} = \orange{f(x') - f(x)}\\"
                 r"e^{\orange{\Delta}}\,\frac{\green{q_\tau(x \mid x')}}{\green{q_\tau(x' \mid x)}} &= e^{\orange{\Delta}}\,\frac{e^{-\orange{\Delta}/\tau}\,\purple{Z(x)}}{e^{\orange{\Delta}/\tau}\,\purple{Z(x')}}\\"
                 r"&= \exp\!\Big(\big(1 - \tfrac{2}{\tau}\big)\orange{\Delta}\Big)\,\frac{\purple{Z(x)}}{\purple{Z(x')}}"
                 r"\end{aligned}",
         "result": r"\tau = 2:\quad A = \min\Big\{\frac{\purple{Z(x)}}{\purple{Z(x')}},\ 1\Big\}",
         "explain": r"With $\tau = 2$ the gain in log-probability and the penalty for an unlikely reverse move cancel exactly. "
                    r"What is left is a ratio of two neighbourhood normalisers, close to 1 when $x'$ is near $x$ and $f$ is smooth. "
                    r"The catch: $\purple{Z(x)} = \sum_{x' \in H(x)} e^{\orange{(f(x') - f(x))}/2}$ needs $f$ at all $D$ neighbours, "
                    r"so each step costs $D$ evaluations.",
         "picture": r"\begin{array}{lll}"
                    r"\tau & \text{acceptance keeps} & \text{behaviour}\\ \hline"
                    r"1 & e^{-\orange{\Delta}}\,\purple{Z(x)}/\purple{Z(x')} & \text{greedy: the reverse move is unlikely, so many rejections}\\"
                    r"2 & \purple{Z(x)}/\purple{Z(x')} & \text{balanced}\\"
                    r"\to\infty & e^{\orange{\Delta}}\,\purple{Z(x)}/\purple{Z(x')} & \text{blind: a random walk that ignores } f"
                    r"\end{array}",
         "caption": r"What the acceptance probability keeps of the gain $\orange{\Delta}$ at three temperatures. Only $\tau = 2$ removes it."},
        {"title": "One gradient estimates every flip",
         "uses": ["M5"],
         "work": r"\begin{aligned}"
                 r"x' &= \operatorname{flip}(x, i):\quad x'_i - x_i = 1 - 2x_i,\ \text{all other entries equal}\\"
                 r"\orange{f(x') - f(x)} &\approx \blue{\nabla_x f(x)^{\top}}(x' - x) = (1 - 2x_i)\,\blue{\nabla_x f(x)_i}\\"
                 r"\blue{\tilde d(x)} &= -(2x - 1)\odot\blue{\nabla_x f(x)}"
                 r"\end{aligned}",
         "expansion": r"\begin{aligned}\text{categorical, } x_i \text{ one-hot, changed to value } j:\quad x'_i - x_i &= e_j - x_i\\ "
                      r"\blue{\tilde d(x)_{ij}} &= \blue{\nabla_x f(x)_{ij}} - x_i^{\top}\blue{\nabla_x f(x)_i}\end{aligned}",
         "result": r"\hl{\blue{\tilde d(x)} = -(2x - 1)\odot\blue{\nabla_x f(x)}}",
         "explain": r"Flipping bit $i$ moves only coordinate $i$, up by 1 if it was 0 and down by 1 if it was 1, so the tangent-plane "
                    r"estimate is the partial derivative along $i$ with that sign; $\odot$ multiplies entry by entry. Automatic "
                    r"differentiation gives the whole gradient for about the cost of one evaluation of $f$, so all $D$ estimates "
                    r"come almost free. For one-hot categories, moving to value $j$ gains the gradient at $j$ and loses it at the current value."},
        {"title": "Gibbs-With-Gradients, one step",
         "uses": ["M6", "M3"],
         "work": r"\begin{aligned}"
                 r"\green{q(i \mid x)} &= \operatorname{Softmax}\Big(\tfrac{\blue{\tilde d(x)}}{2}\Big)_i = \frac{e^{\blue{\tilde d(x)_i}/2}}{\sum_j e^{\blue{\tilde d(x)_j}/2}}\\"
                 r"i &\sim \green{q(i \mid x)},\qquad x' = \operatorname{flip}(x, i)\\"
                 r"\green{q(x \mid x')} &= \green{q(i \mid x')} && \text{flipping } i \text{ again returns to } x\\"
                 r"A &= \min\Big\{ e^{\orange{f(x') - f(x)}}\,\frac{\green{q(i \mid x')}}{\green{q(i \mid x)}},\ 1\Big\}"
                 r"\end{aligned}",
         "expansion": r"\begin{aligned}"
                      r"&f(x) = \log\big(1 + e^{w^{\top}x + a}\big) + b^{\top}x,\quad w = (2, -1, 1),\ a = -1,\ b = (-\tfrac12, \tfrac12, 0),\ x = (1, 0, 1)\\"
                      r"&\blue{\nabla_x f(x)} = \sigma(w^{\top}x + a)\,w + b = \sigma(2)\,(2, -1, 1) + b = (1.26,\ -0.38,\ 0.88)\\"
                      r"&\blue{\tilde d(x)} = -(1, -1, 1)\odot(1.26,\ -0.38,\ 0.88) = (-1.26,\ -0.38,\ -0.88)\\"
                      r"&\text{true changes: } \orange{(-0.93,\ -0.31,\ -0.81)}\\"
                      r"&\green{q(\cdot \mid x)} = \operatorname{Softmax}(-0.63,\ -0.19,\ -0.44) = (0.27,\ \green{0.41},\ 0.32)\\"
                      r"&i = 2:\ \ x' = (1, 1, 1),\quad \blue{\tilde d(x')} = (-0.96,\ 0.23,\ -0.73),\quad \green{q(2 \mid x')} = 0.46\\"
                      r"&A = \min\big\{e^{\orange{1.31 - 1.63}}\cdot 0.46/0.41,\ 1\big\} = \min\{0.73 \cdot 1.12,\ 1\} = 0.82"
                      r"\end{aligned}",
         "result": r"\hl{\green{q(i \mid x)} = \operatorname{Softmax}\big(\blue{\tilde d(x)}/2\big)_i}",
         "explain": r"Each step evaluates $f$ and its gradient twice, at $x$ and at $x'$, whatever $D$ is; the exact $\green{q_2}$ "
                    r"needs $D$ evaluations. In the example the estimates are off by at most $0.33$, the proposal is close to the "
                    r"exact one, $(0.29, 0.40, 0.31)$, and the acceptance step corrects what remains, so the chain still samples $p$ "
                    r"exactly. Flipping $N$ bits at once works the same way, with products of $\green{q(i_n \mid x)}$.",
         "figure": {"type": "sampler", "model": "ising", "size": 24, "theta": 0.3},
         "caption": r"Both chains start from the same random lattice. Green is $\green{q(i \mid x)}$: Gibbs-With-Gradients proposes "
                    r"almost only on the borders between black and white domains, where a flip can be accepted, while Gibbs spends "
                    r"most steps inside domains where nothing changes. A Gibbs-With-Gradients step costs about twice a Gibbs step. "
                    r"Press One step to see a single proposal."},
        {"title": "What the approximation costs: Theorem 1",
         "uses": ["M7", "M8", "M5"],
         "work": r"\begin{aligned}"
                 r"\blue{\nabla(x', x)} &= \blue{\nabla_x f(x)^{\top}}(x' - x) \approx \orange{\Delta(x', x)}\\"
                 r"\big|\blue{\nabla(x', x)} - \orange{\Delta(x', x)}\big| &\le \tfrac{L}{2}\|x' - x\|^2 \le \tfrac{L}{2}D_H^2\\"
                 r"\purple{\tilde Z(x)} = \sum_{x' \in H(x)} e^{\blue{\nabla(x', x)}/2} &\in \big[e^{-LD_H^2/4},\ e^{LD_H^2/4}\big]\,\purple{Z(x)}\\"
                 r"Q(x', x) &= \min\Big\{\frac{e^{\orange{\Delta(x', x)}/2}}{\purple{Z(x)}},\ \frac{e^{\orange{\Delta(x', x)}/2}}{\purple{Z(x')}}\Big\} = \min\{a,\ b\}\\"
                 r"\frac{a^{\nabla}}{a} &= \frac{\purple{Z(x)}}{\purple{\tilde Z(x)}}\,e^{(\blue{\nabla(x', x)} - \orange{\Delta(x', x)})/2} \ge e^{-LD_H^2/4}\,e^{-LD_H^2/4}\\"
                 r"Q^{\nabla}(x', x) &= \min\{a^{\nabla},\ b^{\nabla}\} \ge \red{c}\,Q(x', x),\qquad \red{c} = e^{-LD_H^2/2}"
                 r"\end{aligned}",
         "expansion": r"\operatorname{Gap}(Q^{\nabla}) \ge \red{c}\operatorname{Gap}(Q),\qquad "
                      r"\operatorname{var}_p(h, Q^{\nabla}) \le \frac{\operatorname{var}_p(h, Q)}{\red{c}} + \frac{1-\red{c}}{\red{c}}\operatorname{var}_p(h)",
         "result": r"\hl{\red{c} = e^{-L D_H^2/2}},\qquad D_H = \sup_{x' \in H(x)}\|x - x'\|",
         "explain": r"The gradient estimate is never off by more than $\tfrac{L}{2}D_H^2$, so neither is the proposal or its "
                    r"normaliser, and the approximate chain makes every move at least $\red{c}$ times as often as the ideal chain "
                    r"(the $b$ terms are bounded the same way). M8 turns that into the bounds on mixing and variance. Per step you "
                    r"lose at most a factor $\red{c}$, but each step is about $D$ times cheaper. In the worked example "
                    r"$L \le \tfrac14\|w\|^2 = 1.5$, so the errors are at most $0.75$ (they were $0.33$, $0.07$ and $0.07$) and $\red{c} \ge e^{-0.75} = 0.47$."},
        {"title": "The Ising lattice: the efficiency stays above two-thirds",
         "uses": ["M5", "M8"],
         "work": r"\begin{aligned}"
                 r"f(x) &= \theta\,x^{\top}Jx && J:\ \text{the lattice's adjacency matrix}\\"
                 r"\blue{\nabla_x f(x)} &= 2\theta\,Jx,\qquad \nabla^2 f = 2\theta J\\"
                 r"L &= \|2\theta J\|_2 = 2\theta\,\sigma_{\max}(J) = 2\theta \cdot 4 = 8\theta\\"
                 r"\red{c} &= e^{-L D_H^2/2} = e^{-8(0.1)(1)^2/2} = e^{-0.4} = 0.67"
                 r"\end{aligned}",
         "result": r"\theta = 0.1:\quad \red{c} \approx 0.67 \text{ for every lattice size } D",
         "explain": r"Every site has 4 neighbours, so the largest singular value of $J$ is 4, and one flip moves $x$ a distance "
                    r"$D_H = 1$. The bound does not depend on $D$. The exact $\green{q_2}$ costs $D$ evaluations of an $O(D^2)$ function, "
                    r"$O(D^3)$ per step, while Gibbs-With-Gradients costs $O(D^2)$: a speed-up of order $D$ for a loss of at most a "
                    r"third. When the same distribution can be written with different formulas $f$, the theorem says to choose the one "
                    r"whose gradient has the smallest $L$."},
        {"title": "What the experiments show about sampling",
         "uses": ["M9"],
         "work": r"\begin{aligned}"
                 r"\text{cost per step} &= 1 && \text{Gibbs-1}\\"
                 r"&\approx 1.6,\ \ 2.1,\ \ 6.6 && \text{Gibbs-2, Gibbs-With-Gradients, Hamming ball HB-10-1}"
                 r"\end{aligned}",
         "result": r"\text{generic and tuning-free, yet close to samplers built for the model}",
         "explain": r"Gibbs-With-Gradients has no step size or temperature to tune, unlike samplers that relax $x$ to continuous "
                    r"values and transform back. Block-Gibbs for the RBM uses structure only RBMs have and updates all 784 pixels "
                    r"at once; Gibbs-With-Gradients changes one pixel per step and still matches its MMD.",
         "picture": r"\begin{array}{lll}"
                    r"\text{experiment} & \text{score} & \text{Gibbs-With-Gradients}\\ \hline"
                    r"\text{RBM on MNIST},\ D = 784 & \text{MMD} & \text{reaches the Block-Gibbs level}\\"
                    r" & \text{ESS} & \text{well above Gibbs and Hamming ball}\\"
                    r"\text{Ising},\ 10\times 10,\ 40\times 40 & \text{ESS} & \text{highest in most settings}\\"
                    r"\text{factorial HMM} & \text{likelihood} & \text{best, ahead of the Hamming ball}\\"
                    r"\text{continuous relaxations} & \text{MMD} & \text{they degrade as } D \text{ grows; it does not}"
                    r"\end{array}",
         "caption": "What each sampling experiment measured and found, from the paper's Figures 2 to 5."},
        {"title": "Training energy-based models with it",
         "uses": ["M10", "M1"],
         "work": r"\begin{aligned}"
                 r"\nabla_\theta \log p_\theta(x) &= \nabla_\theta f_\theta(x) - \nabla_\theta \log\purple{Z_\theta}\\"
                 r"\nabla_\theta \log\purple{Z_\theta} &= \frac{1}{\purple{Z_\theta}}\sum_{x'} e^{f_\theta(x')}\,\nabla_\theta f_\theta(x')\\"
                 r"&= \mathbb{E}_{x' \sim p_\theta}\big[\nabla_\theta f_\theta(x')\big] \approx \frac{1}{m}\sum_{k=1}^{m}\nabla_\theta f_\theta(x'_k) && x'_k \text{ from MCMC}"
                 r"\end{aligned}",
         "result": r"\text{better sampler} \;\Rightarrow\; \text{less biased gradient} \;\Rightarrow\; \text{better model}",
         "explain": r"Persistent contrastive divergence keeps a buffer of chains and moves them a few MCMC steps per parameter update. "
                    r"With Gibbs-With-Gradients, Ising couplings are recovered with far lower error, and Potts models of proteins with "
                    r"276 and 526 amino acids predict contacts better than Gibbs or pseudo-likelihood. For deep EBMs, Gibbs needed 800 "
                    r"steps per update against 40, and on 256-level images one Gibbs step costs 256 evaluations against 2, about 870 times slower overall.",
         "picture": r"\begin{array}{lcccc}"
                    r"\text{dataset} & \text{VAE (conv)} & \text{EBM, GWG} & \text{EBM, Gibbs} & \text{RBM}\\ \hline"
                    r"\text{Static MNIST} & -82.41 & \mathbf{-80.01} & -117.17 & -86.39\\"
                    r"\text{Omniglot} & -97.65 & \mathbf{-94.72} & -142.06 & -100.47\\"
                    r"\text{Caltech Silhouettes} & -106.35 & \mathbf{-96.20} & -163.50 & \text{--}"
                    r"\end{array}",
         "caption": "Test log-likelihood, higher is better, from the paper's Table 2. The Gibbs-trained EBM had the same wall-clock time as the one trained with Gibbs-With-Gradients."},
    ],
    "checks": [
        r"$\purple{Z}$ is never computed: Gibbs conditionals, Metropolis-Hastings ratios and the softmax use only differences of $f$.",
        r"For the Ising model $f$ is linear in each $x_i$ on its own ($J_{ii} = 0$), so $\blue{\tilde d(x)}$ equals the true changes "
        r"and Gibbs-With-Gradients is exactly the ideal $\green{q_2}$; $\red{c} = 0.67$ is only a worst case.",
        r"If $f$ is linear, $L = 0$: the Taylor estimate is exact and $\red{c} = e^{0} = 1$.",
        r"In the worked example the errors $0.33$, $0.07$ and $0.07$ are within the bound $\tfrac{L}{2}D_H^2 = 0.75$.",
        r"Flipping the same bit twice returns to $x$, which is why the reverse proposal is $\green{q(i \mid x')}$.",
    ],
    "takeaways": {
        "key_idea": r"Discrete distributions are usually written as differentiable formulas, so one gradient estimates the effect "
                    r"of every local change, and a softmax of half those estimates is a near-optimal Metropolis-Hastings proposal "
                    r"that costs a constant number of evaluations per step.",
        "mistakes": [
            r"Thinking $x$ moves continuously, as in Langevin dynamics. Gibbs-With-Gradients never leaves $\{0,1\}^D$: the gradient "
            r"only chooses which bit to flip, and the acceptance step keeps the sampling exact.",
            r"Dropping the sign $-(2x - 1)$. Flipping a 1 to 0 moves $x_i$ down, so its estimated gain is minus the partial derivative.",
            r"Using $\operatorname{Softmax}(\blue{\tilde d})$ instead of $\operatorname{Softmax}(\blue{\tilde d}/2)$. That is $\tau = 1$, "
            r"too greedy: reverse moves become unlikely and more proposals are rejected.",
            r"Leaving the reverse proposal $\green{q(i \mid x')}$ out of the acceptance. The chain would then not sample $p$.",
            r"Reading Theorem 1 as a speed-up. It bounds the loss per step ($\red{c} \le 1$); the speed-up comes from each step "
            r"costing a constant number of evaluations instead of $D$.",
        ],
    },
    "exam": [
        {"text": r"Setting: sample $p$ on $\{0,1\}^D$, with $\purple{Z}$ unknown and $f$ differentiable.",
         "formula": r"p(x) = e^{f(x)}/\purple{Z}"},
        {"text": r"The ideal local proposal (locally balanced, $\tau = 2$) costs $D$ evaluations of $f$ per step.",
         "formula": r"\green{q_2(x' \mid x)} \propto e^{\orange{(f(x') - f(x))}/2}\,\mathbf{1}(x' \in H(x))"},
        {"text": "A first-order Taylor expansion estimates the change from every single-bit flip with one gradient.",
         "formula": r"\blue{\tilde d(x)} = -(2x - 1)\odot\blue{\nabla_x f(x)}"},
        {"text": r"Gibbs-With-Gradients: draw $i$, flip bit $i$, and accept with the Metropolis-Hastings probability.",
         "formula": r"\green{q(i \mid x)} = \operatorname{Softmax}(\blue{\tilde d(x)}/2)_i,\quad A = \min\Big\{e^{\orange{f(x') - f(x)}}\frac{\green{q(i \mid x')}}{\green{q(i \mid x)}},\,1\Big\}"},
        {"text": r"Theorem 1, for $L$-smooth $f$: the spectral gap is at least $\red{c}$ times that of the ideal chain, and the asymptotic variance is correspondingly bounded.",
         "formula": r"Q^{\nabla} \ge \red{c}\,Q,\qquad \red{c} = e^{-LD_H^2/2}"},
        {"text": "Result: on RBMs, Ising, factorial HMMs and Potts models it beats generic samplers for the same compute, and it makes training deep energy-based models on discrete data practical."},
    ],
}


EXAMPLES = {"trace": TRACE_NOTES, "purity": PURITY_NOTES, "roll": ROLL_NOTES, "ribo": RIBO_NOTES,
            "paper": PAPER_NOTES}
