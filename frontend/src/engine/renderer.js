// src/engine/renderer.js
import * as d3 from "d3";

/* Paleta cinza + vermelho (estilo Sedgewick & Wayne), alinhada ao style.css */
const COLOR = {
  bar: "#b4b4bd", // neutro (cinza)
  barMuted: "#dcdce1", // fora do active_range
  compared: "#f2a5a5", // vermelho claro (em análise)
  swapped: "#e02424", // vermelho forte (ação)
  sorted: "#3f3f46", // cinza-escuro (concluído/fixado)
  pointer: "#e02424", // vermelho (ponteiros/realce)
  label: "#1c1c1e",
};

/* ============================================================
   D3Renderer — desenha o array como barras verticais,
   colorindo conforme os metadados de cada passo.
   ============================================================ */
export class D3Renderer {
  constructor(selector) {
    this.svg = d3.select(selector);
    this.node = this.svg.node();
    this.margin = { top: 28, right: 12, bottom: 44, left: 12 };
  }

  size() {
    const rect = this.node.getBoundingClientRect();
    return {
      w: Math.max(rect.width, 320),
      h: Math.max(rect.height, 260),
    };
  }

  colorFor(index, step) {
    if (step.swapped_indices?.includes(index)) return COLOR.swapped;
    if (step.compared_indices?.includes(index)) return COLOR.compared;
    if (step.is_sorted) return COLOR.sorted;
    if (step.active_range) {
      const [lo, hi] = step.active_range;
      if (index < lo || index > hi) return COLOR.barMuted;
    }
    return COLOR.bar;
  }

  render(step) {
    if (!step) return;
    // Grafos (BFS/DFS/Dijkstra): nós posicionados + arestas.
    if (this.mode === "bfs" || this.mode === "dfs" || this.mode === "dijkstra") {
      this.svg.select("g.plot").remove();
      this.svg.select("g.linear").remove();
      this.svg.select("g.tree").remove();
      return this.renderGraph(step);
    }
    this.svg.select("g.graph").remove();
    // Árvores (BST/AVL): layout hierárquico de nós.
    if (this.mode === "bst" || this.mode === "avl") {
      this.svg.select("g.plot").remove();
      this.svg.select("g.linear").remove();
      return this.renderTree(step);
    }
    this.svg.select("g.tree").remove();
    // Estruturas lineares usam um layout de células/nós, não barras por valor.
    if (this.mode === "stack" || this.mode === "queue" || this.mode === "linked") {
      this.svg.select("g.plot").remove();
      return this.renderLinear(step);
    }
    this.svg.select("g.linear").remove();
    const data = step.array_snapshot;
    const { w, h } = this.size();
    const { top, right, bottom, left } = this.margin;
    const innerW = w - left - right;
    const innerH = h - top - bottom;

    this.svg.attr("viewBox", `0 0 ${w} ${h}`);

    let g = this.svg.select("g.plot");
    if (g.empty()) {
      g = this.svg.append("g").attr("class", "plot");
      g.append("g").attr("class", "shade-layer");
      g.append("g").attr("class", "bar-layer");
      g.append("g").attr("class", "label-layer");
      g.append("g").attr("class", "pointer-layer");
    }
    g.attr("transform", `translate(${left},${top})`);

    const x = d3
      .scaleBand()
      .domain(d3.range(data.length))
      .range([0, innerW])
      .padding(0.18);

    const minV = Math.min(0, d3.min(data));
    const maxV = Math.max(0, d3.max(data), 1);
    const y = d3.scaleLinear().domain([minV, maxV]).nice().range([innerH, 0]);
    const baseline = y(0);

    /* ---- sombreado do active_range ---- */
    const shade = g
      .select(".shade-layer")
      .selectAll("rect.range-shade")
      .data(step.active_range ? [step.active_range] : []);
    shade
      .enter()
      .append("rect")
      .attr("class", "range-shade")
      .attr("rx", 6)
      .merge(shade)
      .attr("y", -6)
      .attr("height", innerH + 12)
      .attr("x", (d) => x(d[0]) - x.bandwidth() * 0.09)
      .attr("width", (d) => x(d[1]) - x(d[0]) + x.bandwidth() * 1.18);
    shade.exit().remove();

    const t = this.svg.transition().duration(this.duration ?? 260);

    /* ---- barras ---- */
    const bars = g
      .select(".bar-layer")
      .selectAll("rect.bar")
      .data(data, (d, i) => i);
    bars
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("rx", 3)
      .attr("x", (d, i) => x(i))
      .attr("width", x.bandwidth())
      .attr("y", baseline)
      .attr("height", 0)
      .merge(bars)
      .attr("stroke", (d, i) =>
        Object.values(step.pointers || {}).includes(i) ? COLOR.pointer : "none"
      )
      .attr("stroke-width", 2.5)
      .transition(t)
      .attr("x", (d, i) => x(i))
      .attr("width", x.bandwidth())
      .attr("y", (d) => (d >= 0 ? y(d) : baseline))
      .attr("height", (d) => Math.abs(y(d) - baseline))
      .attr("fill", (d, i) => this.colorFor(i, step));
    bars.exit().remove();

    /* ---- rótulos de valor ---- */
    const showLabels = data.length <= 22;
    const labels = g
      .select(".label-layer")
      .selectAll("text.bar-label")
      .data(showLabels ? data : [], (d, i) => i);
    labels
      .enter()
      .append("text")
      .attr("class", "bar-label")
      .attr("text-anchor", "middle")
      .merge(labels)
      .text((d) => d)
      .transition(t)
      .attr("x", (d, i) => x(i) + x.bandwidth() / 2)
      .attr("y", (d) => (d >= 0 ? y(d) - 6 : baseline + 14));
    labels.exit().remove();

    /* ---- ponteiros (pivot, i, j, k…) ---- */
    const ptrs = Object.entries(step.pointers || {}).filter(
      ([, idx]) => idx >= 0 && idx < data.length
    );
    // Agrupa múltiplos ponteiros que caem no mesmo índice.
    const byIndex = {};
    for (const [name, idx] of ptrs) (byIndex[idx] ||= []).push(name);
    const ptrData = Object.entries(byIndex);

    const tags = g
      .select(".pointer-layer")
      .selectAll("text.pointer-tag")
      .data(ptrData, (d) => d[0]);
    tags
      .enter()
      .append("text")
      .attr("class", "pointer-tag")
      .attr("text-anchor", "middle")
      .attr("fill", COLOR.pointer)
      .merge(tags)
      .text((d) => d[1].join(","))
      .transition(t)
      .attr("x", (d) => x(+d[0]) + x.bandwidth() / 2)
      .attr("y", innerH + 22);
    tags.exit().remove();
  }

  /* ============================================================
     renderLinear — visualização estilo Sedgewick & Wayne (algs4):
     nós [ valor | next ] encadeados por setas, terminando em "null".
     Ponteiros nomeados (top/front/rear/head/cur) rotulam os nós.
     NUNCA reordena: a posição segue array_snapshot (ordem de
     inserção), então nada de "ordenar por valor".
     ============================================================ */
  renderLinear(step) {
    const data = step.array_snapshot || [];
    const n = data.length;
    const { w, h } = this.size();
    this.svg.attr("viewBox", `0 0 ${w} ${h}`);

    // Nome do ponteiro de cabeça conforme a estrutura (para o caso vazio).
    const HEAD_NAME = { stack: "top", queue: "front", linked: "head" }[this.mode] || "head";

    // Marcador de seta (uma vez).
    if (this.svg.select("#ll-arrowhead").empty()) {
      this.svg
        .append("defs")
        .append("marker")
        .attr("id", "ll-arrowhead")
        .attr("viewBox", "0 0 10 10")
        .attr("refX", 8)
        .attr("refY", 5)
        .attr("markerWidth", 7)
        .attr("markerHeight", 7)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,0 L10,5 L0,10 z")
        .attr("fill", COLOR.label);
    }

    let g = this.svg.select("g.linear");
    if (g.empty()) {
      g = this.svg.append("g").attr("class", "linear");
      g.append("g").attr("class", "link-layer");
      g.append("g").attr("class", "node-layer");
      g.append("g").attr("class", "ptr-layer");
    }

    const t = this.svg.transition().duration(this.duration ?? 260);
    const pointers = step.pointers || {};
    const valColor = (i) => {
      if (step.swapped_indices?.includes(i)) return COLOR.swapped;
      if (step.compared_indices?.includes(i)) return COLOR.compared;
      return COLOR.bar;
    };

    /* ---- geometria: nós numa linha, encolhendo p/ caber ---- */
    const VAL = 46, NXT = 20, NODE = VAL + NXT, GAP = 34;
    const startX = 22;
    const nullW = 52; // espaço reservado para o "null" final
    const avail = w - startX - nullW;
    const pitchMax = NODE + GAP;
    const pitch = n > 0 ? Math.min(pitchMax, avail / n) : pitchMax;
    const k = Math.max(0.55, Math.min(1, pitch / pitchMax)); // fator de encolhimento
    const vw = VAL * k, nw = NXT * k;
    const nodeH = Math.min(48, h * 0.34);
    const cy = h / 2;
    const y = cy - nodeH / 2;
    const xAt = (i) => startX + i * pitch;
    const nextDot = (i) => xAt(i) + vw + nw / 2; // origem da seta "next"

    /* ---- setas next (cada nó aponta p/ o próximo; último → null) ---- */
    const linkData = [];
    for (let i = 0; i < n; i++) {
      const x2 = i < n - 1 ? xAt(i + 1) : nextDot(n - 1) + 26;
      linkData.push({ i, x1: nextDot(i), x2 });
    }
    const links = g.select(".link-layer").selectAll("line.ll-arrow").data(linkData, (d) => d.i);
    links
      .enter()
      .append("line")
      .attr("class", "ll-arrow")
      .attr("stroke", COLOR.label)
      .attr("stroke-width", 2)
      .attr("marker-end", "url(#ll-arrowhead)")
      .merge(links)
      .transition(t)
      .attr("x1", (d) => d.x1)
      .attr("y1", cy)
      .attr("x2", (d) => d.x2 - 2)
      .attr("y2", cy);
    links.exit().remove();

    /* ---- nós: retângulo do valor + compartimento "next" com ponto ---- */
    const idx = d3.range(n);
    const nodes = g.select(".node-layer").selectAll("g.ll-node").data(idx, (i) => i);
    const enter = nodes.enter().append("g").attr("class", "ll-node");
    enter.append("rect").attr("class", "ll-val-box").attr("rx", 5);
    enter.append("rect").attr("class", "ll-next-box");
    enter.append("circle").attr("class", "ll-ref-dot");
    enter.append("text").attr("class", "ll-val").attr("text-anchor", "middle").attr("dominant-baseline", "central");
    const all = enter.merge(nodes);
    all.select("rect.ll-val-box")
      .transition(t)
      .attr("x", (i) => xAt(i)).attr("y", y).attr("width", vw).attr("height", nodeH)
      .attr("fill", (i) => valColor(i)).attr("stroke", COLOR.label).attr("stroke-width", 1.5);
    all.select("rect.ll-next-box")
      .transition(t)
      .attr("x", (i) => xAt(i) + vw).attr("y", y).attr("width", nw).attr("height", nodeH)
      .attr("fill", COLOR.barMuted).attr("stroke", COLOR.label).attr("stroke-width", 1.5);
    all.select("circle.ll-ref-dot")
      .transition(t)
      .attr("cx", (i) => nextDot(i)).attr("cy", cy).attr("r", 3.2).attr("fill", COLOR.label);
    all.select("text.ll-val")
      .text((i) => data[i]).attr("fill", "#fff")
      .transition(t)
      .attr("x", (i) => xAt(i) + vw / 2).attr("y", cy);
    nodes.exit().remove();

    /* ---- rótulo "null" no fim (ou logo após a cabeça, se vazio) ---- */
    const nullX = n > 0 ? nextDot(n - 1) + 30 : startX + 44;
    const nullSel = g.select(".ptr-layer").selectAll("text.ll-null").data([HEAD_NAME]);
    const nullEnter = nullSel
      .enter()
      .append("text")
      .attr("class", "ll-null")
      .attr("dominant-baseline", "central")
      .attr("text-anchor", "start")
      .attr("fill", COLOR.label);
    nullEnter.merge(nullSel).text("null").attr("x", nullX).attr("y", cy);
    if (n === 0) {
      // Estrutura vazia: desenha "head/top/front → null".
      const emptyArrow = g.select(".link-layer").selectAll("line.ll-empty").data([0]);
      emptyArrow
        .enter()
        .append("line")
        .attr("class", "ll-empty")
        .attr("stroke", COLOR.label)
        .attr("stroke-width", 2)
        .attr("marker-end", "url(#ll-arrowhead)")
        .merge(emptyArrow)
        .attr("x1", startX + 4).attr("y1", cy).attr("x2", nullX - 6).attr("y2", cy);
    } else {
      g.select(".link-layer").selectAll("line.ll-empty").remove();
    }

    /* ---- ponteiros nomeados (acima dos nós, com haste) ---- */
    const byIndex = {};
    for (const [name, i] of Object.entries(pointers)) {
      if (i >= 0 && i < n) (byIndex[i] ||= []).push(name);
    }
    // Caso vazio: mostra a cabeça sobre a origem da seta.
    const ptrData =
      n === 0
        ? [{ i: -1, label: HEAD_NAME, x: startX + 4 }]
        : Object.entries(byIndex).map(([i, names]) => ({
            i: +i,
            label: names.join(", "),
            x: xAt(+i) + vw / 2,
          }));

    const tagY = y - 22;
    // hastes verticais
    const stems = g.select(".ptr-layer").selectAll("line.ll-stem").data(ptrData, (d) => d.i);
    stems
      .enter()
      .append("line")
      .attr("class", "ll-stem")
      .attr("stroke", COLOR.pointer)
      .attr("stroke-width", 1.5)
      .attr("marker-end", "url(#ll-arrowhead)")
      .merge(stems)
      .transition(t)
      .attr("x1", (d) => d.x).attr("y1", tagY + 6).attr("x2", (d) => d.x).attr("y2", y - 3);
    stems.exit().remove();
    // rótulos
    const tags = g.select(".ptr-layer").selectAll("text.ll-ptr").data(ptrData, (d) => d.i);
    tags
      .enter()
      .append("text")
      .attr("class", "ll-ptr")
      .attr("text-anchor", "middle")
      .attr("fill", COLOR.pointer)
      .merge(tags)
      .text((d) => d.label)
      .transition(t)
      .attr("x", (d) => d.x)
      .attr("y", tagY);
    tags.exit().remove();
  }

  /* ============================================================
     renderTree — visualização de árvores (BST/AVL) estilo algs4:
     nós como círculos ligados por arestas. Layout determinístico:
     x = ordem in-order (esquerda sempre à esquerda), y = profundidade.
     Cor conforme o estado do nó; fator de balanceamento acima (AVL).
     ============================================================ */
  renderTree(step) {
    const root = step.tree || null;
    const { w, h } = this.size();
    this.svg.attr("viewBox", `0 0 ${w} ${h}`);

    let g = this.svg.select("g.tree");
    if (g.empty()) {
      g = this.svg.append("g").attr("class", "tree");
      g.append("g").attr("class", "edge-layer");
      g.append("g").attr("class", "node-layer");
      g.append("g").attr("class", "empty-layer");
    }
    const t = this.svg.transition().duration(this.duration ?? 260);

    // Layout: x = posição in-order (0..order-1), y = profundidade.
    const nodes = [], edges = [];
    let order = 0, maxDepth = 0;
    const walk = (nd, depth, parent) => {
      if (!nd) return;
      walk(nd.left, depth + 1, nd);
      nd._x = order++;
      nd._d = depth;
      maxDepth = Math.max(maxDepth, depth);
      nodes.push(nd);
      if (parent) edges.push({ s: parent, c: nd });
      walk(nd.right, depth + 1, nd);
    };
    walk(root, 0, null);

    // Árvore vazia.
    const empty = g.select(".empty-layer").selectAll("text.tree-empty").data(root ? [] : [0]);
    empty
      .enter()
      .append("text")
      .attr("class", "tree-empty")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("fill", COLOR.label)
      .merge(empty)
      .text("árvore vazia — insira um valor")
      .attr("x", w / 2)
      .attr("y", h / 2);
    empty.exit().remove();

    const padX = 42, padTop = 40, padBot = 28;
    const spanX = Math.max(order - 1, 1);
    const spanY = Math.max(maxDepth, 1);
    const R = Math.max(11, Math.min(22, (w - 2 * padX) / (order + 1) / 2.1));
    const xOf = (nd) => (order <= 1 ? w / 2 : padX + (nd._x / spanX) * (w - 2 * padX));
    const yOf = (nd) => padTop + (nd._d / spanY) * (h - padTop - padBot);

    /* ---- arestas ---- */
    const edgeSel = g.select(".edge-layer").selectAll("line.tree-edge").data(edges, (d) => d.c.value);
    edgeSel
      .enter()
      .append("line")
      .attr("class", "tree-edge")
      .attr("stroke", COLOR.label)
      .attr("stroke-width", 1.6)
      .merge(edgeSel)
      .transition(t)
      .attr("x1", (d) => xOf(d.s))
      .attr("y1", (d) => yOf(d.s))
      .attr("x2", (d) => xOf(d.c))
      .attr("y2", (d) => yOf(d.c));
    edgeSel.exit().remove();

    /* ---- nós ---- */
    const STATE = {
      normal: COLOR.bar,
      compared: COLOR.compared,
      active: COLOR.pointer,
      inserted: COLOR.sorted,
      found: COLOR.sorted,
      removed: COLOR.swapped,
      visited: "#6b7280",
    };
    const sel = g.select(".node-layer").selectAll("g.tree-node").data(nodes, (d) => d.value);
    const enter = sel.enter().append("g").attr("class", "tree-node");
    enter.append("circle").attr("class", "tree-circle");
    enter.append("text").attr("class", "tree-val").attr("text-anchor", "middle").attr("dominant-baseline", "central");
    enter.append("text").attr("class", "tree-bf").attr("text-anchor", "middle");
    const all = enter.merge(sel);
    all.transition(t).attr("transform", (d) => `translate(${xOf(d)},${yOf(d)})`);
    all
      .select("circle.tree-circle")
      .attr("r", R)
      .attr("stroke", COLOR.label)
      .attr("stroke-width", 1.6)
      .transition(t)
      .attr("fill", (d) => STATE[d.state] || COLOR.bar);
    all
      .select("text.tree-val")
      .attr("fill", "#fff")
      .style("font-size", `${Math.round(R * 0.82)}px`)
      .text((d) => d.value);
    all
      .select("text.tree-bf")
      .attr("fill", COLOR.label)
      .attr("y", -R - 6)
      .text((d) => (this.mode === "avl" && d.balance != null ? `fb ${d.balance > 0 ? "+" : ""}${d.balance}` : ""));
    sel.exit().remove();
  }

  /* ============================================================
     renderGraph — grafo não-dirigido (BFS/DFS/Dijkstra). Nós em
     posições relativas (x,y ∈ [0,1]); arestas coloridas por estado
     (considerada / árvore / caminho), com peso e rótulo de distância.
     ============================================================ */
  renderGraph(step) {
    const gd = step.graph;
    const { w, h } = this.size();
    this.svg.attr("viewBox", `0 0 ${w} ${h}`);

    let g = this.svg.select("g.graph");
    if (g.empty()) {
      g = this.svg.append("g").attr("class", "graph");
      g.append("g").attr("class", "gedge-layer");
      g.append("g").attr("class", "gweight-layer");
      g.append("g").attr("class", "gnode-layer");
    }

    const nodes = gd?.nodes || [];
    const edges = gd?.edges || [];

    // Grafo vazio.
    const empty = g.selectAll("text.graph-empty").data(nodes.length ? [] : [0]);
    empty
      .enter()
      .append("text")
      .attr("class", "graph-empty tree-empty")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("fill", COLOR.label)
      .merge(empty)
      .text("grafo vazio — carregue um exemplo ou adicione vértices")
      .attr("x", w / 2)
      .attr("y", h / 2);
    empty.exit().remove();

    const t = this.svg.transition().duration(this.duration ?? 260);
    const pad = 44;
    const px = (x) => pad + x * (w - 2 * pad);
    const py = (y) => pad + y * (h - 2 * pad);
    const byId = {};
    nodes.forEach((n) => (byId[n.id] = n));
    const R = Math.max(12, Math.min(20, 620 / (nodes.length + 4)));

    const EDGE = { normal: "#d0d0d6", considered: COLOR.compared, tree: COLOR.sorted, inpath: COLOR.swapped };
    const NODE = {
      normal: COLOR.bar,
      source: COLOR.swapped,
      current: COLOR.swapped,
      frontier: COLOR.compared,
      visited: "#6b7280",
      target: COLOR.swapped,
      inpath: COLOR.swapped,
    };

    /* ---- arestas ---- */
    const eKey = (e) => `${e.u}-${e.v}`;
    const eSel = g.select(".gedge-layer").selectAll("line.g-edge").data(edges, eKey);
    eSel
      .enter()
      .append("line")
      .attr("class", "g-edge")
      .merge(eSel)
      .attr("x1", (e) => px(byId[e.u]?.x ?? 0.5))
      .attr("y1", (e) => py(byId[e.u]?.y ?? 0.5))
      .attr("x2", (e) => px(byId[e.v]?.x ?? 0.5))
      .attr("y2", (e) => py(byId[e.v]?.y ?? 0.5))
      .transition(t)
      .attr("stroke", (e) => EDGE[e.state] || EDGE.normal)
      .attr("stroke-width", (e) => (e.state === "tree" || e.state === "inpath" ? 4 : 2));
    eSel.exit().remove();

    /* ---- rótulos de peso ---- */
    const weighted = edges.filter((e) => e.weight != null);
    const wSel = g.select(".gweight-layer").selectAll("text.g-weight").data(weighted, eKey);
    wSel
      .enter()
      .append("text")
      .attr("class", "g-weight")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .merge(wSel)
      .text((e) => e.weight)
      .attr("x", (e) => (px(byId[e.u]?.x ?? 0.5) + px(byId[e.v]?.x ?? 0.5)) / 2)
      .attr("y", (e) => (py(byId[e.u]?.y ?? 0.5) + py(byId[e.v]?.y ?? 0.5)) / 2);
    wSel.exit().remove();

    /* ---- vértices ---- */
    const nSel = g.select(".gnode-layer").selectAll("g.g-node").data(nodes, (n) => n.id);
    const enter = nSel.enter().append("g").attr("class", "g-node");
    enter.append("circle").attr("class", "g-circle");
    enter.append("text").attr("class", "g-id").attr("text-anchor", "middle").attr("dominant-baseline", "central");
    enter.append("text").attr("class", "g-dist").attr("text-anchor", "middle");
    const all = enter.merge(nSel);
    all.transition(t).attr("transform", (n) => `translate(${px(n.x)},${py(n.y)})`);
    all
      .select("circle.g-circle")
      .attr("r", R)
      .attr("stroke", COLOR.label)
      .attr("stroke-width", 1.6)
      .transition(t)
      .attr("fill", (n) => NODE[n.state] || COLOR.bar);
    all
      .select("text.g-id")
      .attr("fill", "#fff")
      .style("font-size", `${Math.round(R * 0.85)}px`)
      .text((n) => n.id);
    all
      .select("text.g-dist")
      .attr("fill", COLOR.label)
      .attr("y", -R - 7)
      .text((n) => (n.dist != null ? `${n.dist}` : ""));
    nSel.exit().remove();
  }
}

/* ============================================================
   AnimationEngine — controla o player (play/pause/step/seek).
   ============================================================ */
export class AnimationEngine {
  constructor(renderer, delayMs = 600) {
    this.renderer = renderer;
    this.steps = [];
    this.currentIndex = 0;
    this.delay = delayMs;
    this.timerId = null;
    this.onStep = null; // callback(step, index, total)
    this.onStateChange = null; // callback(isPlaying)
  }

  load(steps) {
    this.pause();
    this.steps = steps || [];
    this.currentIndex = 0;
    this.renderer.duration = 220;
    this._emit();
  }

  get total() {
    return this.steps.length;
  }

  play() {
    if (this.timerId || this.steps.length === 0) return;
    if (this.currentIndex >= this.steps.length - 1) this.currentIndex = 0;
    this.renderer.duration = Math.min(this.delay * 0.6, 400);
    this._notifyState(true);
    this.timerId = setInterval(() => {
      if (this.currentIndex >= this.steps.length - 1) {
        this.pause();
        return;
      }
      this.currentIndex++;
      this._emit();
    }, this.delay);
  }

  pause() {
    if (this.timerId) {
      clearInterval(this.timerId);
      this.timerId = null;
    }
    this._notifyState(false);
  }

  toggle() {
    this.timerId ? this.pause() : this.play();
  }

  stepForward() {
    this.pause();
    if (this.currentIndex < this.steps.length - 1) {
      this.currentIndex++;
      this.renderer.duration = 220;
      this._emit();
    }
  }

  stepBackward() {
    this.pause();
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.renderer.duration = 220;
      this._emit();
    }
  }

  seek(index) {
    this.pause();
    this.currentIndex = Math.max(0, Math.min(index, this.steps.length - 1));
    this.renderer.duration = 120;
    this._emit();
  }

  setSpeed(ms) {
    this.delay = ms;
    if (this.timerId) {
      this.pause();
      this.play();
    }
  }

  get isPlaying() {
    return this.timerId !== null;
  }

  _emit() {
    const step = this.steps[this.currentIndex];
    if (step) this.renderer.render(step);
    if (this.onStep) this.onStep(step, this.currentIndex, this.total);
  }

  _notifyState(playing) {
    if (this.onStateChange) this.onStateChange(playing);
  }
}
