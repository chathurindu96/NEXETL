<script lang="ts">
  let { state }: { state: 'DRAFT' | 'ARCHIVED' | string } = $props();
</script>
<span class:archived={state === 'ARCHIVED'} class="badge">{state === 'DRAFT' ? 'Draft' : state === 'ARCHIVED' ? 'Archived' : state}</span>
<style>.badge{display:inline-flex;border:1px solid #b9d7c7;border-radius:999px;background:#f0f8f3;color:#17623e;padding:.13rem .48rem;font-size:.72rem;font-weight:600}.archived{border-color:var(--border-default);background:var(--bg-surface-subtle);color:var(--text-muted)}</style>
