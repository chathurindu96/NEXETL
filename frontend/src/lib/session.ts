import { writable } from 'svelte/store';
import { getSession, type SessionState } from '$lib/api/auth';

export type BrowserSession = SessionState & { loading: boolean };
export const session = writable<BrowserSession>({ authenticated: false, loading: true });

export async function refreshSession(): Promise<BrowserSession> {
  try { const state = await getSession(); const next = { ...state, loading: false }; session.set(next); return next; }
  catch { const next = { authenticated: false, loading: false }; session.set(next); return next; }
}

export function clearSession(): void { session.set({ authenticated: false, loading: false }); }
