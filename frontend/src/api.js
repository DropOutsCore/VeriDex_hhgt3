/**
 * VERIDEX Frontend API Client
 * Connects directly to FastAPI backend endpoints.
 * Never fakes progress or mock data.
 */

const API_BASE = '/api';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Health check failed:', err);
    return { status: 'error', error: err.message };
  }
}

export async function runPipeline(file, autoAnchor = true) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/pipeline?auto_anchor=${autoAnchor}`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'Pipeline request failed' }));
    throw new Error(errData.detail || `Pipeline HTTP error ${res.status}`);
  }

  return await res.json();
}

export async function simulateTampering(packageData, fieldToModify = 'matched_url', newValue = 'https://tampered-fake-site.com/hacked.jpg') {
  const url = `${API_BASE}/tamper-test?field_to_modify=${encodeURIComponent(fieldToModify)}&new_value=${encodeURIComponent(newValue)}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(packageData),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'Tamper simulation failed' }));
    throw new Error(errData.detail || `Tamper HTTP error ${res.status}`);
  }

  return await res.json();
}

export async function verifyChainIntegrity(packageData) {
  const res = await fetch(`${API_BASE}/verify-chain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(packageData),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'Integrity check failed' }));
    throw new Error(errData.detail || `Integrity check HTTP error ${res.status}`);
  }

  return await res.json();
}
