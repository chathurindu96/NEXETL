<script lang="ts">
  import Icon from '$lib/components/ui/Icon.svelte';
  let { onZoomIn, onZoomOut, onFit, zoom }: { onZoomIn: () => void; onZoomOut: () => void; onFit: () => void; zoom: number } = $props();
</script>
<div class="controls" aria-label="Canvas controls">
  <button aria-label="Zoom out" title="Zoom out" onclick={onZoomOut}><Icon name="zoom-out" size={16}/></button>
  <span aria-live="polite">{Math.round(zoom * 100)}%</span>
  <button aria-label="Zoom in" title="Zoom in" onclick={onZoomIn}><Icon name="zoom-in" size={16}/></button>
  <i></i>
  <button aria-label="Fit canvas" title="Fit canvas" onclick={onFit}><Icon name="fit" size={16}/></button>
</div>
<style>.controls{position:absolute;left:1rem;bottom:1rem;z-index:6;display:flex;align-items:center;border:1px solid var(--border-default);border-radius:var(--radius-md);background:rgb(255 255 255 / 94%);box-shadow:var(--shadow-md);overflow:hidden}.controls button{display:grid;width:2rem;height:2rem;place-items:center;border:0;background:transparent;color:var(--text-secondary);cursor:pointer}.controls button:hover{background:var(--bg-subtle);color:var(--accent)}.controls span{min-width:2.8rem;color:var(--text-muted);font-size:.64rem;text-align:center}.controls i{width:1px;height:1.25rem;background:var(--border-default)}</style>
