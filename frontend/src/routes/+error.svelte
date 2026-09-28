<script lang="ts">
  import { page } from '$app/state';
  import Button from '$lib/components/ui/Button.svelte';
</script>

<svelte:head><title>Page not found | NEXETL</title></svelte:head>

<section class="error-page"><p class="status">{page.status === 404 ? '404' : 'NEXETL'}</p><h1>{page.status === 404 ? 'Page not found' : 'Something went wrong'}</h1><p>The requested page is not available.</p><a href="/pipelines/new"><Button>Register a Pipeline Definition</Button></a></section>
<style>.error-page{max-width:36rem;padding:var(--space-8) 0}.status{margin:0;color:var(--color-primary);font-weight:750}.error-page h1{margin:var(--space-2) 0;font-size:2rem;letter-spacing:-.03em}.error-page p:not(.status){margin:0 0 var(--space-5);color:var(--color-text-muted)}</style>
