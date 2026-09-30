import type { Edge, Node } from '@xyflow/svelte';
import type { PipelineDesignNodeType, SchemaField } from '$lib/api/pipelines';

export type PipelineNodeData = {
  label: string;
  nodeType: PipelineDesignNodeType;
  nodeKind: string;
  connectorKey: string | null;
  configuration: Record<string, unknown>;
  inputSchema: SchemaField[];
  outputSchema: SchemaField[];
  inputPorts: Array<{key:string;displayName:string;multiple:boolean}>;
  outputPorts: Array<{key:string;displayName:string;multiple:boolean}>;
  status?: string;
};

export type PipelineFlowNode = Node<PipelineNodeData, 'pipeline'>;
export type PipelineFlowEdge = Edge<Record<string, never>, 'smoothstep'>;

export type ConnectionCandidate = {
  source: string | null;
  target: string | null;
  sourceHandle?: string | null;
  targetHandle?: string | null;
};

export type ConnectionCheck = { valid: true } | { valid: false; message: string };
