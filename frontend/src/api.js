const BASE = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${body}`);
  }
  return response.json();
}

export function getHealth() {
  return request("/health");
}

export function askQuestion(question) {
  return request("/chat", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export function ingestDocument(documentName, text) {
  return request("/docs/ingest", {
    method: "POST",
    body: JSON.stringify({ document_name: documentName, text }),
  });
}
