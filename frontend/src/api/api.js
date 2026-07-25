// src/api/api.js
// Camada de acesso à API FastAPI. As rotas são segregadas por categoria
// (sorting, linear, trees, graphs) sob o prefixo /api/v1.

const API_ROOT =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") || "http://localhost:8000";
const BASE = `${API_ROOT}/api/v1`;

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body && body.detail) detail = body.detail;
    } catch {
      /* corpo não-JSON: mantém statusText */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const Api = {
  /** Lista os algoritmos disponíveis em uma categoria. */
  listAlgorithms(category) {
    return request(`/${category}/algorithms`);
  },

  /** Executa um algoritmo e devolve { algorithm, steps }. */
run(category, key, payload) {
    return request(`/${category}/${key}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload), // Substituído para aceitar estruturação dinâmica
    });
  },

  /** Metadados pedagógicos: { algorithm, theory, code, quiz }. */
  metadata(category, key) {
    return request(`/${category}/${key}/metadata`);
  },
};
