<script lang="ts">
  import { goto } from '$app/navigation';
  import { bootstrapCsrf, pipelineErrorMessage, registerPipelineDefinition, type NexetlError } from '$lib/api/pipelines';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import PageHeader from '$lib/components/ui/PageHeader.svelte';
  import { clearSession } from '$lib/session';
  let pending = $state(false);
  let message = $state('');
  async function register() {
    pending = true; message = '';
    try { await bootstrapCsrf(); await goto(`/pipelines/${await registerPipelineDefinition()}`); }
    catch (error) { const failure = error as NexetlError; if (failure.code === 'NEXETL_AUTHENTICATION_REQUIRED') { clearSession(); await goto('/login?next=/pipelines/new'); return; } message = pipelineErrorMessage(failure); }
    finally { pending = false; }
  }
</script>

<PageHeader title="Create Pipeline Definition" description="Create the identity for a new Pipeline Definition." />
<Card title="Create a new Pipeline Definition" description="NEXETL will generate the immutable identifier. No additional fields are required yet.">
  <Button onclick={register} loading={pending}>Create Pipeline Definition</Button>
</Card>
{#if message}<div class="message"><Alert variant={message.includes('authorized') ? 'warning' : 'error'}>{message} An authenticated session is required for protected operations.</Alert></div>{/if}
<style>.message{margin-top:var(--space-4)}</style>
