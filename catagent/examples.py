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

EXAMPLES = {"trace": TRACE_NOTES, "purity": PURITY_NOTES, "roll": ROLL_NOTES, "ribo": RIBO_NOTES}
