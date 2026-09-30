export type NexetlError = { code?: string; detail?: string; message?: string; details?: { issues?: PipelineDesignValidationIssue[] } };
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
export type PipelineDesignNodeType = 'SOURCE' | 'TRANSFORM' | 'TARGET' | 'GOVERNANCE';
export type SchemaField = { name: string; logicalType: string; nativeType?: string | null; nullable: boolean; ordinal: number; metadata?: Record<string, unknown> };
export type PipelineDesignNode = { id: string; type: PipelineDesignNodeType; kind: string; label: string; connectorKey: string | null; configurationVersion: number; configuration: Record<string, unknown>; inputSchema: SchemaField[]; outputSchema: SchemaField[]; positionX: number; positionY: number };
export type PipelineDesignEdge = { id: string; sourceNodeId: string; sourcePort: string; targetNodeId: string; targetPort: string };
export type PipelineDesign = { pipelineId: string; revision: number; nodes: PipelineDesignNode[]; edges: PipelineDesignEdge[]; updatedAt: string | null };
export type PipelineDesignValidationIssue = { code: string; severity?: 'ERROR'|'WARNING'|'INFO'; message: string; nodeId?: string; field?: string; suggestion?: string };
export type PipelineDesignValidationResult = { valid: boolean; issues: PipelineDesignValidationIssue[]; schemas?: Record<string, SchemaField[]> };
export type ConnectionDefinition = { id:string; name:string; connectorKey:string; description:string; configuration:Record<string,unknown>; secretReference:string|null; secretConfigured:boolean; state:'ENABLED'|'DISABLED'; createdAt:string; updatedAt:string };
export type NodePortDefinition = { key:string; displayName:string; multiple:boolean };
export type NodeTypeDefinition = { key:string; displayName:string; category:PipelineDesignNodeType; description:string; icon:string; inputs:NodePortDefinition[]; outputs:NodePortDefinition[]; configurationSchema:Record<string,unknown>; configurationDefaults:Record<string,unknown>; executorKey:string; supportsPreview:boolean; supportsSchemaInference:boolean };
export type PipelineVersion = { id:string; pipelineId:string; version:number; designRevision:number; createdAt:string; createdBy:string|null; graph?:PipelineDesign };
export type PipelineNodeRun = { id:string; label:string; kind:string; status:string; startedAt:string|null; finishedAt:string|null; durationMs:number|null; inputRows:number; outputRows:number; rejectedRows:number; batchCount:number; errorCode:string|null; errorMessage:string; metrics:Record<string,number> };
export type PipelineRun = { id:string; pipelineId:string; pipelineVersionId:string; version:number; status:string; triggerType:string; initiatedBy:string|null; queuedAt:string; startedAt:string|null; finishedAt:string|null; durationMs:number|null; currentNodeId:string|null; cancellationRequested:boolean; errorCode:string|null; errorMessage:string; metrics:Record<string,number>; attempt:number; parentRunId:string|null; graph?:PipelineDesign; nodes?:PipelineNodeRun[]; events?:Array<{id:number;timestamp:string;level:string;event:string;nodeId:string|null;message:string;context:Record<string,unknown>}> };
export type PipelineRunList = { items:PipelineRun[]; page:number; pageSize:number; totalItems:number; totalPages:number };
export type PipelineSchedule = { id:string; pipelineId:string; name:string; enabled:boolean; expression:string; timezone:string; nextRunAt:string|null; lastRunAt:string|null; createdAt:string; updatedAt:string };
export type OperationsSummary = { runningNow:number; failedRuns:number; runsToday:number; scheduledPipelines:number; availableConnections:number; recentRuns:Array<PipelineRun&{pipelineName:string}> };
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
export function listConnections():Promise<{items:ConnectionDefinition[]}>{return request('/api/connections/');}
export function getConnection(id:string):Promise<ConnectionDefinition>{return request(`/api/connections/${encodeURIComponent(id)}/`);}
export function createConnection(value:{name:string;connectorKey:string;description:string;configuration:Record<string,unknown>;password:string}):Promise<ConnectionDefinition>{return mutate('/api/connections/','POST',value);}
export function updateConnection(id:string,value:Partial<ConnectionDefinition>&{password?:string}):Promise<ConnectionDefinition>{return mutate(`/api/connections/${encodeURIComponent(id)}/`,'PATCH',value);}
export function testConnection(id:string):Promise<{success:boolean;latencyMs:number;database:string;server:string}>{return mutate(`/api/connections/${encodeURIComponent(id)}/test/`,'POST');}
export function discoverSchemas(id:string):Promise<{items:string[]}>{return request(`/api/connections/${encodeURIComponent(id)}/schemas/`);}
export function discoverDatasets(id:string,schema:string):Promise<{items:Array<{name:string;type:string}>}>{return request(`/api/connections/${encodeURIComponent(id)}/datasets/?schema=${encodeURIComponent(schema)}`);}
export function discoverDatasetSchema(id:string,schema:string,dataset:string):Promise<{fields:SchemaField[]}>{return request(`/api/connections/${encodeURIComponent(id)}/datasets/${encodeURIComponent(dataset)}/schema/?schema=${encodeURIComponent(schema)}`);}
export function previewDataset(id:string,schema:string,dataset:string,limit=50):Promise<{columns:string[];rows:Array<Record<string,unknown>>;rowCount:number;limit:number}>{return request(`/api/connections/${encodeURIComponent(id)}/preview/?schema=${encodeURIComponent(schema)}&dataset=${encodeURIComponent(dataset)}&limit=${limit}`);}
export function listNodeTypes():Promise<{items:NodeTypeDefinition[]}>{return request('/api/node-types/');}
export function listPipelineVersions(id:string):Promise<{items:PipelineVersion[]}>{return request(`/api/pipeline-definitions/${encodeURIComponent(id)}/versions/`);}
export function publishPipelineVersion(id:string):Promise<PipelineVersion>{return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/versions/`,'POST');}
export function listPipelineRuns(id:string,page=1):Promise<PipelineRunList>{return request(`/api/pipeline-definitions/${encodeURIComponent(id)}/runs/?page=${page}&pageSize=20`);}
export function getPipelineRun(id:string,runId:string):Promise<PipelineRun>{return request(`/api/pipeline-definitions/${encodeURIComponent(id)}/runs/${encodeURIComponent(runId)}/`);}
export function runPipeline(id:string):Promise<PipelineRun>{return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/runs/`,'POST');}
export function cancelPipelineRun(id:string,runId:string):Promise<PipelineRun>{return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/runs/${encodeURIComponent(runId)}/cancel/`,'POST');}
export function retryPipelineRun(id:string,runId:string):Promise<PipelineRun>{return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/runs/${encodeURIComponent(runId)}/retry/`,'POST');}
export function listPipelineSchedules(id:string):Promise<{items:PipelineSchedule[]}>{return request(`/api/pipeline-definitions/${encodeURIComponent(id)}/schedules/`);}
export function createPipelineSchedule(id:string,value:{name:string;expression:string;timezone:string;enabled:boolean}):Promise<PipelineSchedule>{return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/schedules/`,'POST',value);}
export function updatePipelineSchedule(id:string,scheduleId:string,value:Partial<PipelineSchedule>):Promise<PipelineSchedule>{return mutate(`/api/pipeline-definitions/${encodeURIComponent(id)}/schedules/${encodeURIComponent(scheduleId)}/`,'PATCH',value);}
export function getOperationsSummary():Promise<OperationsSummary>{return request('/api/operations/summary/');}

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
