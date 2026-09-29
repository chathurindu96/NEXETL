export type NexetlError = { code?: string; detail?: string; message?: string };
export type PipelineState = 'DRAFT' | 'ARCHIVED';
export type PipelineDefinition = {
  id: string; name: string; description: string; state: PipelineState;
  createdAt: string | null; updatedAt: string | null;
};
export type PipelineListQuery = {
  page?: number; pageSize?: number; search?: string; state?: PipelineState;
  sort?: 'updatedAt' | '-updatedAt' | 'createdAt' | '-createdAt' | 'name' | '-name';
};
export type PipelineListResponse = {
  items: PipelineDefinition[]; page: number; pageSize: number; totalItems: number; totalPages: number;
};
export type ConnectorDefinition = {
  key: string; displayName: string; category: 'SOURCE' | 'TARGET' | 'BOTH';
  description: string; vendor: string; version: string; availability: string; capabilities: string[];
};
export type PipelineDesignNodeType = 'SOURCE' | 'TRANSFORM' | 'TARGET';
export type PipelineDesignNode = { id: string; type: PipelineDesignNodeType; label: string; connectorKey: string | null; positionX: number; positionY: number };
export type PipelineDesignEdge = { id: string; sourceNodeId: string; targetNodeId: string };
export type PipelineDesign = { pipelineId: string; revision: number; nodes: PipelineDesignNode[]; edges: PipelineDesignEdge[]; updatedAt: string | null };
export type PipelineDesignValidationIssue = { code: string; message: string; nodeId?: string };
export type PipelineDesignValidationResult = { valid: boolean; issues: PipelineDesignValidationIssue[] };
export type PipelineErrorState = 'authentication' | 'authorization' | 'not_found' | 'validation' | 'csrf' | 'archived' | 'service';

async function safeError(response: Response): Promise<NexetlError> {
  return response.json().catch(() => ({}));
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, { credentials: 'include', ...init });
  if (!response.ok) throw await safeError(response);
  return response.json() as Promise<T>;
}

export async function bootstrapCsrf(): Promise<void> {
  const response = await fetch('/api/security/csrf/', { credentials: 'include' });
  if (!response.ok) throw await safeError(response);
}

export function listPipelineDefinitions(query: PipelineListQuery = {}): Promise<PipelineListResponse> {
  const parameters = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) if (value !== undefined && value !== '') parameters.set(key, String(value));
  const suffix = parameters.size ? `?${parameters}` : '';
  return request(`/api/pipeline-definitions/${suffix}`);
}

export async function registerPipelineDefinition(name: string, description = ''): Promise<PipelineDefinition> {
  return mutate('/api/pipeline-definitions/', 'POST', { name, description });
}

export function getPipelineDefinition(id: string): Promise<PipelineDefinition> {
  return request(`/api/pipeline-definitions/${encodeURIComponent(id)}/`);
}

export async function updatePipelineDefinition(id: string, name: string, description: string): Promise<PipelineDefinition> {
  return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/`, 'PATCH', { name, description });
}

export async function archivePipelineDefinition(id: string): Promise<PipelineDefinition> {
  return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/archive/`, 'POST');
}

export function listConnectors(category?: ConnectorDefinition['category']): Promise<{ items: ConnectorDefinition[] }> {
  return request(`/api/connectors/${category ? `?category=${category}` : ''}`);
}

export function getConnector(key: string): Promise<ConnectorDefinition> {
  return request(`/api/connectors/${encodeURIComponent(key)}/`);
}

export function getPipelineDesign(id: string): Promise<PipelineDesign> { return request(`/api/pipeline-definitions/${encodeURIComponent(id)}/design/`); }
export function savePipelineDesign(id: string, design: Pick<PipelineDesign, 'revision' | 'nodes' | 'edges'>): Promise<PipelineDesign> { return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/design/`, 'PUT', design); }
export function validatePipelineDesign(id: string): Promise<PipelineDesignValidationResult> { return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/design/validate/`, 'POST'); }

async function mutate<T>(path: string, method: 'POST' | 'PATCH' | 'PUT', body?: object): Promise<T> {
  await bootstrapCsrf();
  return request(path, {
    method,
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
    body: body ? JSON.stringify(body) : undefined,
  });
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
    case 'NEXETL_PIPELINE_ARCHIVED': return 'archived';
    default: return 'service';
  }
}

export function pipelineErrorMessage(error: NexetlError): string {
  switch (pipelineErrorState(error)) {
    case 'authentication': return 'Sign in is required to continue.';
    case 'authorization': return 'You are not authorized for this operation.';
    case 'not_found': return 'The requested item was not found.';
    case 'validation': return 'Please review the information and try again.';
    case 'csrf': return 'Your security check could not be completed. Refresh and try again.';
    case 'archived': return 'Archived Pipeline Definitions are read-only.';
    default: return 'The service could not complete this request. Please try again later.';
  }
}
