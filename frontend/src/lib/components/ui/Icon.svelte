<script lang="ts">
  let { name, size = 18 }: { name: string; size?: number } = $props();
</script>

<svg class="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  {#if name === 'home'}<path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10M9 20v-6h6v6"/>
  {:else if name === 'pipelines'}<circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M7 6h10M6.5 7.5l4.3 8.7M17.5 7.5l-4.3 8.7"/>
  {:else if name === 'connectors'}<path d="M8 3v5M16 3v5M6 8h12v3a6 6 0 0 1-12 0V8ZM12 17v4"/>
  {:else if name === 'settings'}<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.6v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/>
  {:else if name === 'database'}<ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>
  {:else if name === 'transform'}<path d="M4 5h11M4 12h16M9 19h11"/><path d="m12 2 3 3-3 3M12 16l-3 3 3 3"/>
  {:else if name === 'target'}<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M22 12h-3M12 22v-3M2 12h3"/>
  {:else if name === 'save'}<path d="M5 3h12l2 2v16H5z"/><path d="M8 3v6h8V3M8 21v-7h8v7"/>
  {:else if name === 'check'}<path d="m5 12 4 4L19 6"/>
  {:else if name === 'archive'}<path d="M4 7h16v13H4zM3 3h18v4H3zM9 11h6"/>
  {:else if name === 'edit'}<path d="m4 20 4.5-1 10-10-3.5-3.5-10 10L4 20ZM13.5 7l3.5 3.5"/>
  {:else if name === 'search'}<circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/>
  {:else if name === 'filter'}<path d="M3 5h18M6 12h12M10 19h4"/>
  {:else if name === 'chevron-left'}<path d="m15 18-6-6 6-6"/>
  {:else if name === 'chevron-right'}<path d="m9 18 6-6-6-6"/>
  {:else if name === 'plus'}<path d="M12 5v14M5 12h14"/>
  {:else if name === 'trash'}<path d="M4 7h16M9 7V4h6v3M6 7l1 14h10l1-14M10 11v6M14 11v6"/>
  {:else if name === 'fit'}<path d="M8 3H3v5M16 3h5v5M8 21H3v-5M16 21h5v-5"/>
  {:else if name === 'zoom-in'}<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6M10 7v6M7 10h6"/>
  {:else if name === 'zoom-out'}<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6M7 10h6"/>
  {:else if name === 'arrow-left'}<path d="M19 12H5m6-6-6 6 6 6"/>
  {:else if name === 'menu'}<path d="M4 6h16M4 12h16M4 18h16"/>
  {:else if name === 'user'}<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>
  {:else if name === 'more'}<circle cx="5" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1" fill="currentColor" stroke="none"/>
  {:else}<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>{/if}
</svg>

<style>.icon{display:block;flex:none}</style>
