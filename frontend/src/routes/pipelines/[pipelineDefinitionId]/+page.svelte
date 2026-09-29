<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { getPipelineDefinition, pipelineErrorMessage, type NexetlError } from '$lib/api/pipelines';
  import { clearSession } from '$lib/session';
  import Alert from '$lib/components/ui/Alert.svelte'; import LoadingState from '$lib/components/ui/LoadingState.svelte'; import PageHeader from '$lib/components/ui/PageHeader.svelte';
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

<div class="breadcrumb">Pipelines / {id ? id.slice(0, 8) : 'Inspect'}</div>
<PageHeader title="Pipeline Definition" description="Inspect the registered identity for this Pipeline Definition." />
{#if loading}<LoadingState />{:else if message}<Alert variant={message.includes('not found') ? 'warning' : 'error'}>{message}</Alert>{:else}<section class="details" aria-label="Pipeline Definition details"><span>Identifier</span><code>{id}</code></section>{/if}
<style>.breadcrumb{margin-bottom:var(--space-3);color:var(--text-muted);font-size:.8125rem;font-weight:500}.details{max-width:46rem;border:1px solid var(--border-default);border-radius:var(--radius-sm);background:var(--bg-surface);padding:var(--space-5)}.details span{display:block;color:var(--text-muted);font-size:.75rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase}.details code{display:block;margin-top:var(--space-2);overflow-wrap:anywhere;color:var(--text-primary);font-family:var(--font-mono);font-size:.9rem;user-select:all}</style>
