// Figures the Notepad draws itself from a small spec (see figures.py for what the specs mean).
//   rna       a sequence and its folds: laid out here, morphing from one fold to the next
//   molecule  a 3D structure from the Protein Data Bank, shown with 3Dmol.js
//   sampler   an Ising lattice sampled live by Gibbs and by Gibbs-With-Gradients, side by side
// Figures.render(element, spec, { colors }) fills `element`; colors maps names to hex (no "#").

"use strict";

window.Figures = (() => {
  const SVG = "http://www.w3.org/2000/svg";
  const INK = "#1D1D1F";
  const SOFT_INK = "#3A3A3F";
  const LINE = "#C7C7CC";
  const LIGAND = "#7A4FD0";
  const REDUCED = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function el(tag, attrs, ...children) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k.startsWith("on")) e.addEventListener(k.slice(2).toLowerCase(), v);
      else if (k === "class") e.className = v;
      else if (k === "text") e.textContent = v;
      else e.setAttribute(k, v);
    }
    for (const c of children.flat()) if (c !== null && c !== undefined) e.append(c);
    return e;
  }

  function svg(tag, attrs) {
    const e = document.createElementNS(SVG, tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    return e;
  }

  // Run once, the first time the element is mostly on screen.
  function whenSeen(element, run) {
    if (!("IntersectionObserver" in window)) { run(); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { io.disconnect(); run(); }
    }, { threshold: 0.5 });
    io.observe(element);
  }

  // ==== RNA ==================================================================================

  function pairTable(structure) {
    const pt = new Array(structure.length).fill(-1);
    const stack = [];
    for (let i = 0; i < structure.length; i++) {
      if (structure[i] === "(") stack.push(i);
      else if (structure[i] === ")") { const j = stack.pop(); pt[i] = j; pt[j] = i; }
    }
    return pt;
  }

  // Lay out a fold the way RNA is drawn in textbooks: the unpaired 5' and 3' ends on a straight
  // line, every helix a ladder standing up from it, every loop a regular polygon. Each step
  // along the chain and each base pair is one unit long. Returns [x, y] per base, y up.
  function layout(structure) {
    const n = structure.length;
    const pt = pairTable(structure);
    const pos = new Array(n);

    function stem(i, j, dir) {
      while (pt[i + 1] === j - 1 && i + 1 < j - 1) {
        pos[i + 1] = [pos[i][0] + dir[0], pos[i][1] + dir[1]];
        pos[j - 1] = [pos[j][0] + dir[0], pos[j][1] + dir[1]];
        i += 1;
        j -= 1;
      }
      loop(i, j, dir);
    }

    function loop(i, j, dir) {
      const verts = [i];
      const kids = [];
      for (let k = i + 1; k < j;) {
        if (pt[k] < 0) { verts.push(k); k += 1; }
        else { kids.push([k, pt[k]]); verts.push(k, pt[k]); k = pt[k] + 1; }
      }
      verts.push(j);
      const m = verts.length;
      const radius = 1 / (2 * Math.sin(Math.PI / m));
      const apothem = radius * Math.cos(Math.PI / m);
      const mid = [(pos[i][0] + pos[j][0]) / 2, (pos[i][1] + pos[j][1]) / 2];
      const c = [mid[0] + dir[0] * apothem, mid[1] + dir[1] * apothem];
      const a0 = Math.atan2(pos[i][1] - c[1], pos[i][0] - c[0]);
      for (let t = 1; t < m - 1; t++) {
        const a = a0 - (t * 2 * Math.PI) / m;   // clockwise: up the left side, over, down to j
        pos[verts[t]] = [c[0] + radius * Math.cos(a), c[1] + radius * Math.sin(a)];
      }
      for (const [p, q] of kids) {
        const md = [(pos[p][0] + pos[q][0]) / 2 - c[0], (pos[p][1] + pos[q][1]) / 2 - c[1]];
        const len = Math.hypot(md[0], md[1]) || 1;
        stem(p, q, [md[0] / len, md[1] / len]);
      }
    }

    let x = 0;
    let overhang = -Infinity;          // right edge of the helices so far, above the line
    for (let i = 0; i < n;) {
      if (pt[i] < 0) { pos[i] = [x, 0]; x += 1; i += 1; continue; }
      // A helix off the 5'-3' line: lay it out at the origin, then slide it right of what's
      // there. Unpaired bases may tuck in under a helix's upper branches, other helices may not.
      const j = pt[i];
      pos[i] = [0, 0];
      pos[j] = [1, 0];
      stem(i, j, [0, 1]);
      let lo = Infinity, hi = -Infinity, low = -Infinity;
      for (let k = i; k <= j; k++) {
        lo = Math.min(lo, pos[k][0]);
        hi = Math.max(hi, pos[k][0]);
        if (pos[k][1] < 1.5) low = Math.max(low, pos[k][0]);
      }
      const dx = Math.max(x, overhang + 1.2) - lo;
      for (let k = i; k <= j; k++) pos[k] = [pos[k][0] + dx, pos[k][1]];
      overhang = hi + dx;
      x = low + dx + 1;
      i = j + 1;
    }
    return pos;
  }

  function regionOf(spec, i) {
    for (const r of spec.regions || []) if (i + 1 >= r.start && i + 1 <= r.end) return r;
    return null;
  }

  function renderRNA(root, spec, opts) {
    const colors = opts.colors || {};
    const seq = spec.sequence;
    const n = seq.length;
    const states = spec.states;
    const layouts = states.map((s) => layout(s.structure));
    const pts = states.map((s) => pairTable(s.structure));
    const U = 26;                      // pixels per unit
    const R = 10.5;                    // a base's circle

    // One frame that fits every fold, so nothing jumps out of view while it refolds.
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (const L of layouts) for (const [x, y] of L) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
    const pad = 2.6;
    const vb = [(x0 - pad) * U, (-y1 - pad) * U, (x1 - x0 + 2 * pad) * U, (y1 - y0 + 2 * pad) * U];
    const drawing = svg("svg", { viewBox: vb.join(" "), class: "rna-svg", role: "img",
                                 "aria-label": "RNA secondary structure: " + states.map((s) => s.name).join(", ") });

    const backbone = svg("path", { fill: "none", stroke: LINE, "stroke-width": 2.2, "stroke-linejoin": "round" });
    const pairLayer = svg("g", {});
    const ligandLayer = svg("g", { opacity: 0 });
    const baseLayer = svg("g", {});
    const labelLayer = svg("g", {});
    drawing.append(backbone, pairLayer, ligandLayer, baseLayer, labelLayer);

    const bases = [];
    for (let i = 0; i < n; i++) {
      const r = regionOf(spec, i);
      const col = r ? "#" + (colors[r.color] || "1D1D1F") : null;
      const g = svg("g", {});
      const title = svg("title", {});
      title.textContent = seq[i] + (i + 1) + (r ? " · " + r.name : "");
      g.append(title,
        svg("circle", { r: R, fill: "#FFFFFF" }),   // hides the backbone under a tinted base
        svg("circle", { r: R, fill: col ? col : "#FFFFFF", "fill-opacity": col ? 0.16 : 1, stroke: col || LINE, "stroke-width": col ? 1.6 : 1.2 }));
      const t = svg("text", { "text-anchor": "middle", "dominant-baseline": "central", "font-size": 14, fill: col || SOFT_INK, class: "rna-letter" });
      t.textContent = seq[i];
      g.append(t);
      baseLayer.append(g);
      bases.push(g);
    }

    const ends = [svg("text", { class: "rna-end" }), svg("text", { class: "rna-end" })];
    ends[0].textContent = "5′";
    ends[1].textContent = "3′";
    labelLayer.append(...ends);

    const regionLabels = (spec.regions || []).map((r) => {
      const t = svg("text", { class: "rna-region", "text-anchor": "middle", "dominant-baseline": "central", fill: "#" + (colors[r.color] || "1D1D1F") });
      t.textContent = r.name;
      labelLayer.append(t);
      return { r, t };
    });

    const lig = spec.ligand;
    let ligandDot = null, ligandText = null;
    if (lig) {
      ligandDot = svg("circle", { r: 10, fill: LIGAND });
      ligandText = svg("text", { class: "rna-ligand", "text-anchor": "middle", fill: LIGAND });
      ligandText.textContent = lig.name;
      ligandLayer.append(ligandDot, ligandText);
    }

    const pairSets = pts.map((pt) => {
      const g = svg("g", { opacity: 0 });
      for (let i = 0; i < n; i++) if (pt[i] > i) g.append(svg("line", { stroke: SOFT_INK, "stroke-width": 1.4, "data-i": i, "data-j": pt[i] }));
      pairLayer.append(g);
      return g;
    });

    // Draw every base at positions P (unit coordinates, y up), labelled for pair table pt.
    function place(P, pt) {
      const sx = (i) => P[i][0] * U;
      const sy = (i) => -P[i][1] * U;
      backbone.setAttribute("d", P.map((p, i) => (i ? "L" : "M") + (p[0] * U).toFixed(1) + " " + (-p[1] * U).toFixed(1)).join(" "));
      bases.forEach((g, i) => g.setAttribute("transform", `translate(${sx(i).toFixed(1)} ${sy(i).toFixed(1)})`));
      for (const g of pairSets) {
        for (const line of g.children) {
          const i = +line.dataset.i, j = +line.dataset.j;
          const ax = sx(i), ay = sy(i), bx = sx(j), by = sy(j);
          const d = Math.hypot(bx - ax, by - ay) || 1;
          const ux = ((bx - ax) / d) * R, uy = ((by - ay) / d) * R;
          line.setAttribute("x1", ax + ux); line.setAttribute("y1", ay + uy);
          line.setAttribute("x2", bx - ux); line.setAttribute("y2", by - uy);
        }
      }
      ends[0].setAttribute("x", sx(0) - 22); ends[0].setAttribute("y", sy(0) + 4);
      ends[1].setAttribute("x", sx(n - 1) + 12); ends[1].setAttribute("y", sy(n - 1) + 4);
      // Region labels sit just outside their stretch: below the line, or away from the middle.
      let cx = 0, cy = 0;
      for (const p of P) { cx += p[0]; cy += p[1]; }
      cx /= n; cy /= n;
      for (const { r, t } of regionLabels) {
        let mx = 0, my = 0;
        for (let i = r.start - 1; i < r.end; i++) { mx += P[i][0]; my += P[i][1]; }
        const k = r.end - r.start + 1;
        mx /= k; my /= k;
        // On a helix: beside the strand, away from its partner. On the line: below it.
        // In a loop: away from the middle of the drawing.
        let px = 0, py = 0, paired = 0;
        for (let i = r.start - 1; i < r.end; i++) if (pt[i] >= 0) { px += P[pt[i]][0]; py += P[pt[i]][1]; paired += 1; }
        let dx = 0, dy = -1.7;
        if (paired >= k / 2) {
          px /= paired; py /= paired;
          const d = Math.hypot(mx - px, my - py) || 1;
          dx = ((mx - px) / d) * 2.1; dy = ((my - py) / d) * 2.1;
        } else if (Math.abs(my) > 0.5) {
          const d = Math.hypot(mx - cx, my - cy) || 1;
          dx = ((mx - cx) / d) * 2.2; dy = ((my - cy) / d) * 2.2;
        }
        t.setAttribute("x", (mx + dx) * U); t.setAttribute("y", -(my + dy) * U);
      }
      if (lig) {
        let mx = 0, my = 0;
        for (const b of lig.near) { mx += P[b - 1][0]; my += P[b - 1][1]; }
        mx /= lig.near.length; my /= lig.near.length;
        ligandDot.setAttribute("cx", mx * U); ligandDot.setAttribute("cy", -my * U);
        ligandText.setAttribute("x", mx * U); ligandText.setAttribute("y", -my * U + 24);
      }
    }

    // ---- the controls: one button per fold, and what the fold means -------------------------
    let current = 0;
    let anim = null;
    const buttons = states.map((s, k) => el("button", { type: "button", class: "fig-tab", role: "radio", "aria-checked": String(k === 0),
                                                         onClick: () => show(k, true) }, s.name));
    const note = el("p", { class: "fig-note" });
    const energy = el("p", { class: "fig-energy" });
    const replay = states.length > 1 ? el("button", { type: "button", class: "fig-play", onClick: () => cycle() }, "▶ Refold") : null;

    function describe(k) {
      buttons.forEach((b, i) => b.setAttribute("aria-checked", String(i === k)));
      note.textContent = states[k].note;
      const e = states[k].energy;
      energy.textContent = typeof e === "number" ? "ΔG = " + String(e).replace("-", "−") + " kcal/mol (ViennaRNA)" : "";
      energy.hidden = typeof e !== "number";
    }

    function show(k, animate) {
      if (anim) cancelAnimationFrame(anim);
      const from = layouts[current], to = layouts[k];
      const fromPairs = pairSets[current], toPairs = pairSets[k];
      const fromLig = lig && states[current].ligand ? 1 : 0, toLig = lig && states[k].ligand ? 1 : 0;
      const fromIndex = current;
      current = k;
      describe(k);
      if (!animate || REDUCED || from === to) {
        place(to, pts[k]);
        pairSets.forEach((g, i) => g.setAttribute("opacity", i === k ? 1 : 0));
        ligandLayer.setAttribute("opacity", toLig);
        return;
      }
      const start = performance.now();
      const ms = 1400;
      const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
      const frame = (now) => {
        const t = Math.min(1, (now - start) / ms);
        const e = ease(t);
        place(from.map((p, i) => [p[0] + (to[i][0] - p[0]) * e, p[1] + (to[i][1] - p[1]) * e]), t < 0.5 ? pts[fromIndex] : pts[k]);
        // old pairs let go first, new ones snap in at the end
        if (fromPairs !== toPairs) {
          fromPairs.setAttribute("opacity", Math.max(0, 1 - t * 3));
          toPairs.setAttribute("opacity", Math.max(0, t * 3 - 2));
        }
        ligandLayer.setAttribute("opacity", fromLig + (toLig - fromLig) * e);
        if (t < 1) anim = requestAnimationFrame(frame);
      };
      anim = requestAnimationFrame(frame);
    }

    function cycle() {
      show(0, false);
      states.slice(1).forEach((_, k) => setTimeout(() => show(k + 1, true), 600 + k * 2200));
    }

    show(0, false);
    root.classList.add("fig", "fig-rna");
    root.append(
      states.length > 1 ? el("div", { class: "fig-tabs", role: "radiogroup", "aria-label": "Fold" }, buttons, replay) : null,
      drawing,
      el("div", { class: "fig-caption-row" }, note, energy));
    if (states.length > 1) whenSeen(root, () => setTimeout(cycle, 300));
  }

  // ==== 3D molecules ==========================================================================

  // "13-19,64-71" -> [13, ..., 19, 64, ..., 71]
  function residues(text) {
    const out = [];
    for (const part of String(text).replace(/\s/g, "").split(",")) {
      const m = part.match(/^(-?\d+)(?:-(-?\d+))?$/);
      if (!m) continue;
      const a = +m[1], b = m[2] === undefined ? a : +m[2];
      for (let k = Math.min(a, b); k <= Math.max(a, b); k++) out.push(k);
    }
    return out;
  }

  function structureUrl(id) {
    // window.GINGER_PDB_BASE lets a page serve its own copies (the published demo does).
    return (window.GINGER_PDB_BASE || "https://files.rcsb.org/download/") + id.toUpperCase() + ".cif";
  }

  function renderMolecule(root, spec, opts) {
    const colors = opts.colors || {};
    root.classList.add("fig", "fig-molecule");
    const stage = el("div", { class: "mol-stage" }, el("p", { class: "mol-status", text: "Loading " + spec.pdb.toUpperCase() + "…" }));
    const legend = el("div", { class: "mol-legend" });
    const tools = el("div", { class: "fig-tabs" });
    const source = el("p", { class: "fig-energy" });
    root.append(tools, stage, el("div", { class: "fig-caption-row" }, legend, source));

    if (!window.$3Dmol) { stage.firstChild.textContent = "3D viewer missing (vendor/3Dmol-min.js)."; return; }
    fetch(structureUrl(spec.pdb))
      .then((r) => (r.ok ? r.text() : Promise.reject(new Error(String(r.status)))))
      .then((text) => draw(text))
      .catch(() => {
        stage.firstChild.textContent = "Couldn’t download PDB " + spec.pdb.toUpperCase() + ". The 3D structure needs an internet connection the first time.";
      });

    function draw(text) {
      stage.replaceChildren();
      const viewer = $3Dmol.createViewer(stage, { backgroundColor: "white", antialias: true });
      const model = viewer.addModel(text, "cif");
      viewer.setStyle({}, { cartoon: { color: "#C9CDD4", thickness: 0.35 } });
      viewer.setStyle({ hetflag: true }, {});           // water and ions out of the way
      const center = (sel) => {
        const atoms = model.selectedAtoms(sel);
        if (!atoms.length) return null;
        const c = atoms.reduce((a, b) => ({ x: a.x + b.x, y: a.y + b.y, z: a.z + b.z }), { x: 0, y: 0, z: 0 });
        return { x: c.x / atoms.length, y: c.y / atoms.length, z: c.z / atoms.length };
      };
      const labelStyle = (hex) => ({ backgroundColor: hex, backgroundOpacity: 0.9, fontColor: "white", fontSize: 13,
                                     font: "KaTeX_Main, Times New Roman, serif", borderRadius: 6, padding: 3, inFront: true });
      const missing = [];
      for (const hl of spec.highlights || []) {
        const hex = "#" + (colors[hl.color] || "1D1D1F");
        const sel = { resi: residues(hl.residues) };
        if (hl.chain) sel.chain = hl.chain;
        const at = center(sel);
        if (!at) { missing.push(hl.label); continue; }
        viewer.setStyle(sel, { cartoon: { color: hex, thickness: 0.35 }, stick: { color: hex, radius: 0.12 } });
        legend.append(el("span", { class: "mol-key" }, el("i", { style: "background:" + hex }), hl.label));
      }
      let ligandSel = null;
      if (spec.ligand && spec.ligand.resn) {
        ligandSel = { resn: spec.ligand.resn.toUpperCase() };
        const at = center(ligandSel);
        if (at) {
          viewer.setStyle(ligandSel, { stick: { color: LIGAND, radius: 0.28 }, sphere: { color: LIGAND, scale: 0.32 } });
          viewer.addLabel(spec.ligand.name, { ...labelStyle(LIGAND), position: { x: at.x, y: at.y + 3, z: at.z } });
          legend.append(el("span", { class: "mol-key" }, el("i", { style: "background:" + LIGAND }), spec.ligand.name));
        } else {
          missing.push(spec.ligand.name);
          ligandSel = null;
        }
      }
      viewer.zoomTo();
      viewer.zoom(1.35);
      viewer.render();
      const title = (text.match(/_struct\.title\s+(?:'([^']*)'|"([^"]*)"|;([^;]*);|(\S.*))/) || []).slice(1).find(Boolean);
      // PDB titles are in capitals: sentence case, but keep codes like C74U or 2,6 as they are.
      const pretty = (t) => t.trim().toLowerCase().replace(/^./, (c) => c.toUpperCase())
        .replace(/\b([a-z]*\d[a-z0-9]*)\b/g, (w) => w.toUpperCase());
      source.textContent = "PDB " + spec.pdb.toUpperCase() + (title ? " · " + pretty(title) : "");
      if (missing.length) source.textContent += " · not found in this structure: " + missing.join(", ");

      let spinning = false;
      const spin = el("button", { type: "button", class: "fig-tab", "aria-pressed": "false", onClick: () => {
        spinning = !spinning;
        viewer.spin(spinning ? "y" : false);
        spin.setAttribute("aria-pressed", String(spinning));
      } }, "Spin");
      tools.append(
        el("button", { type: "button", class: "fig-tab", onClick: () => { viewer.zoomTo(); viewer.zoom(1.35); viewer.render(); } }, "Whole molecule"),
        ligandSel ? el("button", { type: "button", class: "fig-tab", onClick: () => { viewer.zoomTo(ligandSel, 600); viewer.render(); } }, "Binding pocket") : null,
        spin,
        el("span", { class: "fig-hint", text: "drag to turn · scroll to zoom" }));
      if (!REDUCED) whenSeen(stage, () => { viewer.spin("y", 0.6); setTimeout(() => viewer.spin(false), 6000); });
    }
  }

  // ==== MCMC samplers =========================================================================

  // An Ising model on a cyclic n x n lattice, f(x) = theta s^T J s with spins s = 2x - 1, sampled
  // live by two chains from the same start: random-scan Gibbs, and Gibbs-With-Gradients, whose
  // proposal q(i|x) = Softmax(d(x)/2) with d(x) = -(2x - 1) * grad f(x) is drawn as a heat map.
  function renderSampler(root, spec, opts) {
    const colors = opts.colors || {};
    const PROPOSAL = "#" + (colors.green || "1E8A50");
    const GWG = "#" + (colors.blue || "2F6FDB");
    const REJECT = "#" + (colors.red || "C23B32");
    const GIBBS = "#8E8E93";
    const n = spec.size, D = n * n, theta = spec.theta;
    const nbrs = Array.from({ length: D }, (_, i) => {
      const r = Math.floor(i / n), c = i % n;
      return [((r + n - 1) % n) * n + c, ((r + 1) % n) * n + c, r * n + (c + n - 1) % n, r * n + (c + 1) % n];
    });
    const field = (x, i) => nbrs[i].reduce((a, j) => a + 2 * x[j] - 1, 0);              // (Js)_i
    const delta = (x, i) => -4 * theta * (2 * x[i] - 1) * field(x, i);                   // f(x with i flipped) - f(x)
    const agree = (x) => { let a = 0; for (let i = 0; i < D; i++) a += (x[i] === x[nbrs[i][1]]) + (x[i] === x[nbrs[i][3]]); return a / (2 * D); };

    // A small seeded generator, so Reset replays the same start.
    let seed = 7;
    const rand = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };

    // d(x) from one gradient: grad_x f = 4 theta J s, so d_i = -(2x_i - 1) 4 theta (Js)_i.
    // (For this model the first-order estimate equals the true difference.)
    function proposal(x) {
      const logits = new Float64Array(D);
      let top = -Infinity;
      for (let i = 0; i < D; i++) { logits[i] = delta(x, i) / 2; top = Math.max(top, logits[i]); }
      const q = new Float64Array(D);
      let sum = 0;
      for (let i = 0; i < D; i++) { q[i] = Math.exp(logits[i] - top); sum += q[i]; }
      for (let i = 0; i < D; i++) q[i] /= sum;
      return q;
    }

    const chains = {};
    function reset() {
      seed = 7;
      const start = Uint8Array.from({ length: D }, () => (rand() < 0.5 ? 1 : 0));
      chains.gibbs = { x: start.slice(), steps: 0, moved: 0, last: -1, ok: true, trace: [agree(start)] };
      chains.gwg = { x: start.slice(), steps: 0, moved: 0, last: -1, ok: true, trace: [agree(start)], q: proposal(start), lastQ: 0 };
    }

    function stepGibbs(ch) {
      const i = Math.floor(rand() * D);
      const d1 = ch.x[i] ? -delta(ch.x, i) : delta(ch.x, i);                              // f(x_i = 1) - f(x_i = 0)
      const v = rand() < 1 / (1 + Math.exp(-d1)) ? 1 : 0;
      ch.ok = v !== ch.x[i];
      if (ch.ok) ch.moved += 1;
      ch.x[i] = v;
      ch.last = i;
      ch.steps += 1;
    }

    function stepGWG(ch) {
      let u = rand(), i = 0;
      while (i < D - 1 && (u -= ch.q[i]) > 0) i += 1;
      const forward = ch.q[i], gain = delta(ch.x, i);
      ch.x[i] ^= 1;
      const back = proposal(ch.x);
      ch.ok = rand() < Math.min(1, Math.exp(gain) * back[i] / forward);
      if (ch.ok) { ch.moved += 1; ch.q = back; } else ch.x[i] ^= 1;
      ch.last = i;
      ch.lastQ = forward;
      ch.steps += 1;
    }

    // drawing
    const px = Math.max(4, Math.floor(260 / n));
    const lattice = (label) => {
      const canvas = el("canvas", { class: "mc-canvas", width: n * px, height: n * px, "aria-label": label });
      return { canvas, ctx: canvas.getContext("2d") };
    };
    const left = lattice("Gibbs chain"), right = lattice("Gibbs-With-Gradients chain");
    let showMap = true;

    function paint(view, ch, map) {
      const { ctx } = view;
      ctx.clearRect(0, 0, n * px, n * px);
      let top = 0;
      if (map) for (let i = 0; i < D; i++) top = Math.max(top, map[i]);
      for (let i = 0; i < D; i++) {
        const r = Math.floor(i / n), c = i % n;
        ctx.fillStyle = ch.x[i] ? INK : "#F2F2F4";
        ctx.fillRect(c * px, r * px, px, px);
        if (map && map[i] > top * 0.02) {
          ctx.globalAlpha = 0.85 * Math.sqrt(map[i] / top);
          ctx.fillStyle = PROPOSAL;
          ctx.fillRect(c * px + 1, r * px + 1, px - 2, px - 2);
          ctx.globalAlpha = 1;
        }
      }
      if (ch.last >= 0) {
        const r = Math.floor(ch.last / n), c = ch.last % n;
        ctx.strokeStyle = ch.ok ? "#C9760F" : REJECT;
        ctx.lineWidth = 2;
        ctx.strokeRect(c * px - 2, r * px - 2, px + 4, px + 4);
      }
    }

    const W = 900, H = 130, MAXSTEPS = Math.max(4000, 12 * D);
    const chart = svg("svg", { class: "mc-chart", viewBox: `0 0 ${W} ${H + 22}`, role: "img",
                               "aria-label": "Neighbours that agree, over the steps of each chain" });
    const yOf = (v) => H - (v - 0.5) / 0.5 * (H - 8);
    for (const v of [0.5, 0.75, 1]) {
      chart.append(svg("line", { x1: 34, x2: W, y1: yOf(v), y2: yOf(v), stroke: LINE, "stroke-width": 1 }));
      const t = svg("text", { x: 28, y: yOf(v) + 4, "text-anchor": "end", class: "mc-axis" });
      t.textContent = Math.round(v * 100) + "%";
      chart.append(t);
    }
    const xLabel = svg("text", { x: W, y: H + 18, "text-anchor": "end", class: "mc-axis" });
    xLabel.textContent = "steps →  " + MAXSTEPS.toLocaleString("en-US");
    const lines = { gibbs: svg("polyline", { stroke: GIBBS, "stroke-width": 2, fill: "none" }),
                    gwg: svg("polyline", { stroke: GWG, "stroke-width": 2, fill: "none" }) };
    chart.append(xLabel, lines.gibbs, lines.gwg);
    const EVERY = Math.max(1, Math.round(MAXSTEPS / 260));
    const plot = (key) => {
      const tr = chains[key].trace;
      lines[key].setAttribute("points", tr.map((v, k) => `${34 + (k * EVERY / MAXSTEPS) * (W - 34)},${yOf(v)}`).join(" "));
    };

    const stat = () => el("p", { class: "mc-stat" });
    const stats = { gibbs: stat(), gwg: stat() };
    const info = el("p", { class: "fig-note" });
    const pct = (a, b) => (b ? Math.round(100 * a / b) : 0) + "%";

    function draw(detail) {
      paint(left, chains.gibbs, null);
      paint(right, chains.gwg, showMap ? chains.gwg.q : null);
      for (const key of ["gibbs", "gwg"]) {
        const ch = chains[key];
        stats[key].textContent = `${ch.steps.toLocaleString("en-US")} steps · x changed in ${pct(ch.moved, ch.steps)} of them`;
        plot(key);
      }
      const g = chains.gwg;
      if (detail && g.last >= 0) {
        const r = Math.floor(g.last / n) + 1, c = g.last % n + 1;
        info.textContent = `Gibbs-With-Gradients proposed the site in row ${r}, column ${c}, with probability ` +
          `${g.lastQ.toFixed(4)} (a uniform pick would be ${(1 / D).toFixed(4)}), and ${g.ok ? "accepted" : "rejected"} it.`;
      } else if (!detail) {
        info.textContent = "Green: where Gibbs-With-Gradients will propose next, q(i | x). Gibbs picks every site equally often.";
      }
    }

    let running = false, frame = 0;
    function advance(k) {
      for (let s = 0; s < k; s++) {
        stepGibbs(chains.gibbs);
        stepGWG(chains.gwg);
        if (chains.gwg.steps % EVERY === 0) {
          chains.gibbs.trace.push(agree(chains.gibbs.x));
          chains.gwg.trace.push(agree(chains.gwg.x));
        }
      }
    }
    function loop() {
      advance(Math.max(1, Math.round(D / 60)));
      draw(false);
      if (chains.gwg.steps >= MAXSTEPS) setRunning(false);
      if (running) frame = requestAnimationFrame(loop);
    }
    function setRunning(on) {
      running = on && chains.gwg.steps < MAXSTEPS;
      run.textContent = running ? "Pause" : "▶ Run";
      run.setAttribute("aria-pressed", String(running));
      cancelAnimationFrame(frame);
      if (running) frame = requestAnimationFrame(loop);
    }

    const run = el("button", { type: "button", class: "fig-tab", "aria-pressed": "false", onClick: () => setRunning(!running) }, "▶ Run");
    const one = el("button", { type: "button", class: "fig-tab", onClick: () => { setRunning(false); advance(1); draw(true); } }, "One step");
    const again = el("button", { type: "button", class: "fig-tab", onClick: () => { setRunning(false); reset(); draw(false); } }, "Reset");
    const mapBtn = el("button", { type: "button", class: "fig-tab", "aria-pressed": "true", onClick: () => {
      showMap = !showMap;
      mapBtn.setAttribute("aria-pressed", String(showMap));
      draw(false);
    } }, "Proposal map");

    const panel = (title, color, view, key) => el("div", { class: "mc-panel" },
      el("p", { class: "mc-title" }, el("i", { style: "background:" + color }), title), view.canvas, stats[key]);
    root.classList.add("fig", "fig-sampler");
    root.append(
      el("div", { class: "fig-tabs" }, run, one, again, mapBtn,
         el("span", { class: "fig-hint", text: `Ising model · ${n}×${n} lattice · θ = ${theta}` })),
      el("div", { class: "mc-panels" }, panel("Gibbs, one random site", GIBBS, left, "gibbs"),
         panel("Gibbs-With-Gradients", GWG, right, "gwg")),
      el("div", { class: "mc-chart-wrap" }, el("p", { class: "mc-title" }, "Neighbours that agree"), chart),
      el("div", { class: "fig-caption-row" }, info));
    reset();
    draw(false);
    if (!REDUCED) whenSeen(root, () => setRunning(true));
  }

  function render(root, spec, opts) {
    try {
      if (spec.type === "rna") renderRNA(root, spec, opts || {});
      else if (spec.type === "molecule") renderMolecule(root, spec, opts || {});
      else if (spec.type === "sampler") renderSampler(root, spec, opts || {});
    } catch (e) {
      root.textContent = "This figure couldn't be drawn: " + e.message;
    }
  }

  return { render, layout };
})();
