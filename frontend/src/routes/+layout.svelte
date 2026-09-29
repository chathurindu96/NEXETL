<script lang="ts">
  import '@fontsource/inter/400.css'; import '@fontsource/inter/500.css'; import '@fontsource/inter/600.css'; import '@fontsource/inter/700.css'; import '../app.css';
  import { goto } from '$app/navigation'; import { page } from '$app/state'; import { onMount } from 'svelte'; import { logout } from '$lib/api/auth'; import { clearSession, refreshSession, session } from '$lib/session';
  let { children } = $props(); let collapsed = $state(false); let drawerOpen = $state(false); let signingOut = $state(false);
  onMount(() => { collapsed = localStorage.getItem('nexetl.sidebar.collapsed') === 'true'; void refreshSession(); });
  $effect(() => { if ($session.loading || signingOut) return; const loginPage = page.url.pathname === '/login'; if (!loginPage && !$session.authenticated) void goto(`/login?next=${encodeURIComponent(page.url.pathname)}`); if (loginPage && $session.authenticated) void goto(page.url.searchParams.get('next') || '/pipelines/new'); });
  async function signOut() { signingOut = true; await logout(); clearSession(); await goto('/login'); }
  function toggleNavigation() { collapsed = !collapsed; localStorage.setItem('nexetl.sidebar.collapsed', String(collapsed)); }
  function closeDrawer() { drawerOpen = false; }
</script>
{#if page.url.pathname === '/login'}{@render children()}{:else if $session.authenticated}
  <div class:sidebar-collapsed={collapsed} class="app-shell">
    {#if drawerOpen}<button class="mobile-backdrop" aria-label="Close navigation" onclick={closeDrawer}></button>{/if}
    <aside class:drawer-open={drawerOpen} class="sidebar" aria-label="Primary navigation">
      <a class="brand" href="/pipelines/new" title="NEXETL" onclick={closeDrawer}><span class="brand-mark">NX</span><span class="brand-text">NEXETL</span></a>
      <nav aria-label="Primary navigation"><p class="nav-label">Pipelines</p><a class="nav-link" href="/pipelines/new" aria-current={page.url.pathname === '/pipelines/new' ? 'page' : undefined} title="New Pipeline" onclick={closeDrawer}><svg class="nav-icon" aria-hidden="true" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg><span class="nav-text">New Pipeline</span></a></nav>
      <div class="sidebar-footer"><span class="environment-badge">Local Development</span><button class="sidebar-toggle" aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'} title={collapsed ? 'Expand navigation' : 'Collapse navigation'} onclick={toggleNavigation}><svg aria-hidden="true" viewBox="0 0 24 24"><path d={collapsed ? 'm9 18 6-6-6-6' : 'm15 18-6-6 6-6'}/></svg></button></div>
    </aside>
    <div class="app-area"><header class="topbar"><button class="mobile-menu" aria-label="Open navigation" onclick={() => drawerOpen = true}><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button><span class="topbar-context"><strong>Pipelines</strong> / {page.url.pathname === '/pipelines/new' ? 'Create' : 'Inspect'}</span><span class="topbar-environment">Local Development</span><div class="user-area"><span>{$session.username}</span><span class="role">Super Admin</span><button onclick={signOut}>Sign out</button></div></header><main class="main-content">{@render children()}</main></div>
  </div>
{:else}<main class="session-loading" aria-live="polite">Checking your session…</main>{/if}
