<script lang="ts">
  type Variant = 'primary' | 'secondary' | 'danger';
  let { variant = 'primary', loading = false, disabled = false, type = 'button', onclick, children }: { variant?: Variant; loading?: boolean; disabled?: boolean; type?: 'button' | 'submit'; onclick?: () => void; children?: import('svelte').Snippet } = $props();
</script>
<button class:primary={variant === 'primary'} class:secondary={variant === 'secondary'} class:danger={variant === 'danger'} {type} {onclick} disabled={disabled || loading} aria-busy={loading}>
  {#if loading}<span class="spinner" aria-hidden="true"></span>{/if}{@render children?.()}
</button>
<style>
  button { display:inline-flex; align-items:center; justify-content:center; gap:.45rem; min-height:2.25rem; border:1px solid transparent; border-radius:var(--radius-sm); padding:.42rem .75rem; cursor:pointer; font-size:.78rem; font-weight:650; transition:background-color .15s ease, border-color .15s ease; }
  .primary { background:var(--color-primary); color:var(--color-primary-text); } .primary:hover:not(:disabled) { background:var(--color-primary-hover); }
  .secondary { background:var(--color-surface); border-color:var(--color-border); color:var(--color-text); } .secondary:hover:not(:disabled) { background:var(--color-surface-muted); }
  .danger { background:var(--color-danger); color:white; } button:disabled { cursor:not-allowed; opacity:.62; }
  .spinner { width:1rem; height:1rem; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:spin .7s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } } @media (prefers-reduced-motion: reduce) { .spinner { animation:none; } }
</style>
