import type { ConnectionCandidate, ConnectionCheck, PipelineFlowEdge, PipelineFlowNode } from './graph-model';

export function checkConnection(
  candidate: ConnectionCandidate,
  nodes: PipelineFlowNode[],
  edges: PipelineFlowEdge[],
): ConnectionCheck {
  const { source, target } = candidate;
  if (!source || !target) return { valid: false, message: 'Choose both a source and target node.' };
  if (source === target) return { valid: false, message: 'A node cannot connect to itself.' };
  const sourceNode = nodes.find((node) => node.id === source);
  const targetNode = nodes.find((node) => node.id === target);
  if (!sourceNode || !targetNode) return { valid: false, message: 'One of the selected nodes no longer exists.' };
  if (sourceNode.data.nodeType === 'TARGET') return { valid: false, message: 'Target nodes cannot originate connections.' };
  if (targetNode.data.nodeType === 'SOURCE') return { valid: false, message: 'Source nodes cannot receive connections.' };
  if (edges.some((edge) => edge.source === source && edge.target === target)) return { valid: false, message: 'That connection already exists.' };
  if (wouldCreateCycle(source, target, edges)) return { valid: false, message: 'That connection would create a cycle.' };
  return { valid: true };
}

function wouldCreateCycle(source: string, target: string, edges: PipelineFlowEdge[]): boolean {
  const outgoing = new Map<string, string[]>();
  for (const edge of edges) outgoing.set(edge.source, [...(outgoing.get(edge.source) ?? []), edge.target]);
  const pending = [target];
  const seen = new Set<string>();
  while (pending.length) {
    const current = pending.pop()!;
    if (current === source) return true;
    if (seen.has(current)) continue;
    seen.add(current);
    pending.push(...(outgoing.get(current) ?? []));
  }
  return false;
}
