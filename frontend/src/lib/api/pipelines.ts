export type NexetlError = { code?: string; message?: string };

export type PipelineErrorState = 'authentication' | 'authorization' | 'not_found' | 'validation' | 'csrf' | 'service';

async function safeError(response: Response): Promise<NexetlError> {
  return response.json().catch(() => ({}));
}

export async function bootstrapCsrf(): Promise<void> {
  const response = await fetch('/api/security/csrf/', { credentials: 'include' });
  if (!response.ok) throw await safeError(response);
}

export async function registerPipelineDefinition(): Promise<string> {
  const response = await fetch('/api/pipeline-definitions/', {
    method: 'POST', credentials: 'include', headers: { 'X-CSRFToken': csrfToken() },
  });
  if (!response.ok) throw await safeError(response);
  return (await response.json()).id;
}

export async function getPipelineDefinition(id: string): Promise<string> {
  const response = await fetch(`/api/pipeline-definitions/${id}/`, { credentials: 'include' });
  if (!response.ok) throw await safeError(response);
  return (await response.json()).id;
}

function csrfToken(): string {
  return document.cookie.split('; ').find((entry) => entry.startsWith('csrftoken='))?.split('=')[1] ?? '';
}

export function pipelineErrorState(error: NexetlError): PipelineErrorState {
  switch (error.code) {
    case 'NEXETL_AUTHENTICATION_REQUIRED': return 'authentication';
    case 'NEXETL_AUTHORIZATION_DENIED': return 'authorization';
    case 'NEXETL_PIPELINE_DEFINITION_NOT_FOUND': return 'not_found';
    case 'NEXETL_VALIDATION_FAILED': return 'validation';
    case 'NEXETL_CSRF_REJECTED': return 'csrf';
    default: return 'service';
  }
}

export function pipelineErrorMessage(error: NexetlError): string {
  switch (pipelineErrorState(error)) {
    case 'authentication': return 'Sign in is required to continue.';
    case 'authorization': return 'You are not authorized for this operation.';
    case 'not_found': return 'The Pipeline Definition was not found.';
    case 'validation': return 'The Pipeline Definition identifier is invalid.';
    case 'csrf': return 'Your security check could not be completed. Refresh and try again.';
    default: return 'The service could not complete this request. Please try again later.';
  }
}
