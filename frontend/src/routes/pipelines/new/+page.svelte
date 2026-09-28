<script lang="ts">
  import { goto } from '$app/navigation';
  import { bootstrapCsrf, pipelineErrorMessage, registerPipelineDefinition, type NexetlError } from '$lib/api/pipelines';
  let pending = $state(false);
  let message = $state('');
  async function register() {
    pending = true; message = '';
    try { await bootstrapCsrf(); await goto(`/pipelines/${await registerPipelineDefinition()}`); }
    catch (error) { message = pipelineErrorMessage(error as NexetlError); }
    finally { pending = false; }
  }
</script>

<h1>Register Pipeline Definition</h1>
<p>Register an identity-only Pipeline Definition.</p>
<button onclick={register} disabled={pending}>{pending ? 'Creating…' : 'Create Pipeline Definition'}</button>
{#if message}<p role="alert">{message}</p>{/if}
