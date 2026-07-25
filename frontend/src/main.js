// src/main.js
import { Api } from "./api/api.js";
import { D3Renderer, AnimationEngine } from "./engine/renderer.js";

/* ============================================================
   Catálogo de categorias e algoritmos.
   Somente "sorting" está implementado no backend; as demais
   categorias aparecem no menu marcadas como "em breve".
   ============================================================ */
const CATALOG = [
  {
    key: "sorting",
    label: "Sorting",
    available: true,
    algorithms: [
      { key: "bubble", name: "Bubble Sort", cases: ["O(n)", "O(n²)", "O(n²)", "O(1)"], worst: "O(n²)" },
      { key: "insertion", name: "Insertion Sort", cases: ["O(n)", "O(n²)", "O(n²)", "O(1)"], worst: "O(n²)" },
      { key: "selection", name: "Selection Sort", cases: ["O(n²)", "O(n²)", "O(n²)", "O(1)"], worst: "O(n²)" },
      { key: "quick", name: "Quick Sort", cases: ["O(n log n)", "O(n log n)", "O(n²)", "O(log n)"], worst: "O(n²)" },
      { key: "merge", name: "Merge Sort", cases: ["O(n log n)", "O(n log n)", "O(n log n)", "O(n)"], worst: "O(n log n)" },
      { key: "heap", name: "Heap Sort", cases: ["O(n log n)", "O(n log n)", "O(n log n)", "O(1)"], worst: "O(n log n)" },
    ],
  },
  {
  key: "linear", label: "Linear", available: true, algorithms: [
    { key: "stack", name: "Pilha (Stack)", cases: ["O(1)", "O(1)", "O(1)", "O(n)"], worst: "O(1)" },
    { key: "queue", name: "Fila (Queue)", cases: ["O(1)", "O(1)", "O(1)", "O(n)"], worst: "O(1)" },
    { key: "linked", name: "Lista Encadeada", cases: ["O(1)", "O(n)", "O(n)", "O(n)"], worst: "O(n)" }
  ]
  },
  { key: "trees", label: "Trees", available: true, algorithms: [
      { key: "bst", name: "Árvore Binária de Busca", cases: ["O(log n)", "O(log n)", "O(n)", "O(n)"], worst: "O(n)" },
      { key: "avl", name: "Árvore AVL", cases: ["O(log n)", "O(log n)", "O(log n)", "O(n)"], worst: "O(log n)" } ] },
  { key: "graphs", label: "Graphs", available: true, algorithms: [
      { key: "bfs", name: "Busca em Largura (BFS)", cases: ["O(V+E)", "O(V+E)", "O(V+E)", "O(V)"], worst: "O(n)" },
      { key: "dfs", name: "Busca em Profundidade (DFS)", cases: ["O(V+E)", "O(V+E)", "O(V+E)", "O(V)"], worst: "O(n)" },
      { key: "dijkstra", name: "Dijkstra", cases: ["O(E log V)", "O(E log V)", "O(E log V)", "O(V)"], worst: "O(n log n)" } ] },
];

/* Índice plano usado pela busca global. */
const FLAT = CATALOG.flatMap((c) =>
  c.algorithms.map((a) => ({ ...a, category: c.key, categoryLabel: c.label, available: c.available }))
);

/* ---------------------- Elementos do DOM ---------------------- */
const $ = (id) => document.getElementById(id);
const statusText = $("status-text");
const metaName = $("meta-name");
const metaTime = $("meta-time");
const metaSpace = $("meta-space");
const complexityBody = $("complexity-body");
const theoryText = $("theory-text");
const codeBody = $("code-body");
const quizContainer = $("quiz-container");
const progressSlider = $("progress-slider");
const progressLabel = $("progress-label");
const btnPlay = $("btn-play");
const customInput = $("custom-input");

/* ---------------------- Instâncias ---------------------- */
const renderer = new D3Renderer("#visualization-container");
const engine = new AnimationEngine(renderer, 600);

/* ---------------------- Estado ---------------------- */
const state = {
  category: null,
  key: null,
  meta: null, // { theory, code, quiz }
  quiz: { index: 0, answered: false },
  activeTab: "theory",
  linear: { contents: [] }, // estado corrente da estrutura linear selecionada
  tree: { current: null }, // raiz corrente da árvore selecionada (round-trip)
  graph: { current: null }, // grafo corrente (nós + arestas + posições)
};

/* Operações interativas por estrutura linear (rótulo, verbo, se pede valor). */
const LINEAR_OPS = {
  stack: [
    { label: "Push", verb: "push", arg: true },
    { label: "Pop", verb: "pop", arg: false },
    { label: "Peek", verb: "peek", arg: false },
  ],
  queue: [
    { label: "Enqueue", verb: "enqueue", arg: true },
    { label: "Dequeue", verb: "dequeue", arg: false },
    { label: "Front", verb: "front", arg: false },
  ],
  linked: [
    { label: "Insert", verb: "insert", arg: true },
    { label: "Search", verb: "search", arg: true },
    { label: "Delete", verb: "delete", arg: true },
  ],
};

/* Operações interativas de árvore. Verbos com valor + travessias. */
const TREE_VALUE_OPS = [
  { label: "Insert", verb: "insert" },
  { label: "Search", verb: "search" },
  { label: "Delete", verb: "delete" },
];
const TREE_TRAVERSALS = [
  { label: "In-ordem", mode: "inorder" },
  { label: "Pré-ordem", mode: "preorder" },
  { label: "Pós-ordem", mode: "postorder" },
  { label: "Nível", mode: "level" },
];

/* Grafos de exemplo (estilo tinyEWG do Sedgewick). Posições relativas 0..1. */
const GRAPH_PRESETS = [
  {
    name: "Ponderado (6 vértices)",
    graph: {
      directed: false,
      nodes: [
        { id: 0, x: 0.10, y: 0.50 },
        { id: 1, x: 0.35, y: 0.16 },
        { id: 2, x: 0.35, y: 0.84 },
        { id: 3, x: 0.66, y: 0.16 },
        { id: 4, x: 0.90, y: 0.50 },
        { id: 5, x: 0.66, y: 0.84 },
      ],
      edges: [
        { u: 0, v: 1, weight: 7 }, { u: 0, v: 2, weight: 9 }, { u: 0, v: 5, weight: 14 },
        { u: 1, v: 2, weight: 10 }, { u: 1, v: 3, weight: 15 }, { u: 2, v: 3, weight: 11 },
        { u: 2, v: 5, weight: 2 }, { u: 3, v: 4, weight: 6 }, { u: 4, v: 5, weight: 9 },
      ],
    },
  },
  {
    name: "Grade (8 vértices)",
    graph: {
      directed: false,
      nodes: [
        { id: 0, x: 0.15, y: 0.2 }, { id: 1, x: 0.5, y: 0.2 }, { id: 2, x: 0.85, y: 0.2 },
        { id: 3, x: 0.15, y: 0.55 }, { id: 4, x: 0.5, y: 0.55 }, { id: 5, x: 0.85, y: 0.55 },
        { id: 6, x: 0.32, y: 0.85 }, { id: 7, x: 0.68, y: 0.85 },
      ],
      edges: [
        { u: 0, v: 1, weight: 4 }, { u: 1, v: 2, weight: 3 }, { u: 0, v: 3, weight: 2 },
        { u: 1, v: 4, weight: 5 }, { u: 2, v: 5, weight: 6 }, { u: 3, v: 4, weight: 1 },
        { u: 4, v: 5, weight: 7 }, { u: 3, v: 6, weight: 8 }, { u: 4, v: 7, weight: 2 },
        { u: 6, v: 7, weight: 5 },
      ],
    },
  },
];

/* ============================================================
   Header: dropdowns de categorias + busca global
   ============================================================ */
function buildCategoryNav() {
  const nav = $("category-nav");
  nav.innerHTML = "";
  for (const cat of CATALOG) {
    const dd = document.createElement("div");
    dd.className = "dropdown";
    const btn = document.createElement("button");
    btn.textContent = cat.label;
    const menu = document.createElement("div");
    menu.className = "dropdown-menu";

    for (const algo of cat.algorithms) {
      const item = document.createElement("button");
      item.className = "dropdown-item";
      item.disabled = !cat.available;
      item.innerHTML = `<span>${algo.name}</span>${
        cat.available ? "" : '<span class="soon">em breve</span>'
      }`;
      if (cat.available) {
        item.addEventListener("click", () => {
          closeDropdowns();
          selectAlgorithm(cat.key, algo.key);
        });
      }
      menu.appendChild(item);
    }

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const wasOpen = dd.classList.contains("open");
      closeDropdowns();
      dd.classList.toggle("open", !wasOpen);
    });

    dd.append(btn, menu);
    nav.appendChild(dd);
  }
}

function closeDropdowns() {
  document.querySelectorAll(".dropdown.open").forEach((d) => d.classList.remove("open"));
}
document.addEventListener("click", closeDropdowns);

/* Busca global */
function setupSearch() {
  const input = $("global-search");
  const list = $("search-results");

  const renderResults = (q) => {
    const query = q.trim().toLowerCase();
    if (!query) {
      list.hidden = true;
      return;
    }
    const hits = FLAT.filter(
      (a) =>
        a.name.toLowerCase().includes(query) ||
        a.categoryLabel.toLowerCase().includes(query)
    ).slice(0, 8);

    list.innerHTML = "";
    if (hits.length === 0) {
      const li = document.createElement("li");
      li.className = "empty";
      li.textContent = "Nenhum algoritmo encontrado.";
      list.appendChild(li);
    } else {
      for (const a of hits) {
        const li = document.createElement("li");
        li.innerHTML = `<span>${a.name}</span><span class="cat">${a.categoryLabel}${
          a.available ? "" : " · em breve"
        }</span>`;
        if (a.available) {
          li.addEventListener("mousedown", () => {
            selectAlgorithm(a.category, a.key);
            input.value = "";
            list.hidden = true;
          });
        } else {
          li.style.opacity = 0.5;
        }
        list.appendChild(li);
      }
    }
    list.hidden = false;
  };

  input.addEventListener("input", (e) => renderResults(e.target.value));
  input.addEventListener("focus", (e) => renderResults(e.target.value));
  input.addEventListener("blur", () => setTimeout(() => (list.hidden = true), 150));
}

/* ============================================================
   Abas do painel lateral
   ============================================================ */
function setupTabs() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const name = tab.dataset.tab;
      state.activeTab = name;
      document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t === tab));
      document
        .querySelectorAll(".tab-panel")
        .forEach((p) => p.classList.toggle("active", p.dataset.panel === name));
    });
  });
}

/* ============================================================
   Realce de sintaxe (Python) + destaque de linha
   ============================================================ */
const PY_KEYWORDS = new Set([
  "def", "for", "in", "range", "if", "elif", "else", "while",
  "return", "break", "and", "or", "not", "None", "True", "False", "len",
]);

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function highlightPython(raw) {
  const esc = escapeHtml(raw);
  return esc.replace(
    /(#.*$)|("[^"]*")|(\b[A-Za-z_]\w*\b)|(\b\d+\b)/g,
    (m, comment, str, word, num) => {
      if (comment) return `<span class="tok-com">${comment}</span>`;
      if (str) return `<span class="tok-str">${str}</span>`;
      if (num) return `<span class="tok-num">${num}</span>`;
      if (word) {
        if (word === "def") return `<span class="tok-kw">def</span>`;
        if (PY_KEYWORDS.has(word)) return `<span class="tok-kw">${word}</span>`;
        return word;
      }
      return m;
    }
  );
}

function renderCode(lines) {
  codeBody.innerHTML = lines
    .map(
      (line, i) =>
        `<span class="code-line" data-line="${i + 1}"><span class="ln">${
          i + 1
        }</span>${highlightPython(line) || " "}</span>`
    )
    .join("");
}

function highlightCodeLine(lineNo) {
  const prev = codeBody.querySelector(".code-line.highlight");
  if (prev) prev.classList.remove("highlight");
  if (!lineNo) return;
  const el = codeBody.querySelector(`.code-line[data-line="${lineNo}"]`);
  if (el) {
    el.classList.add("highlight");
    el.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
}

/* ============================================================
   Quiz interativo
   ============================================================ */
function renderQuiz() {
  const quiz = state.meta?.quiz || [];
  state.quiz.answered = false;
  quizContainer.innerHTML = "";

  if (quiz.length === 0) {
    quizContainer.innerHTML = '<p class="hint">Sem quiz para este algoritmo.</p>';
    return;
  }
  const idx = state.quiz.index % quiz.length;
  const q = quiz[idx];

  const prog = document.createElement("div");
  prog.className = "quiz-progress";
  prog.textContent = `Pergunta ${idx + 1} de ${quiz.length}`;

  const question = document.createElement("p");
  question.className = "quiz-q";
  question.textContent = q.question;

  const opts = document.createElement("div");
  opts.className = "quiz-options";

  q.options.forEach((opt, i) => {
    const b = document.createElement("button");
    b.className = "quiz-opt";
    b.textContent = opt;
    b.addEventListener("click", () => answerQuiz(i, q, opts, explain));
    opts.appendChild(b);
  });

  const explain = document.createElement("div");
  explain.className = "quiz-explain";
  explain.hidden = true;

  const next = document.createElement("button");
  next.className = "btn-ghost quiz-next";
  next.textContent = "Próxima pergunta →";
  next.addEventListener("click", () => {
    state.quiz.index = (idx + 1) % quiz.length;
    renderQuiz();
  });

  quizContainer.append(prog, question, opts, explain, next);
}

function answerQuiz(chosen, q, optsEl, explainEl) {
  if (state.quiz.answered) return;
  state.quiz.answered = true;
  const buttons = [...optsEl.children];
  buttons.forEach((b, i) => {
    b.disabled = true;
    if (i === q.answer) b.classList.add("correct");
    else if (i === chosen) b.classList.add("wrong");
  });
  explainEl.hidden = false;
  explainEl.textContent =
    (chosen === q.answer ? "✔ Correto! " : "✘ Não é bem isso. ") + q.explanation;
}

/* ============================================================
   Seleção e execução de algoritmo
   ============================================================ */
async function selectAlgorithm(category, key) {
  hideHome();
  state.category = category;
  state.key = key;
  state.quiz.index = 0;

  const catalogAlgo = FLAT.find((a) => a.category === category && a.key === key);
  metaName.textContent = catalogAlgo?.name || key;
  statusText.textContent = "Carregando algoritmo…";

  try {
    const meta = await Api.metadata(category, key);
    state.meta = meta;

    // Metadados fixos
    metaTime.textContent = meta.theory.time_complexity;
    metaSpace.textContent = meta.theory.space_complexity;
    theoryText.textContent = meta.theory.description;

    // Tabela de complexidade (casos vêm do catálogo do frontend)
    const cases = catalogAlgo?.cases || [
      "—", meta.theory.time_complexity, meta.theory.time_complexity, meta.theory.space_complexity,
    ];
    const rows = ["Melhor", "Médio", "Pior", "Espaço"];
    complexityBody.innerHTML = rows
      .map((r, i) => `<tr><td>${r}</td><td>${cases[i]}</td></tr>`)
      .join("");

    // Código
    renderCode(meta.code || []);

    // Quiz
    renderQuiz();

    // Modo de execução conforme a categoria.
    if (category === "linear") {
      setupLinearMode(key, catalogAlgo?.name || key);
    } else if (category === "trees") {
      setupTreeMode(key, catalogAlgo?.name || key);
    } else if (category === "graphs") {
      setupGraphMode(key, catalogAlgo?.name || key);
    } else {
      showControls("data");
      await runCurrent();
    }
  } catch (err) {
    statusText.textContent = `Erro: ${err.message}`;
  }
}

/* ============================================================
   Modo linear: botões por operação sobre um estado persistente
   ============================================================ */
const linearControls = $("linear-controls");
const treeControls = $("tree-controls");
const graphControls = $("graph-controls");

/* Mostra apenas um painel: 'data' (sorting), 'linear', 'tree' ou 'graph'. */
function showControls(which) {
  const dataInput = document.querySelector(".data-input");
  if (dataInput) dataInput.hidden = which !== "data";
  if (linearControls) linearControls.hidden = which !== "linear";
  if (treeControls) treeControls.hidden = which !== "tree";
  if (graphControls) graphControls.hidden = which !== "graph";
}

function emptyLinearStep(name) {
  return [
    {
      array_snapshot: [],
      pointers: {},
      code_line: 1,
      description: `${name}: vazia. Use os botões para inserir e remover elementos.`,
    },
  ];
}

function buildLinearControls(key) {
  if (!linearControls) return;
  linearControls.innerHTML = "";

  const val = document.createElement("input");
  val.id = "linear-value";
  val.type = "number";
  val.placeholder = "valor";
  val.className = "linear-value";
  val.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const first = LINEAR_OPS[key].find((o) => o.arg);
      if (first) applyLinearOp(first.verb, true);
    }
  });
  linearControls.appendChild(val);

  for (const op of LINEAR_OPS[key]) {
    const b = document.createElement("button");
    b.className = "btn-solid linear-op";
    b.textContent = op.label;
    b.addEventListener("click", () => applyLinearOp(op.verb, op.arg));
    linearControls.appendChild(b);
  }

  const clear = document.createElement("button");
  clear.className = "btn-ghost";
  clear.textContent = "Limpar";
  clear.addEventListener("click", () => {
    state.linear.contents = [];
    const name = FLAT.find((a) => a.category === "linear" && a.key === state.key)?.name || "Estrutura";
    engine.load(emptyLinearStep(name));
  });
  linearControls.appendChild(clear);
}

function setupLinearMode(key, name) {
  renderer.mode = key;
  state.linear.contents = [];
  buildLinearControls(key);
  showControls("linear");
  engine.load(emptyLinearStep(name));
  seedLinearDemo(key); // popula com um exemplo para não abrir vazio
}

/* Popula a estrutura linear com um exemplo (estado inicial, sem autoplay). */
async function seedLinearDemo(key) {
  const ops =
    key === "stack" ? ["push 5", "push 8", "push 3"]
    : key === "queue" ? ["enqueue 5", "enqueue 8", "enqueue 3"]
    : ["insert 5", "insert 8", "insert 3", "insert 1"];
  renderer.mode = key;
  try {
    const res = await Api.run("linear", key, { initial: [], operations: ops });
    engine.load(res.steps);
    engine.seek(res.steps.length - 1);
    state.linear.contents = (res.steps[res.steps.length - 1]?.array_snapshot || []).slice();
    statusText.textContent = "Exemplo carregado. Continue com os botões ou Limpar.";
  } catch (err) {
    statusText.textContent = `Erro: ${err.message}`;
  }
}

async function applyLinearOp(verb, needsArg) {
  if (state.category !== "linear") return;
  let op = verb;
  if (needsArg) {
    const raw = $("linear-value")?.value ?? "";
    const v = parseInt(raw, 10);
    if (!Number.isFinite(v)) {
      statusText.textContent = "Informe um valor inteiro para esta operação.";
      $("linear-value")?.focus();
      return;
    }
    op = `${verb} ${v}`;
  }

  renderer.mode = state.key;
  statusText.textContent = "Executando…";
  try {
    const res = await Api.run("linear", state.key, {
      initial: state.linear.contents,
      operations: [op],
    });
    engine.load(res.steps);
    engine.play();
    // O estado corrente passa a ser o resultado final desta operação.
    const last = res.steps[res.steps.length - 1];
    state.linear.contents = (last?.array_snapshot || []).slice();
  } catch (err) {
    statusText.textContent = `Erro: ${err.message}`;
  }
}

/* ============================================================
   Modo árvore (BST/AVL): botões de operação + travessias.
   O estado é a raiz da árvore, reenviada a cada operação
   (round-trip), preservando a estrutura entre cliques.
   ============================================================ */
function emptyTreeStep(name) {
  return [
    {
      array_snapshot: [],
      tree: null,
      code_line: null,
      description: `${name}: vazia. Insira valores para construir a árvore.`,
    },
  ];
}

function buildTreeControls(key) {
  if (!treeControls) return;
  treeControls.innerHTML = "";

  const val = document.createElement("input");
  val.id = "tree-value";
  val.type = "number";
  val.placeholder = "valor";
  val.className = "linear-value";
  val.addEventListener("keydown", (e) => {
    if (e.key === "Enter") applyTreeOp("insert", true);
  });
  treeControls.appendChild(val);

  for (const op of TREE_VALUE_OPS) {
    const b = document.createElement("button");
    b.className = "btn-solid linear-op";
    b.textContent = op.label;
    b.addEventListener("click", () => applyTreeOp(op.verb, true));
    treeControls.appendChild(b);
  }

  // Travessias (não pedem valor).
  const sep = document.createElement("span");
  sep.className = "tree-sep";
  sep.textContent = "travessias:";
  treeControls.appendChild(sep);

  for (const tr of TREE_TRAVERSALS) {
    const b = document.createElement("button");
    b.className = "btn-ghost tree-traverse";
    b.textContent = tr.label;
    b.addEventListener("click", () => applyTreeOp(`traverse ${tr.mode}`, false));
    treeControls.appendChild(b);
  }

  const clear = document.createElement("button");
  clear.className = "btn-ghost";
  clear.textContent = "Limpar";
  clear.addEventListener("click", () => {
    state.tree.current = null;
    const name = FLAT.find((a) => a.category === "trees" && a.key === state.key)?.name || "Árvore";
    engine.load(emptyTreeStep(name));
  });
  treeControls.appendChild(clear);

  // Botão para semear uma árvore de exemplo.
  const demo = document.createElement("button");
  demo.className = "btn-ghost";
  demo.textContent = "Exemplo";
  demo.addEventListener("click", () => seedTreeDemo(true));
  treeControls.appendChild(demo);
}

function setupTreeMode(key, name) {
  renderer.mode = key;
  state.tree.current = null;
  buildTreeControls(key);
  showControls("tree");
  engine.load(emptyTreeStep(name));
  seedTreeDemo(false); // popula com um exemplo para não abrir vazio
}

async function applyTreeOp(rawOp, needsArg) {
  if (state.category !== "trees") return;
  let op = rawOp;
  if (needsArg) {
    const v = parseInt($("tree-value")?.value ?? "", 10);
    if (!Number.isFinite(v)) {
      statusText.textContent = "Informe um valor inteiro para esta operação.";
      $("tree-value")?.focus();
      return;
    }
    op = `${rawOp} ${v}`;
  }

  renderer.mode = state.key;
  statusText.textContent = "Executando…";
  try {
    const res = await Api.run("trees", state.key, {
      operations: [op],
      initial: state.tree.current,
    });
    engine.load(res.steps);
    engine.play();
    // A raiz corrente passa a ser a árvore do último passo (round-trip exato).
    state.tree.current = res.steps[res.steps.length - 1]?.tree ?? null;
  } catch (err) {
    statusText.textContent = `Erro: ${err.message}`;
  }
}

/* Semeia uma árvore de exemplo. autoplay=false apenas mostra o resultado. */
async function seedTreeDemo(autoplay = true) {
  if (state.category !== "trees") return;
  const values = state.key === "avl" ? [10, 20, 30, 40, 50, 25] : [50, 30, 70, 20, 40, 60, 80];
  renderer.mode = state.key;
  statusText.textContent = "Montando exemplo…";
  try {
    const res = await Api.run("trees", state.key, {
      operations: values.map((v) => `insert ${v}`),
      initial: null,
    });
    engine.load(res.steps);
    if (autoplay) engine.play();
    else engine.seek(res.steps.length - 1);
    state.tree.current = res.steps[res.steps.length - 1]?.tree ?? null;
    if (!autoplay) statusText.textContent = "Exemplo carregado. Continue com os botões ou Limpar.";
  } catch (err) {
    statusText.textContent = `Erro: ${err.message}`;
  }
}

/* ============================================================
   Modo grafo (BFS/DFS/Dijkstra): presets + edição + execução.
   O grafo (nós/arestas/posições) é fornecido a cada execução;
   os algoritmos não o alteram, só devolvem estados por passo.
   ============================================================ */
const clone = (o) => JSON.parse(JSON.stringify(o));

function graphStaticStep(desc) {
  return [{ array_snapshot: [], graph: state.graph.current, code_line: null, description: desc }];
}

function renderGraphStatic(desc) {
  const gc = state.graph.current;
  const msg = gc && gc.nodes.length
    ? desc || "Grafo carregado. Escolha a origem e clique em Executar."
    : "Grafo vazio. Carregue um exemplo ou adicione vértices.";
  engine.load(graphStaticStep(msg));
  statusText.textContent = msg;
}

function loadPreset(idx) {
  state.graph.current = clone(GRAPH_PRESETS[idx].graph);
  renderGraphStatic();
}

function buildGraphControls() {
  if (!graphControls) return;
  graphControls.innerHTML = "";

  const preset = document.createElement("select");
  preset.id = "graph-preset";
  preset.className = "graph-select";
  GRAPH_PRESETS.forEach((p, i) => {
    const o = document.createElement("option");
    o.value = String(i);
    o.textContent = p.name;
    preset.appendChild(o);
  });
  preset.addEventListener("change", (e) => loadPreset(+e.target.value));
  graphControls.appendChild(labeled("Exemplo", preset));

  const src = document.createElement("input");
  src.id = "graph-source";
  src.type = "number";
  src.value = "0";
  src.className = "linear-value graph-mini";
  graphControls.appendChild(labeled("Origem", src));

  const tgt = document.createElement("input");
  tgt.id = "graph-target";
  tgt.type = "number";
  tgt.placeholder = "opc.";
  tgt.className = "linear-value graph-mini";
  graphControls.appendChild(labeled("Destino", tgt));

  const run = document.createElement("button");
  run.className = "btn-solid linear-op";
  run.textContent = "Executar";
  run.addEventListener("click", applyGraphRun);
  graphControls.appendChild(run);

  // Edição.
  const sep = document.createElement("span");
  sep.className = "tree-sep";
  sep.textContent = "editar:";
  graphControls.appendChild(sep);

  const addV = document.createElement("button");
  addV.className = "btn-ghost";
  addV.textContent = "+ Vértice";
  addV.addEventListener("click", addVertex);
  graphControls.appendChild(addV);

  const eu = mkNum("edge-u", "u");
  const ev = mkNum("edge-v", "v");
  const ew = mkNum("edge-w", "peso");
  graphControls.append(eu, ev, ew);
  const addE = document.createElement("button");
  addE.className = "btn-ghost";
  addE.textContent = "+ Aresta";
  addE.addEventListener("click", () => addEdge(eu, ev, ew));
  graphControls.appendChild(addE);

  const clr = document.createElement("button");
  clr.className = "btn-ghost";
  clr.textContent = "Limpar";
  clr.addEventListener("click", () => {
    state.graph.current = { nodes: [], edges: [], directed: false };
    renderGraphStatic();
  });
  graphControls.appendChild(clr);
}

function labeled(text, el) {
  const wrap = document.createElement("label");
  wrap.className = "graph-field";
  wrap.append(document.createTextNode(text + " "), el);
  return wrap;
}
function mkNum(id, ph) {
  const i = document.createElement("input");
  i.id = "graph-" + id;
  i.type = "number";
  i.placeholder = ph;
  i.className = "linear-value graph-mini";
  return i;
}

function setupGraphMode(key, name) {
  renderer.mode = key;
  buildGraphControls();
  showControls("graph");
  loadPreset(0);
  statusText.textContent = `${name}: carregue/edite o grafo, escolha a origem e Executar.`;
}

async function applyGraphRun() {
  if (state.category !== "graphs") return;
  const gc = state.graph.current;
  if (!gc || !gc.nodes.length) {
    statusText.textContent = "Carregue um exemplo ou adicione vértices primeiro.";
    return;
  }
  const source = parseInt($("graph-source")?.value ?? "0", 10) || 0;
  const rawT = $("graph-target")?.value ?? "";
  const target = rawT === "" ? null : parseInt(rawT, 10);

  renderer.mode = state.key;
  statusText.textContent = "Executando…";
  try {
    const res = await Api.run("graphs", state.key, { graph: gc, source, target });
    engine.load(res.steps);
    engine.play();
  } catch (err) {
    statusText.textContent = `Erro: ${err.message}`;
  }
}

function addVertex() {
  const gc = state.graph.current || { nodes: [], edges: [], directed: false };
  const ids = gc.nodes.map((n) => n.id);
  const id = ids.length ? Math.max(...ids) + 1 : 0;
  const k = gc.nodes.length;
  const ang = k * 0.9; // radianos; distribui numa espiral suave
  const x = Math.min(0.92, Math.max(0.08, 0.5 + 0.34 * Math.cos(ang)));
  const y = Math.min(0.92, Math.max(0.08, 0.5 + 0.34 * Math.sin(ang)));
  gc.nodes.push({ id, x, y });
  state.graph.current = gc;
  renderGraphStatic(`Vértice ${id} adicionado.`);
}

function addEdge(eu, ev, ew) {
  const gc = state.graph.current;
  if (!gc) return;
  const u = parseInt(eu.value, 10);
  const v = parseInt(ev.value, 10);
  if (!Number.isFinite(u) || !Number.isFinite(v)) {
    statusText.textContent = "Informe os vértices u e v da aresta.";
    return;
  }
  const ids = new Set(gc.nodes.map((n) => n.id));
  if (!ids.has(u) || !ids.has(v) || u === v) {
    statusText.textContent = "Aresta inválida: u e v devem existir e ser distintos.";
    return;
  }
  const w = ew.value === "" ? null : parseInt(ew.value, 10);
  gc.edges.push({ u, v, weight: w });
  renderGraphStatic(`Aresta ${u}–${v}${w != null ? " (peso " + w + ")" : ""} adicionada.`);
  eu.value = ev.value = ew.value = "";
}

function parseInput() {
  const raw = customInput.value.trim();
  if (!raw) return null;

  if (state.category === "linear") {
    const ops = raw.split(",").map(s => s.trim()).filter(Boolean);
    return ops.length ? ops : null;
  }

  const nums = raw.split(/[,\s]+/).map(Number).filter(Number.isFinite).map(Math.trunc);
  return nums.length ? nums : null;
}

// Substitua runCurrent integralmente
async function runCurrent() {
  if (!state.category || !state.key) return;
  
  let payload;
  if (state.category === "linear") {
    // Fallback mapeado conforme a estrutura selecionada
    const defaultOps = state.key === "stack" ? ["push 5", "push 8", "pop"] :
                       state.key === "queue" ? ["enqueue 5", "enqueue 8", "dequeue"] :
                       ["insert 5", "insert 8", "search 8", "delete 5"];
    
    const ops = parseInput() || defaultOps;
    customInput.value = ops.join(", ");
    payload = { operations: ops };
  } else {
    const data = parseInput() || [5, 3, 8, 4, 1, 9, 2, 7];
    customInput.value = data.join(", ");
    payload = { data: data };
  }

  // Informa ao renderer o modo de desenho: barras (sorting) ou
  // células/nós (linear). Deve ser definido antes de engine.load().
  renderer.mode = state.category === "linear" ? state.key : null;

  statusText.textContent = "Executando…";
  try {
    const res = await Api.run(state.category, state.key, payload);
    engine.load(res.steps);
  } catch (err) {
    statusText.textContent = `Erro: ${err.message}`;
  }
}

/* ============================================================
   Wiring do player + entrada de dados
   ============================================================ */
function setupControls() {
  $("btn-prev").addEventListener("click", () => engine.stepBackward());
  $("btn-next").addEventListener("click", () => engine.stepForward());
  btnPlay.addEventListener("click", () => engine.toggle());

  progressSlider.addEventListener("input", (e) => engine.seek(+e.target.value));
  $("speed-slider").addEventListener("input", (e) => {
    // Slider maior = mais rápido, então invertemos.
    const min = 60, max = 1200;
    engine.setSpeed(max + min - +e.target.value);
  });

  $("btn-apply").addEventListener("click", runCurrent);
  customInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runCurrent();
  });
  $("btn-random").addEventListener("click", () => {
    seed += 1;
    customInput.value = randomArray().join(", ");
    runCurrent();
  });

  // Callbacks do engine → UI
  engine.onStep = (step, index, total) => {
    if (!step) return;
    statusText.textContent = step.description || "";
    highlightCodeLine(step.code_line);
    progressSlider.max = Math.max(total - 1, 0);
    progressSlider.value = index;
    progressLabel.textContent = `${index + 1} / ${total}`;
  };
  engine.onStateChange = (playing) => {
    btnPlay.textContent = playing ? "⏸" : "▶";
  };

  window.addEventListener("resize", () => {
    const step = engine.steps[engine.currentIndex];
    if (step) renderer.render(step);
  });
}

/* ============================================================
   Página inicial (home) + cards de algoritmos
   ============================================================ */
const CARD_DESCS = {
  bubble: "Troca vizinhos fora de ordem, repetidamente.",
  quick: "Particiona em torno de um pivô e recorre.",
  merge: "Divide, ordena metades e intercala.",
  insertion: "Insere cada elemento na posição correta.",
  selection: "Seleciona o mínimo a cada passo.",
  heap: "Usa um heap máximo para ordenar.",
  stack: "LIFO: empilha e desempilha pelo topo.",
  queue: "FIFO: enfileira no fim, remove na frente.",
  linked: "Nós ligados por ponteiros.",
  bst: "Busca binária dinâmica em árvore.",
  avl: "BST auto-balanceada por rotações.",
  bfs: "Explora o grafo em camadas (fila).",
  dfs: "Aprofunda antes de retroceder (pilha).",
  dijkstra: "Caminhos mínimos com pesos não negativos.",
};

function buildHome() {
  const root = $("home-catalog");
  if (!root) return;
  root.innerHTML = "";
  for (const cat of CATALOG) {
    if (!cat.available) continue;
    const section = document.createElement("div");
    section.className = "home-section";
    const h = document.createElement("h2");
    h.textContent = cat.label;
    section.appendChild(h);
    const grid = document.createElement("div");
    grid.className = "card-grid";
    for (const algo of cat.algorithms) {
      const card = document.createElement("button");
      card.className = "algo-card";
      card.innerHTML =
        `<span class="cat">${cat.label}</span>` +
        `<span class="name">${algo.name}</span>` +
        `<span class="desc">${CARD_DESCS[algo.key] || ""}</span>`;
      card.addEventListener("click", () => selectAlgorithm(cat.key, algo.key));
      grid.appendChild(card);
    }
    section.appendChild(grid);
    root.appendChild(grid.children.length ? section : document.createComment(""));
  }
}

function showHome() {
  engine.pause();
  state.category = null;
  state.key = null;
  $("home").hidden = false;
  document.querySelector(".workspace").hidden = true;
  document.querySelector(".sidebar").hidden = true;
}

function hideHome() {
  $("home").hidden = true;
  document.querySelector(".workspace").hidden = false;
  document.querySelector(".sidebar").hidden = false;
}

/* ============================================================
   Barra lateral redimensionável (arrastar a alça esquerda)
   ============================================================ */
function setupResizer() {
  const grid = document.querySelector(".app-grid");
  const handle = $("sidebar-resizer");
  if (!grid || !handle) return;
  const MIN = 280, MAX = 680;
  let dragging = false;

  const onMove = (e) => {
    if (!dragging) return;
    const w = Math.min(MAX, Math.max(MIN, window.innerWidth - e.clientX));
    grid.style.setProperty("--sidebar-w", `${w}px`);
    const step = engine.steps[engine.currentIndex];
    if (step) renderer.render(step);
  };
  const stop = () => {
    dragging = false;
    handle.classList.remove("dragging");
    document.body.classList.remove("resizing");
    window.removeEventListener("pointermove", onMove);
    window.removeEventListener("pointerup", stop);
    const step = engine.steps[engine.currentIndex];
    if (step) renderer.render(step);
  };
  handle.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    dragging = true;
    handle.classList.add("dragging");
    document.body.classList.add("resizing");
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", stop);
  });
}

/* Gera um array pseudo-aleatório sem depender de Math.random do host. */
let seed = 0;
function randomArray() {
  const size = 7 + (seed % 6);
  const out = [];
  for (let i = 0; i < size; i++) {
    seed = (seed * 1103515245 + 12345 + Date.now() % 997) & 0x7fffffff;
    out.push(1 + (seed % 40));
  }
  return out;
}

/* ============================================================
   Bootstrap
   ============================================================ */
function init() {
  buildCategoryNav();
  setupSearch();
  setupTabs();
  setupControls();
  setupResizer();
  buildHome();
  $("brand-home").addEventListener("click", showHome);
  // Abre na página inicial; usuário escolhe um algoritmo nos cards ou no menu.
  showHome();
}

init();
