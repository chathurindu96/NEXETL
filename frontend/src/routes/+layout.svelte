<script lang="ts">
  import '../app.css'; import { goto } from '$app/navigation'; import { page } from '$app/state'; import { onMount } from 'svelte'; import { logout } from '$lib/api/auth'; import { clearSession, refreshSession, session } from '$lib/session';
  let { children } = $props();
  onMount(() => { void refreshSession(); });
  $effect(() => { if ($session.loading) return; const loginPage = page.url.pathname === '/login'; if (!loginPage && !$session.authenticated) void goto(`/login?next=${encodeURIComponent(page.url.pathname)}`); if (loginPage && $session.authenticated) void goto(page.url.searchParams.get('next') || '/pipelines/new'); });
  async function signOut() { await logout(); clearSession(); await goto('/login'); }
</script>
{#if page.url.pathname === '/login'}{@render children()}{:else if $session.authenticated}<div class="app-shell"><aside class="sidebar" aria-label="Primary navigation"><a class="brand" href="/pipelines/new"><span class="brand-mark">NX</span><span>NEXETL</span></a><nav><p class="nav-label">Pipelines</p><a class="nav-link" href="/pipelines/new">New Pipeline</a></nav><span class="environment-badge sidebar-badge">Local Development</span></aside><div class="app-area"><header class="topbar"><span class="topbar-context">Pipelines</span><div class="user-area"><span>{$session.username}</span><span class="role">Super Admin</span><button onclick={signOut}>Sign out</button></div></header><main class="main-content">{@render children()}</main></div></div>{:else}<main class="session-loading" aria-live="polite">Checking your session…</main>{/if}
