<script lang="ts">
  import '@fontsource/inter/400.css'; import '@fontsource/inter/500.css'; import '@fontsource/inter/600.css'; import '@fontsource/inter/700.css'; import '../app.css';
  import { goto } from '$app/navigation'; import { page } from '$app/state'; import { onMount } from 'svelte';
  import { logout } from '$lib/api/auth'; import { clearSession, refreshSession, session } from '$lib/session'; import Icon from '$lib/components/ui/Icon.svelte';
  import { routeEntity } from '$lib/route-context';
  let { children } = $props(); let collapsed = $state(false); let drawerOpen = $state(false); let signingOut = $state(false);
  const navigation = [{ label: 'Home', href: '/home', icon: 'home' }, { label: 'Pipelines', href: '/pipelines', icon: 'pipelines' }, { label: 'Connectors', href: '/connectors', icon: 'connectors' }, { label: 'Settings', href: '/settings', icon: 'settings' }];
  onMount(() => { const sync=()=>collapsed=localStorage.getItem('nexetl.sidebar.collapsed') === 'true'; sync(); window.addEventListener('nexetl-sidebar-preference',sync); void refreshSession(); return()=>window.removeEventListener('nexetl-sidebar-preference',sync); });
  $effect(() => { if ($session.loading || signingOut) return; const login = page.url.pathname === '/login'; if (!login && !$session.authenticated) void goto(`/login?next=${encodeURIComponent(page.url.pathname + page.url.search)}`); if (login && $session.authenticated) void goto(page.url.searchParams.get('next') || '/home'); });
  function active(href: string) { return href === '/home' ? page.url.pathname === href : page.url.pathname === href || page.url.pathname.startsWith(`${href}/`); }
  function context() { const path = page.url.pathname; if (path === '/home') return ['Home']; if (path === '/settings') return ['Settings']; if (path.endsWith('/design')) return ['Pipelines', $routeEntity ?? 'Pipeline', 'Design']; if (path === '/pipelines/new') return ['Pipelines', 'Create']; if (path.startsWith('/pipelines/')) return ['Pipelines', $routeEntity ?? 'Details']; if (path.startsWith('/pipelines')) return ['Pipelines']; if (path.startsWith('/connectors/') && path !== '/connectors/') return ['Connectors', $routeEntity ?? 'Details']; return ['Connectors']; }
  async function signOut() { signingOut = true; try { await logout(); } finally { clearSession(); await goto('/login'); } }
  function toggleNavigation() { collapsed = !collapsed; localStorage.setItem('nexetl.sidebar.collapsed', String(collapsed)); }
</script>
{#if page.url.pathname === '/login'}{@render children()}{:else if $session.authenticated}
  <div class:sidebar-collapsed={collapsed} class="app-shell">
    {#if drawerOpen}<button class="mobile-backdrop" aria-label="Close navigation" onclick={() => drawerOpen = false}></button>{/if}
    <aside class:drawer-open={drawerOpen} class="sidebar" aria-label="Primary navigation">
      <a class="brand" href="/home" title="NEXETL" onclick={() => drawerOpen = false}><span class="brand-mark">NX</span><span class="brand-copy"><span class="brand-name">NEXETL</span><span class="brand-subtitle">DATA PIPELINE PLATFORM</span></span></a>
      <nav aria-label="Primary navigation"><p class="nav-label">Workspace</p>{#each navigation as item}<a class="nav-link" href={item.href} title={collapsed ? item.label : undefined} aria-current={active(item.href) ? 'page' : undefined} onclick={() => drawerOpen = false}><span class="nav-icon"><Icon name={item.icon}/></span><span class="nav-text">{item.label}</span></a>{/each}</nav>
      <div class="sidebar-footer"><span class="environment-badge">Local development</span><button class="sidebar-toggle" aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'} onclick={toggleNavigation}><Icon name={collapsed ? 'chevron-right' : 'chevron-left'} /></button></div>
    </aside>
    <div class="app-area"><header class="topbar"><button class="mobile-menu" aria-label="Open navigation" onclick={() => drawerOpen = true}><Icon name="menu"/></button><nav class="breadcrumbs" aria-label="Breadcrumb">{#each context() as item, index}{#if index}<span class="breadcrumb-sep">/</span>{/if}<strong>{item}</strong>{/each}</nav><span class="topbar-environment">Local development</span><div class="user-area"><span class="user-avatar"><Icon name="user" size={14}/></span><span>{$session.username}</span><button onclick={signOut}>Sign out</button></div></header><main class:designer-route={page.url.pathname.endsWith('/design')} class="main-content">{@render children()}</main></div>
  </div>
{:else}<main class="session-loading" aria-live="polite">Checking your session…</main>{/if}
