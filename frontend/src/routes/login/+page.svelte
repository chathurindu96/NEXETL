<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { login } from '$lib/api/auth';
  import { refreshSession } from '$lib/session';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  let username = $state(''); let password = $state(''); let pending = $state(false); let message = $state('');
  async function submit() {
    pending = true; message = '';
    try { await login(username, password); await refreshSession(); await goto(page.url.searchParams.get('next') || '/pipelines/new'); }
    catch (error) { message = (error as { code?: string }).code === 'NEXETL_AUTHENTICATION_FAILED' ? 'Invalid username or password.' : 'The service could not complete sign in. Please try again.'; }
    finally { pending = false; }
  }
</script>
<svelte:head><title>Sign in | NEXETL</title></svelte:head>
<main class="auth-shell"><section class="auth-card" aria-labelledby="login-title"><div class="auth-brand"><span class="brand-mark">NX</span><span>NEXETL</span></div><h1 id="login-title">Welcome to NEXETL</h1><p>Sign in to your workspace.</p>{#if message}<Alert variant="error">{message}</Alert>{/if}<form onsubmit={(event) => { event.preventDefault(); void submit(); }}><label>Username<input bind:value={username} autocomplete="username" required /></label><label>Password<input bind:value={password} type="password" autocomplete="current-password" required /></label><Button type="submit" loading={pending} disabled={!username || !password}>Sign in</Button></form><span class="local">Local Development</span></section></main>
<style>.auth-shell{display:grid;min-height:100vh;place-items:center;padding:var(--space-5);background:linear-gradient(145deg,#f8fbff,#edf2fa)}.auth-card{width:min(100%,25rem);border:1px solid var(--color-border);border-radius:var(--radius-md);background:var(--color-surface);padding:var(--space-8);box-shadow:0 18px 45px rgb(16 24 40 / 10%)}.auth-brand{display:flex;align-items:center;gap:.6rem;font-weight:800;letter-spacing:.05em}.brand-mark{display:grid;width:2rem;height:2rem;place-items:center;border-radius:var(--radius-sm);background:var(--color-primary);color:white;font-size:.72rem}h1{margin:var(--space-6) 0 var(--space-1);font-size:1.45rem}p{margin:0 0 var(--space-5);color:var(--color-text-muted)}form{display:grid;gap:var(--space-4);margin-top:var(--space-5)}label{display:grid;gap:var(--space-2);font-size:.875rem;font-weight:650}input{width:100%;border:1px solid var(--color-border);border-radius:var(--radius-sm);padding:.65rem .75rem;background:white;color:var(--color-text)}.local{display:block;margin-top:var(--space-5);color:var(--color-text-muted);font-size:.8rem;text-align:center}</style>
