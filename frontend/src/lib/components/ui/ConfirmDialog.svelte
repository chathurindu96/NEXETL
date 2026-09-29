<script lang="ts">
  import Button from './Button.svelte';
  let { open, title, message, pending = false, onconfirm, oncancel }: { open: boolean; title: string; message: string; pending?: boolean; onconfirm: () => void; oncancel: () => void } = $props();
</script>
{#if open}
  <div class="backdrop" role="presentation"><dialog open class="dialog" aria-labelledby="dialog-title"><h2 id="dialog-title">{title}</h2><p>{message}</p><div><Button variant="secondary" onclick={oncancel}>Cancel</Button><Button variant="danger" loading={pending} onclick={onconfirm}>Archive</Button></div></dialog></div>
{/if}
<style>.backdrop{position:fixed;inset:0;z-index:40;display:grid;place-items:center;background:rgb(16 24 40 / 38%);padding:var(--space-4)}.dialog{width:min(100%,28rem);border:1px solid var(--border-default);border-radius:var(--radius-md);background:#fff;padding:var(--space-6);box-shadow:0 12px 28px rgb(16 24 40 / 18%)}h2{margin:0;font-size:1.125rem}p{margin:var(--space-3) 0 var(--space-5);color:var(--text-secondary)}.dialog div{display:flex;justify-content:flex-end;gap:var(--space-2)}</style>
