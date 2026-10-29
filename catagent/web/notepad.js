// The Notepad page. Python (notepad.py) owns the data: the notes, the projects and the clip
// files. This page shows them and sends what you click back through the "bridge" object.
// Only view details live here: which folders are open, which one is selected, the search.

"use strict";

// Coloured ink for ideas, and a highlighter for the few results that matter (study.py has the same).
const COLORS = { blue: "2F6FDB", orange: "C9760F", green: "1E8A50", purple: "7A4FD0", red: "C23B32" };
const OLD_COLORS = { beige: "orange", pink: "red" };   // clips saved before the colours were inks
const MACROS = { "\\hl": "\\htmlClass{hl}{#1}" };
for (const [name, hex] of Object.entries(COLORS)) MACROS["\\" + name] = "\\textcolor{" + hex + "}{#1}";  // no "#": it would read as an argument
for (const [old, name] of Object.entries(OLD_COLORS)) MACROS["\\" + old] = MACROS["\\" + name];
const KATEX = { throwOnError: false, strict: false, trust: (c) => c.command === "\\htmlClass" };
const KIND_NAMES = { solution: "Solution", note: "Study note", idea: "Idea" };
const SUGGEST_TOP = ["Week 1", "Week 2", "Exams", "Assignments", "Projects"];
const SUGGEST_SUB = ["Questions", "Lectures", "Assignments", "Exams", "Projects"];

const ICONS = {
  check: '<path d="M5 12l5 5 9-10"/>',
  clip: '<path d="M20 11.5l-7.8 7.8a5 5 0 0 1-7.1-7.1l8.5-8.5a3.3 3.3 0 0 1 4.7 4.7l-8.5 8.5a1.7 1.7 0 0 1-2.4-2.4l7.8-7.8"/>',
  sidebar: '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M15 4v16"/>',
  board: '<rect x="6" y="4" width="12" height="17" rx="2"/><path d="M9 3h6v3H9z"/>',
  chevron: '<path d="M9 6l6 6-6 6"/>',
  down: '<path d="M6 9l6 6 6-6"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  finder: '<path d="M4 7a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M10 13h6M13 10l3 3-3 3"/>',
  trash: '<path d="M5 7h14M10 7V5h4v2M7 7l1 12h8l1-12"/>',
  x: '<path d="M6 6l12 12M18 6L6 18"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="2"/>',
  arrow: '<path d="M12 19V5M6 11l6-6 6 6"/>',
  solution: '<path d="M6 3h8l5 5v13H6z"/><path d="M9.5 14l2 2 4-4"/>',
  note: '<path d="M6 3h8l5 5v13H6z"/><path d="M9.5 12.5h6M9.5 16.5h6"/>',
  idea: '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
};

// ---- tiny DOM helpers -------------------------------------------------------------------------

function h(tag, props, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key.startsWith("on")) el.addEventListener(key.slice(2).toLowerCase(), value);
    else if (key === "class") el.className = value;
    else if (key === "text") el.textContent = value;
    else el.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

function icon(name, cls) {
  const span = document.createElement("span");
  span.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"' + (cls ? ' class="' + cls + '"' : "") + ">" + ICONS[name] + "</svg>";
  return span.firstChild;
}

function kindIcon(kind) {
  return icon(kind in ICONS ? kind : "note", "k-" + kind);
}

// A display formula, rendered by KaTeX. A formula KaTeX can't read shows its source in red.
function formula(latex, cls) {
  const el = h("div", { class: cls || "formula" });
  try {
    katex.render(latex, el, { ...KATEX, displayMode: true, macros: { ...MACROS } });
  } catch (e) {
    el.textContent = latex;
  }
  return el;
}

// A sentence with $inline math$ in it.
function prose(text, tag, cls) {
  const el = h(tag || "span", { class: cls || null, text: text || "" });
  if (window.renderMathInElement) {
    renderMathInElement(el, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true },
        { left: "$", right: "$", display: false },
      ],
      ...KATEX,
      macros: { ...MACROS },
    });
  }
  return el;
}

// ---- talking to Python ------------------------------------------------------------------------

let bridge = null;

function call(method, ...args) {
  return new Promise((resolve) => {
    bridge[method](...args, (raw) => resolve(raw ? JSON.parse(raw) : {}));
  });
}

// Ask Python to do something, then redraw. Returns the reply, or null if it didn't work.
async function act(method, ...args) {
  const result = await call(method, ...args);
  if (result.error) { alertReply(result.error); return null; }
  update(result.state);
  return result;
}

// ---- state ----------------------------------------------------------------------------------

let S = null;                  // everything Python sends: see Notepad.state() in notepad.py
const view = {
  openFolders: new Set(),
  selected: null,              // folder path ("" is the project itself); null until first render
  query: "",
  adding: null,                // "top" | "sub" | "note"
  draft: "",
  noteKind: "note",
  formError: "",
  projectMenu: false,
  projectDraft: "",
  projectError: "",
  replyHidden: false,
  knownProject: null,
};

function folderPaths(nodes, out = []) {
  for (const n of nodes) if (n.type === "folder") { out.push(n.path); folderPaths(n.children, out); }
  return out;
}

function countClips(nodes) {
  let n = 0;
  for (const node of nodes) n += node.type === "clip" ? 1 : countClips(node.children);
  return n;
}

function allClips(nodes, out = []) {
  for (const n of nodes) {
    if (n.type === "clip") out.push(n);
    else allClips(n.children, out);
  }
  return out;
}

function prettyPath(folder) {
  return [S.project, ...(folder ? folder.split("/") : [])].join(" › ");
}

function parentOf(path) {
  const i = path.lastIndexOf("/");
  return i < 0 ? "" : path.slice(0, i);
}

function reveal(folder) {
  for (let p = folder; p; p = parentOf(p)) view.openFolders.add(p);
}

function update(state) {
  S = state;
  if (view.knownProject !== S.project) {
    // A different project: start with its top-level folders open and the first one selected.
    view.knownProject = S.project;
    view.openFolders = new Set(S.tree.filter((n) => n.type === "folder").map((n) => n.path));
    view.selected = null;
    view.query = "";
    view.adding = null;
  }
  const folders = folderPaths(S.tree);
  if (view.selected === null || (view.selected !== "" && !folders.includes(view.selected))) {
    view.selected = S.currentPath ? parentOf(S.currentPath) : (folders[0] || "");
  }
  if (S.reply || S.error) view.replyHidden = false;
  render();
}

// ---- rendering -------------------------------------------------------------------------------

function render() {
  renderTitlebar();
  renderNotes();
  renderChat();
  renderSide();
}

function renderTitlebar() {
  const button = document.getElementById("project-button");
  button.replaceChildren(S.project, icon("down"));
  button.setAttribute("aria-expanded", String(view.projectMenu));
  const pop = document.getElementById("project-popover");
  pop.hidden = !view.projectMenu;
  if (view.projectMenu) {
    pop.replaceChildren(
      ...S.projects.map((name) => h("button", {
        type: "button", class: "item", role: "menuitemradio", "aria-checked": String(name === S.project),
        onClick: () => { view.projectMenu = false; act("selectProject", name); },
      }, h("span", { class: "name", style: "flex:1" }, name), name === S.project ? icon("check") : null)),
      h("hr"),
      h("form", {
        onSubmit: async (e) => {
          e.preventDefault();
          const result = await call("makeProject", view.projectDraft);
          if (result.error) { view.projectError = result.error; renderTitlebar(); return; }
          view.projectMenu = false; view.projectDraft = ""; view.projectError = "";
          update(result.state);
        },
      },
        h("label", { for: "new-project", class: "eyebrow" }, "New project"),
        h("input", { id: "new-project", type: "text", placeholder: "e.g. Math 1", value: view.projectDraft,
                     onInput: (e) => { view.projectDraft = e.target.value; } }),
        view.projectError ? h("span", { class: "form-error" }, view.projectError) : null,
        h("div", { class: "form-actions" }, h("button", { type: "submit", class: "create" }, "Create"))),
    );
  }
  document.getElementById("export").disabled = !(S.current && S.current.kind === "solution");
  const toggle = document.getElementById("side-toggle");
  toggle.setAttribute("aria-pressed", String(S.sideOpen));
  document.getElementById("side").classList.toggle("closed", !S.sideOpen);
}

function renderNotes() {
  const root = document.getElementById("notes");
  const current = S.current;
  if (!current) {
    root.dataset.noteId = "";
    root.replaceChildren(h("div", { class: "empty" },
      S.asking ? h("span", { class: "writing", "aria-label": S.catName + " is writing" }, h("i"), h("i"), h("i")) : null,
      h("h1", {}, S.asking ? S.catName + " is writing your notes" : "Your study notes go here"),
      h("p", {}, S.asking
        ? "They'll appear here as soon as they're ready."
        : "Ask " + S.catName + " about a problem below, like “Prove that Trace(AB) = Trace(BA)”, or open a clip from the clipboard.")));
    return;
  }
  if (current.kind !== "solution") {
    root.dataset.noteId = "";
    root.replaceChildren(h("div", { class: "note-card" },
      h("span", { class: "kind" }, kindIcon(current.kind), KIND_NAMES[current.kind]),
      prose(current.title, "h1"),
      current.text && current.text !== current.title ? prose(current.text, "div", "text") : null));
    return;
  }
  // Rebuild only when different notes open. Interactive figures (a 3D view you've turned, an
  // RNA mid-refold) survive everything else; only the clip status is refreshed.
  if (root.dataset.noteId === current.id) {
    const slot = root.querySelector(".clip-slot");
    if (slot) slot.replaceChildren(clipStatus("pill"));
    return;
  }
  root.dataset.noteId = current.id;
  const n = current.notes;
  let figures = 0;

  // The colours, written in their own ink: "class 1 · class 2 · the gain".
  const legend = (n.colors || []).map((c) => {
    const el = prose(c.meaning, "span");
    el.style.color = "#" + (COLORS[OLD_COLORS[c.color] || c.color] || "1D1D1F");
    return el;
  });

  const given = h("div", { class: "given" },
    n.have.map((row) => h("div", { class: "fact" },
      h("span", { class: "tag" }, "(" + row.label.replace(/^\(|\)$/g, "") + ")"),
      h("div", { class: "fact-body" }, formula(row.formula), prose(row.meaning, "p", "meaning")))),
    h("div", { class: "fact goal" },
      h("span", { class: "tag" }, "To show."),
      h("div", { class: "fact-body" }, formula(n.goal.formula), prose(n.goal.meaning, "p", "meaning"))));

  // Each step is one board: the derivation, with its figure beside it when there is one.
  const steps = n.steps.map((s, i) => {
    let figure = null;
    if (s.figure) {
      figures += 1;
      const drawn = h("div", { class: "drawn" });
      Figures.render(drawn, s.figure, { colors: COLORS });
      figure = h("figure", { class: "figure" }, drawn,
        h("figcaption", {}, h("b", {}, "Figure " + figures + ". "), s.caption ? prose(s.caption) : null));
    } else if (s.picture) {
      figures += 1;
      figure = h("figure", { class: "figure" },
        formula(s.picture, "figure-math"),
        h("figcaption", {}, h("b", {}, "Figure " + figures + ". "), s.caption ? prose(s.caption) : null));
    }
    // Figures the Notepad draws (a fold, a 3D molecule) get the full width, under the derivation.
    return h("section", { class: "board" + (figure ? " has-figure" : "") + (s.figure ? " stacked" : "") },
      h("div", { class: "derivation" },
        h("span", { class: "step-no" }, "Step " + (i + 1)),
        prose(s.title, "h3"),
        prose("Uses " + s.uses + ".", "p", "uses"),
        formula(s.formula, "display"),
        s.expansion ? formula(s.expansion, "expansion") : null,
        prose(s.meaning, "p", "what")),
      figure);
  });

  const sol = n.solution;
  const writeup = h("ol", { class: "writeup" }, sol.steps.map((s) =>
    h("li", {}, prose(s.text, "p"), s.formula ? formula(s.formula, "writeup-math") : null)));

  const options = (n.options || []).length ? h("section", { class: "section" },
    h("h2", {}, "Every option, checked"),
    h("div", { class: "table-wrap" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", {}, "Option"), h("th", {}, "What it computes"), h("th", {}, "Value"), h("th", {}, "Verdict"))),
      h("tbody", {}, n.options.map((o) => h("tr", { class: o.correct ? "right" : null },
        h("td", { class: "letter" }, o.option, o.correct ? icon("check") : null),
        h("td", {}, inline(o.computes)),
        h("td", { class: "num" }, o.value || "–"),
        h("td", {}, prose(o.verdict)))))))) : null;

  root.replaceChildren(...[
    h("header", { class: "doc-head" },
      h("span", { class: "kicker" }, "Worked solution"),
      prose(n.title, "h1"),
      legend.length ? h("div", { class: "legend" }, legend) : null),
    h("section", { class: "problem" }, h("span", { class: "label" }, "Question"), prose(n.asked, "p", "asked")),
    n.short_answer ? h("section", { class: "short" }, h("span", { class: "label" }, "Short answer"), prose(n.short_answer, "p")) : null,
    h("section", { class: "section" }, h("h2", {}, "Given"), given),
    h("section", { class: "section" },
      h("h2", {}, "Solution"),
      n.example ? prose(n.example, "p", "lead") : null,
      h("div", { class: "boards" }, steps)),
    h("section", { class: "section writeup-box" },
      h("div", { class: "head" }, h("h2", {}, "Write-up"), h("span", { class: "clip-slot" }, clipStatus("pill"))),
      sol.intro ? prose(sol.intro, "p") : null,
      writeup,
      h("p", { class: "remark" }, h("b", {}, "Key idea. "), prose(sol.key_idea)),
      sol.watch_out ? h("p", { class: "remark" }, h("b", {}, "Watch out. "), prose(sol.watch_out)) : null),
    options,
    n.answer ? h("section", { class: "final" }, h("span", { class: "label" }, "Answer"), formula(n.answer, "answer-math")) : null,
  ].filter(Boolean));
  requestAnimationFrame(fitFigures);
}

// A figure beside its derivation can be wider than its column (a matrix product, say). If it would
// have to shrink below 80%, it moves under the derivation instead; whatever is still too wide
// shrinks to fit, down to 60%, and only then scrolls.
function fitFigures() {
  for (const el of document.querySelectorAll(".figure-math")) {
    const board = el.closest(".board");
    board.classList.remove("stacked");
    if (fit(el) < 0.8 && getComputedStyle(board).gridTemplateColumns.split(" ").length > 1) {
      board.classList.add("stacked");
      fit(el);
    }
  }
}

function fit(el) {
  el.style.fontSize = "";
  const base = parseFloat(getComputedStyle(el).fontSize);
  const pad = 32;   // its left and right padding
  const scale = Math.min(1, (el.clientWidth - pad) / (el.scrollWidth - pad));
  if (scale < 1) el.style.fontSize = Math.max(0.6, scale) * base + "px";
  return scale;
}
window.addEventListener("resize", () => requestAnimationFrame(fitFigures));

// An inline formula, for table cells.
function inline(latex) {
  const el = h("span", { class: "inline-math" });
  try {
    katex.render(latex, el, { ...KATEX, displayMode: false, macros: { ...MACROS } });
  } catch (e) {
    el.textContent = latex;
  }
  return el;
}

// Where the open note is clipped, or a button to clip it into the selected folder.
function clipStatus(style) {
  if (S.currentPath) {
    const where = prettyPath(parentOf(S.currentPath));
    if (style === "pill") return h("span", { class: "status-pill" }, icon("check"), "Clipped to " + where);
    return h("div", { class: "clipped" }, icon("check"), h("span", {}, "Clipped to ", h("b", {}, where)),
      h("button", { type: "button", class: "link-button", onClick: unclip }, "Undo"));
  }
  return h("button", { type: "button", class: "dark-button", onClick: clipHere },
    icon("clip"), "Clip solution to " + prettyPath(view.selected));
}

function clipHere() {
  reveal(view.selected);
  return S.currentPath ? act("moveClip", S.currentPath, view.selected) : act("clip", view.selected);
}

function unclip() {
  return act("deleteClip", S.currentPath);
}

function alertReply(message) {
  S.error = message;
  view.replyHidden = false;
  renderChat();
}

function renderChat() {
  const reply = document.getElementById("reply");
  const text = S.error || S.reply;
  reply.hidden = !text || view.replyHidden;
  reply.className = "reply" + (S.error ? " error" : "");
  if (text) {
    reply.replaceChildren(
      h("span", { class: "who" }, S.error ? "Oops" : S.catName),
      prose(text, "span", "text"),
      h("button", { type: "button", class: "close", "aria-label": "Dismiss", onClick: () => { view.replyHidden = true; renderChat(); } }, icon("x")));
  }
  const send = document.getElementById("send");
  send.classList.toggle("stop", S.asking);
  send.setAttribute("aria-label", S.asking ? "Stop" : "Send");
  send.replaceChildren(icon(S.asking ? "stop" : "arrow"));
  const input = document.getElementById("ask");
  input.placeholder = S.asking ? S.catName + " is working on it…"
    : S.attached.length ? "📎 " + S.attached.join(", ") + " — what should I do with it?"
    : "Ask about any step, or paste the next problem…";
}

function renderSide() {
  const side = document.getElementById("side-inner");
  const total = countClips(S.tree);
  const parts = [
    h("div", { class: "side-head" },
      h("span", { class: "badge", "aria-hidden": "true" }, icon("board")),
      h("div", { class: "names" }, h("b", {}, "Clipboard"),
        h("span", {}, S.project + " · " + total + (total === 1 ? " clip" : " clips"))),
      h("button", { type: "button", class: "square-button", "aria-label": "Show in Finder", title: "Show in Finder",
                    onClick: () => act("reveal", view.selected) }, icon("finder")),
      h("button", { type: "button", class: "square-button", "aria-label": "Hide the clipboard",
                    onClick: () => setSide(false) }, icon("sidebar"))),
    thisNoteCard(),
    h("div", { class: "search" }, icon("search"),
      h("input", { type: "search", "aria-label": "Search clips", placeholder: "Search clips", value: view.query,
                   onInput: (e) => { view.query = e.target.value; renderTreeOnly(); } })),
    h("div", { class: "toolbar" },
      h("button", { type: "button", onClick: () => startAdd("top") }, icon("plus"), "Folder"),
      h("button", { type: "button", onClick: () => startAdd("sub"), disabled: view.selected === "" ? true : null,
                    title: view.selected === "" ? "Select a folder first" : null }, icon("plus"), "Subfolder"),
      h("button", { type: "button", onClick: () => startAdd("note") }, icon("plus"), "Note")),
    view.adding ? addForm() : null,
    h("div", { id: "tree-slot" }, treeOrResults()),
    h("div", { class: "legend-row" },
      h("span", {}, kindIcon("solution"), "Solution"),
      h("span", {}, kindIcon("note"), "Study note"),
      h("span", {}, kindIcon("idea"), "Idea")),
  ];
  const focused = document.activeElement && side.contains(document.activeElement) ? document.activeElement.id || document.activeElement.getAttribute("aria-label") : null;
  side.replaceChildren(...parts.filter(Boolean));
  if (focused) {
    const again = document.getElementById(focused) || side.querySelector('[aria-label="' + focused + '"]');
    if (again) again.focus();
  }
}

function renderTreeOnly() {
  document.getElementById("tree-slot").replaceChildren(treeOrResults());
}

function thisNoteCard() {
  const current = S.current;
  if (!current) {
    return h("div", { class: "card" }, h("span", { class: "eyebrow" }, "This note"),
      h("span", { class: "hint" }, "Notes " + S.catName + " writes show up here, ready to clip into a folder."));
  }
  const sub = current.kind === "solution"
    ? "Formulas, " + current.notes.steps.length + " steps and the complete solution"
    : KIND_NAMES[current.kind];
  const elsewhere = S.currentPath && parentOf(S.currentPath) !== view.selected;
  return h("div", { class: "card" },
    h("span", { class: "eyebrow" }, "This note"),
    h("div", { class: "this-note" },
      h("span", { class: "icon", "aria-hidden": "true" }, kindIcon(current.kind)),
      h("div", { style: "flex:1;min-width:0;display:flex;flex-direction:column;gap:1px" },
        prose(current.title, "span", "title"), h("span", { class: "sub" }, sub))),
    S.currentPath ? clipStatus("card") : null,
    !S.currentPath || elsewhere ? h("div", { style: "display:flex;flex-direction:column;gap:8px" },
      h("span", { class: "hint" }, (S.currentPath ? "Move it" : "Clip it") + " into ",
        h("b", {}, prettyPath(view.selected)), ". Pick another folder below to change it."),
      h("button", { type: "button", class: "dark-button", onClick: clipHere },
        icon("clip"), S.currentPath ? "Move here" : "Clip here")) : null);
}

function startAdd(mode) {
  view.adding = mode;
  view.draft = "";
  view.noteKind = "note";
  view.formError = "";
  renderSide();
  const input = document.getElementById("clip-new");
  if (input) input.focus();
}

function addForm() {
  const where = view.selected === "" ? S.project : view.selected.split("/").pop();
  const label = { top: "New folder in " + S.project, sub: "New folder inside " + where, note: "New note in " + prettyPath(view.selected) }[view.adding];
  const suggestions = view.adding === "top" ? SUGGEST_TOP : view.adding === "sub" ? SUGGEST_SUB : [];
  const isNote = view.adding === "note";
  const field = isNote
    ? h("textarea", { id: "clip-new", placeholder: view.noteKind === "idea" ? "e.g. An app that quizzes me on my clips" : "e.g. Trace is linear: $\\operatorname{Tr}(A+B) = \\operatorname{Tr}(A) + \\operatorname{Tr}(B)$",
                      onInput: (e) => { view.draft = e.target.value; }, onKeydown: formKeys }, view.draft)
    : h("input", { id: "clip-new", type: "text", value: view.draft, placeholder: view.adding === "top" ? "e.g. Week 1" : "e.g. Questions",
                   onInput: (e) => { view.draft = e.target.value; }, onKeydown: formKeys });
  return h("form", { class: "add-form", onSubmit: (e) => { e.preventDefault(); create(); } },
    h("label", { for: "clip-new" }, label),
    isNote ? h("div", { class: "segmented", role: "radiogroup", "aria-label": "Kind of note" },
      ["note", "idea"].map((kind) => h("button", {
        type: "button", role: "radio", "aria-checked": String(view.noteKind === kind),
        onClick: () => { view.noteKind = kind; renderSide(); },
      }, KIND_NAMES[kind]))) : null,
    field,
    suggestions.length ? h("div", { class: "chips" }, suggestions.map((name) => h("button", {
      type: "button", onClick: () => { view.draft = name; renderSide(); document.getElementById("clip-new").focus(); },
    }, name))) : null,
    view.formError ? h("span", { class: "form-error", role: "alert" }, view.formError) : null,
    h("div", { class: "form-actions" },
      h("button", { type: "button", class: "cancel", onClick: () => { view.adding = null; renderSide(); } }, "Cancel"),
      h("button", { type: "submit", class: "create" }, "Create")));
}

function formKeys(e) {
  if (e.key === "Escape") { view.adding = null; renderSide(); }
  if (e.key === "Enter" && (e.target.tagName === "INPUT" || e.metaKey)) { e.preventDefault(); create(); }
}

async function create() {
  if (!view.draft.trim()) { view.formError = "Give it a name first."; renderSide(); return; }
  const result = view.adding === "note"
    ? await call("addNote", view.selected, view.noteKind, view.draft)
    : await call("makeFolder", view.adding === "top" ? "" : view.selected, view.draft);
  if (result.error) { view.formError = result.error; renderSide(); return; }
  if (view.adding === "note") reveal(view.selected);
  else { reveal(result.path); view.selected = result.path; }
  view.adding = null;
  update(result.state);
}

function treeOrResults() {
  const q = view.query.trim().toLowerCase();
  if (q) {
    const matches = allClips(S.tree).filter((c) => c.name.toLowerCase().includes(q));
    if (!matches.length) return h("div", { class: "tree-empty" }, "No clips match “" + view.query + "”.");
    return h("div", { class: "tree" }, matches.map((c) => h("button", {
      type: "button", class: "result", onClick: () => { view.query = ""; openClip(c.path); },
    }, kindIcon(c.kind), h("span", { style: "display:flex;flex-direction:column;gap:1px;min-width:0" },
      prose(c.name, "span", "name"), h("span", { class: "path" }, prettyPath(parentOf(c.path)))))));
  }
  if (!S.tree.length) {
    return h("div", { class: "tree-empty" }, "No folders yet. Make one with + Folder, like Week 1, then subfolders for Questions, Exams or Projects.");
  }
  const rows = [];
  const walk = (nodes, depth) => {
    for (const node of nodes) {
      if (node.type === "folder") {
        const open = view.openFolders.has(node.path);
        const selected = view.selected === node.path;
        const count = countClips(node.children);
        rows.push(h("div", { class: "row" + (selected ? " selected" : ""), role: "treeitem",
                             "aria-expanded": String(open), "aria-selected": String(selected), style: "padding-left:" + depth * 16 + "px" },
          h("button", { type: "button", class: "chev" + (open ? " open" : "") + (node.children.length ? "" : " none"),
                        "aria-label": (open ? "Collapse " : "Expand ") + node.name,
                        onClick: () => { open ? view.openFolders.delete(node.path) : view.openFolders.add(node.path); renderSide(); } },
            icon("chevron")),
          h("button", { type: "button", class: "row-main", onClick: () => { view.selected = node.path; view.openFolders.add(node.path); renderSide(); } },
            icon("folder", "folder-icon"), h("span", { class: "name" }, node.name), h("span", { class: "count" }, count ? String(count) : ""))));
        if (open) walk(node.children, depth + 1);
      } else {
        const isOpen = node.path === S.currentPath;
        rows.push(h("div", { class: "row clip" + (isOpen ? " active" : ""), role: "treeitem", "aria-selected": String(isOpen),
                             style: "padding-left:" + (depth * 16 + 10) + "px" },
          h("button", { type: "button", class: "row-main", onClick: () => openClip(node.path) },
            kindIcon(node.kind), prose(node.name, "span", "name"), isOpen ? h("span", { class: "open-tag" }, "open") : null),
          isOpen ? null : h("button", { type: "button", class: "row-delete", "aria-label": "Delete " + node.name, title: "Delete",
                                        onClick: () => deleteClip(node) }, icon("trash"))));
      }
    }
  };
  walk(S.tree, 0);
  return h("div", { class: "tree", role: "tree", "aria-label": "Folders" }, rows);
}

function openClip(path) {
  view.selected = parentOf(path);
  reveal(view.selected);
  return act("openClip", path);
}

function deleteClip(node) {
  if (confirm("Delete “" + node.name + "”? This removes the file from the folder.")) act("deleteClip", node.path);
}

function setSide(open) {
  return act("setSideOpen", open);
}

// ---- chat -------------------------------------------------------------------------------------

async function send() {
  if (S.asking) { act("stop"); return; }
  const input = document.getElementById("ask");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  view.replyHidden = true;
  act("ask", text);
}

// ---- start --------------------------------------------------------------------------------------

function wire() {
  document.getElementById("send").addEventListener("click", send);
  document.getElementById("ask").addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
  document.getElementById("attach").addEventListener("click", () => act("attach"));
  document.getElementById("export").addEventListener("click", () => act("exportTex"));
  document.getElementById("side-toggle").addEventListener("click", () => setSide(!S.sideOpen));
  document.getElementById("project-button").addEventListener("click", () => {
    view.projectMenu = !view.projectMenu;
    view.projectError = "";
    renderTitlebar();
    if (view.projectMenu) document.getElementById("new-project").focus();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && view.projectMenu) { view.projectMenu = false; renderTitlebar(); }
  });
  document.addEventListener("click", (e) => {
    if (view.projectMenu && !e.target.closest(".project-menu")) { view.projectMenu = false; renderTitlebar(); }
  });
  bridge.stateChanged.connect((raw) => update(JSON.parse(raw)));
  act("state");
}

if (window.__gingerBridge) {
  bridge = window.__gingerBridge;   // a stand-in bridge, for testing the page in a browser
  wire();
} else {
  new QWebChannel(qt.webChannelTransport, (channel) => {
    bridge = channel.objects.bridge;
    wire();
  });
}
