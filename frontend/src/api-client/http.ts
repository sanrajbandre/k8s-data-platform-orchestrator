import { useAuthStore } from '../auth/store';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

async function refreshToken(): Promise<void> {
  const state = useAuthStore.getState();
  if (!state.refreshToken) throw new Error('No refresh token');
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: state.refreshToken }),
  });
  if (!res.ok) throw new Error('Refresh failed');
  const data = await res.json();
  useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
}

export async function apiFetch(path: string, init?: RequestInit): Promise<any> {
  const state = useAuthStore.getState();
  const headers = new Headers(init?.headers ?? {});
  headers.set('Content-Type', 'application/json');
  if (state.accessToken) headers.set('Authorization', `Bearer ${state.accessToken}`);

  let res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (res.status === 401 && state.refreshToken) {
    await refreshToken();
    const refreshed = useAuthStore.getState();
    headers.set('Authorization', `Bearer ${refreshed.accessToken}`);
    res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}
