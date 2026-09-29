import { bootstrapCsrf, type NexetlError } from './pipelines';

export type SessionState = { authenticated: boolean; username?: string };

async function error(response: Response): Promise<NexetlError> { return response.json().catch(() => ({})); }

export async function getSession(): Promise<SessionState> {
  const response = await fetch('/api/auth/session/', { credentials: 'include' });
  if (!response.ok) throw await error(response);
  return response.json();
}

export async function login(username: string, password: string): Promise<void> {
  await bootstrapCsrf();
  const response = await fetch('/api/auth/login/', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body: JSON.stringify({ username, password }) });
  if (!response.ok) throw await error(response);
}

export async function logout(): Promise<void> {
  await bootstrapCsrf();
  const response = await fetch('/api/auth/logout/', { method: 'POST', credentials: 'include', headers: { 'X-CSRFToken': csrfToken() } });
  if (!response.ok) throw await error(response);
}

function csrfToken(): string { return document.cookie.split('; ').find((part) => part.startsWith('csrftoken='))?.split('=')[1] ?? ''; }
