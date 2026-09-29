<script lang="ts">
  import { goto } from '$app/navigation';
  import { bootstrapCsrf, pipelineErrorMessage, registerPipelineDefinition, type NexetlError } from '$lib/api/pipelines';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Button from '$lib/components/ui/Button.svelte';
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

<div class="breadcrumb">Pipelines / Create</div>
<PageHeader title="Create Pipeline Definition" description="Create an identity for a new Pipeline Definition." />
<section class="action-section" aria-labelledby="pipeline-definition-action"><div><h2 id="pipeline-definition-action">Pipeline definition</h2><p>NEXETL generates an immutable identifier automatically.</p></div><Button onclick={register} loading={pending}>Create Pipeline Definition</Button></section>
{#if message}<div class="message"><Alert variant={message.includes('authorized') ? 'warning' : 'error'}>{message} An authenticated session is required for protected operations.</Alert></div>{/if}
<style>.breadcrumb{margin-bottom:var(--space-3);color:var(--text-muted);font-size:.8125rem;font-weight:500}.action-section{display:flex;align-items:center;justify-content:space-between;gap:var(--space-5);max-width:46rem;border-top:1px solid var(--border-default);border-bottom:1px solid var(--border-default);padding:var(--space-5) 0}.action-section h2{margin:0;font-size:1.125rem;font-weight:600}.action-section p{margin:var(--space-1) 0 0;color:var(--text-secondary);font-size:.875rem}.message{margin-top:var(--space-4)}@media(max-width:600px){.action-section{align-items:flex-start;flex-direction:column}}</style>
