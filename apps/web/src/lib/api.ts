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
  if (res.status === 204 || res.headers.get("content-length") === "0") {
    return null;
  }
  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return res.text();
  }
  return res.json();
}

async function apiUpload(path: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(API_BASE + path, { method: "POST", body: form });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error("API " + res.status + ": " + text);
  }
  return res.json();
}

function sseStream(
  path: string,
  body: any,
  onEvent: (event: any) => void
): () => void {
  const controller = new AbortController();

  fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error("API " + res.status + ": " + text);
      }
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              onEvent(JSON.parse(line.slice(6)));
            } catch { /* skip malformed */ }
          }
        }
      }
      if (buffer.startsWith("data: ")) {
        try {
          onEvent(JSON.parse(buffer.slice(6)));
        } catch { /* skip malformed */ }
      }
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onEvent({ type: "error", message: err.message });
      }
    });

  return () => controller.abort();
}

export const api = {
  projects: {
    list: () => apiFetch("/api/v1/projects"),
    get: (id: string) => apiFetch("/api/v1/projects/" + id),
    create: (data: { title: string; description?: string }) =>
      apiFetch("/api/v1/projects", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: any) =>
      apiFetch("/api/v1/projects/" + id, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: string) => apiFetch("/api/v1/projects/" + id, { method: "DELETE" }),
    versions: (id: string) => apiFetch("/api/v1/projects/" + id + "/versions"),
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
    stream: (data: any, onEvent: (event: any) => void) =>
      sseStream("/api/v1/generation/generate/stream", data, onEvent),
    dashboard: () => apiFetch("/api/v1/generation/dashboard"),
  },
  upload: {
    document: (file: File) => apiUpload("/api/v1/generation/upload", file),
  },
  nlp: {
    analyze: (text: string) =>
      apiFetch("/api/v1/generation/analyze-text", {
        method: "POST",
        body: JSON.stringify(text),
      }),
  },
  search: {
    files: (q: string) =>
      apiFetch("/api/v1/generation/search?q=" + encodeURIComponent(q)),
  },
  export: {
    formats: () => apiFetch("/api/v1/export/formats"),
    publishers: () => apiFetch("/api/v1/export/publishers"),
    publisher: (key: string) => apiFetch("/api/v1/export/publishers/" + key),
    generate: (data: any) =>
      apiFetch("/api/v1/export/generate", { method: "POST", body: JSON.stringify(data) }),
    download: (data: any) => {
      const base = API_BASE + "/api/v1/export/download";
      return fetch(base, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }).then((res) => {
        if (!res.ok) throw new Error("Export failed");
        return res.blob();
      });
    },
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
