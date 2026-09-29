<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { getPipelineDefinition, pipelineErrorMessage, type NexetlError } from '$lib/api/pipelines';
  import { clearSession } from '$lib/session';
  import Alert from '$lib/components/ui/Alert.svelte'; import Card from '$lib/components/ui/Card.svelte'; import LoadingState from '$lib/components/ui/LoadingState.svelte'; import PageHeader from '$lib/components/ui/PageHeader.svelte';
  let id = $state('');
  let message = $state('');
  let loading = $state(true);
  $effect(() => { void load(page.params.pipelineDefinitionId ?? ''); });
  async function load(value: string) {
    loading = true; message = '';
    try {
      if (!value) throw new Error('A Pipeline Definition identifier is required.');
      id = await getPipelineDefinition(value);
    }
    catch (error) {
      const failure = error as NexetlError;
      if (failure.code === 'NEXETL_AUTHENTICATION_REQUIRED') {
        clearSession();
        await goto(`/login?next=${encodeURIComponent(page.url.pathname)}`);
        return;
      }
      message = pipelineErrorMessage(failure);
    }
    finally { loading = false; }
  }
</script>

<PageHeader title="Pipeline Definition" description="Inspect the registered identity for this Pipeline Definition." />
{#if loading}<LoadingState />{:else if message}<Alert variant={message.includes('not found') ? 'warning' : 'error'}>{message}</Alert>{:else}<Card title="Pipeline Definition details" description="The approved Increment 1 representation contains one immutable identifier."><dl><dt>Pipeline Definition ID</dt><dd><code>{id}</code></dd></dl></Card>{/if}
<style>dl{margin:0}dt{color:var(--color-text-muted);font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em}dd{margin:var(--space-2) 0 0}code{display:block;overflow-wrap:anywhere;border-radius:var(--radius-sm);background:var(--color-surface-muted);padding:var(--space-3);font-family:var(--font-mono);font-size:.9rem}</style>
