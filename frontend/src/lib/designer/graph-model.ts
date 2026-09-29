import type { Edge, Node } from '@xyflow/svelte';
import type { PipelineDesignNodeType } from '$lib/api/pipelines';

export type PipelineNodeData = {
  label: string;
  nodeType: PipelineDesignNodeType;
  connectorKey: string | null;
};

export type PipelineFlowNode = Node<PipelineNodeData, 'pipeline'>;
export type PipelineFlowEdge = Edge<Record<string, never>, 'smoothstep'>;

export type ConnectionCandidate = {
  source: string | null;
  target: string | null;
};

export type ConnectionCheck = { valid: true } | { valid: false; message: string };
