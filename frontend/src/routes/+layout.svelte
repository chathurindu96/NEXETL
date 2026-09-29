<script lang="ts">
  import '@fontsource/inter/400.css'; import '@fontsource/inter/500.css'; import '@fontsource/inter/600.css'; import '@fontsource/inter/700.css'; import '../app.css';
  import { goto } from '$app/navigation'; import { page } from '$app/state'; import { onMount } from 'svelte';
  import { logout } from '$lib/api/auth'; import { clearSession, refreshSession, session } from '$lib/session';
  let { children } = $props(); let collapsed = $state(false); let drawerOpen = $state(false); let signingOut = $state(false);
  const navigation = [{ label: 'Home', href: '/home' }, { label: 'Pipelines', href: '/pipelines' }, { label: 'Connectors', href: '/connectors' }];
  onMount(() => { collapsed = localStorage.getItem('nexetl.sidebar.collapsed') === 'true'; void refreshSession(); });
  $effect(() => { if ($session.loading || signingOut) return; const login = page.url.pathname === '/login'; if (!login && !$session.authenticated) void goto(`/login?next=${encodeURIComponent(page.url.pathname + page.url.search)}`); if (login && $session.authenticated) void goto(page.url.searchParams.get('next') || '/home'); });
  function active(href: string) { return href === '/home' ? page.url.pathname === href : page.url.pathname === href || page.url.pathname.startsWith(`${href}/`); }
  function context() { const path = page.url.pathname; if (path === '/home') return 'Home'; if (path === '/pipelines/new') return 'Pipelines / New'; if (path.startsWith('/pipelines/')) return 'Pipelines / Details'; if (path.startsWith('/pipelines')) return 'Pipelines'; if (path.startsWith('/connectors/') && path !== '/connectors/') return 'Connectors / Details'; return 'Connectors'; }
  async function signOut() { signingOut = true; try { await logout(); } finally { clearSession(); await goto('/login'); } }
  function toggleNavigation() { collapsed = !collapsed; localStorage.setItem('nexetl.sidebar.collapsed', String(collapsed)); }
</script>
{#if page.url.pathname === '/login'}{@render children()}{:else if $session.authenticated}
  <div class:sidebar-collapsed={collapsed} class="app-shell">
    {#if drawerOpen}<button class="mobile-backdrop" aria-label="Close navigation" onclick={() => drawerOpen = false}></button>{/if}
    <aside class:drawer-open={drawerOpen} class="sidebar" aria-label="Primary navigation">
      <a class="brand" href="/home" title="NEXETL" onclick={() => drawerOpen = false}><span class="brand-mark">NX</span><span class="brand-text">NEXETL</span></a>
      <nav aria-label="Primary navigation"><p class="nav-label">Workspace</p>{#each navigation as item}<a class="nav-link" href={item.href} aria-current={active(item.href) ? 'page' : undefined} onclick={() => drawerOpen = false}><span class="nav-icon" aria-hidden="true">{item.label.slice(0, 1)}</span><span class="nav-text">{item.label}</span></a>{/each}</nav>
      <div class="sidebar-footer"><span class="environment-badge">Local Development</span><button class="sidebar-toggle" aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'} onclick={toggleNavigation}>‹</button></div>
    </aside>
    <div class="app-area"><header class="topbar"><button class="mobile-menu" aria-label="Open navigation" onclick={() => drawerOpen = true}>☰</button><span class="topbar-context">{context()}</span><span class="topbar-environment">Local Development</span><div class="user-area"><span>{$session.username}</span><button onclick={signOut}>Sign out</button></div></header><main class="main-content">{@render children()}</main></div>
  </div>
{:else}<main class="session-loading" aria-live="polite">Checking your session…</main>{/if}
