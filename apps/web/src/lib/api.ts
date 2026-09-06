const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(API_BASE + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error("API " + res.status + ": " + text);
  }
  return res.json();
}

export const api = {
  projects: {
    list: () => apiFetch("/api/v1/projects/"),
    get: (id: string) => apiFetch("/api/v1/projects/" + id),
    create: (data: { title: string }) =>
      apiFetch("/api/v1/projects/", { method: "POST", body: JSON.stringify(data) }),
    delete: (id: string) => apiFetch("/api/v1/projects/" + id, { method: "DELETE" }),
  },
  generation: {
    fromScratch: (data: any) =>
      apiFetch("/api/v1/generation/from-scratch", { method: "POST", body: JSON.stringify(data) }),
    fromContent: (data: any) =>
      apiFetch("/api/v1/generation/from-content", { method: "POST", body: JSON.stringify(data) }),
    fromData: (data: any) =>
      apiFetch("/api/v1/generation/from-data", { method: "POST", body: JSON.stringify(data) }),
    convert: (data: any) =>
      apiFetch("/api/v1/generation/convert", { method: "POST", body: JSON.stringify(data) }),
  },
  export: {
    formats: () => apiFetch("/api/v1/export/formats"),
    publishers: () => apiFetch("/api/v1/export/publishers"),
    publisher: (key: string) => apiFetch("/api/v1/export/publishers/" + key),
    generate: (data: any) =>
      apiFetch("/api/v1/export/generate", { method: "POST", body: JSON.stringify(data) }),
    preview: (data: any) =>
      apiFetch("/api/v1/export/preview", { method: "POST", body: JSON.stringify(data) }),
  },
  knowledge: {
    stats: () => apiFetch("/api/v1/knowledge/stats"),
    publishers: () => apiFetch("/api/v1/knowledge/publishers"),
    publisher: (key: string) => apiFetch("/api/v1/knowledge/publishers/" + key),
    citations: () => apiFetch("/api/v1/knowledge/citations"),
    citation: (key: string) => apiFetch("/api/v1/knowledge/citations/" + key),
    journals: (publisher?: string) =>
      apiFetch("/api/v1/knowledge/journals" + (publisher ? "?publisher_key=" + publisher : "")),
    journal: (key: string) => apiFetch("/api/v1/knowledge/journals/" + key),
    search: (data: any) =>
      apiFetch("/api/v1/knowledge/search", { method: "POST", body: JSON.stringify(data) }),
  },
  analysis: {
    upload: (data: any) =>
      apiFetch("/api/v1/analysis/upload", { method: "POST", body: JSON.stringify(data) }),
    analyze: (data: any) =>
      apiFetch("/api/v1/analysis/analyze", { method: "POST", body: JSON.stringify(data) }),
    chart: (data: any) =>
      apiFetch("/api/v1/analysis/chart", { method: "POST", body: JSON.stringify(data) }),
  },
  cdm: {
    get: (versionId: string) => apiFetch("/api/v1/cdm/" + versionId),
    update: (versionId: string, data: any) =>
      apiFetch("/api/v1/cdm/" + versionId, { method: "PUT", body: JSON.stringify(data) }),
  },
  health: () => apiFetch("/api/v1/health"),
};
