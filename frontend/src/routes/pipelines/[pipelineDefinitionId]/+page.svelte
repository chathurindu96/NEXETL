<script lang="ts">
  import { page } from '$app/state';
  import { getPipelineDefinition, pipelineErrorMessage, type NexetlError } from '$lib/api/pipelines';
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
    catch (error) { message = pipelineErrorMessage(error as NexetlError); }
    finally { loading = false; }
  }
</script>

<h1>Pipeline Definition</h1>
{#if loading}<p>Loading…</p>{:else if message}<p role="alert">{message}</p>{:else}<p>Pipeline Definition ID</p><code>{id}</code>{/if}
