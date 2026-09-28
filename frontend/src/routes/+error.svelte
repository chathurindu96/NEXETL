<script lang="ts">
  import { page } from '$app/state';
</script>

<svelte:head><title>Page not found | NEXETL</title></svelte:head>

<h1>{page.status === 404 ? 'Page not found' : 'Something went wrong'}</h1>
<p>The requested page is not available.</p>
<a href="/pipelines/new">Register a Pipeline Definition</a>
