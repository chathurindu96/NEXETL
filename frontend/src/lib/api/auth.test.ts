import { afterEach, describe, expect, it, vi } from 'vitest';

import { getSession, login, logout } from './auth';

describe('session authentication client', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    document.cookie = 'csrftoken=; Max-Age=0; path=/';
  });

  it('reads only browser-safe session state', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ authenticated: true, username: 'admin' })));
    vi.stubGlobal('fetch', fetch);

    await expect(getSession()).resolves.toEqual({ authenticated: true, username: 'admin' });
    expect(fetch).toHaveBeenCalledWith('/api/auth/session/', { credentials: 'include' });
  });

  it('bootstraps CSRF before sending the real login request', async () => {
    document.cookie = 'csrftoken=test-csrf; path=/';
    const fetch = vi.fn()
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', fetch);

    await login('admin', '123');

    expect(fetch).toHaveBeenNthCalledWith(1, '/api/security/csrf/', { credentials: 'include' });
    expect(fetch).toHaveBeenNthCalledWith(2, '/api/auth/login/', expect.objectContaining({
      method: 'POST', credentials: 'include', headers: expect.objectContaining({ 'X-CSRFToken': 'test-csrf' }),
    }));
  });

  it('preserves a safe invalid-credential response and signs out through the API', async () => {
    document.cookie = 'csrftoken=test-csrf; path=/';
    const invalid = new Response(JSON.stringify({ code: 'NEXETL_AUTHENTICATION_FAILED' }), { status: 401 });
    const fetch = vi.fn()
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(invalid)
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', fetch);

    await expect(login('admin', 'wrong')).rejects.toMatchObject({ code: 'NEXETL_AUTHENTICATION_FAILED' });
    await expect(logout()).resolves.toBeUndefined();
    expect(fetch).toHaveBeenLastCalledWith('/api/auth/logout/', expect.objectContaining({ method: 'POST', credentials: 'include' }));
  });
});
