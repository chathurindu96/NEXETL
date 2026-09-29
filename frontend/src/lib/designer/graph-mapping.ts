import { MarkerType } from '@xyflow/svelte';
import type { PipelineDesign, PipelineDesignEdge, PipelineDesignNode } from '$lib/api/pipelines';
import type { PipelineFlowEdge, PipelineFlowNode } from './graph-model';

export function apiNodeToFlow(node: PipelineDesignNode, readonly = false): PipelineFlowNode {
  return {
    id: node.id,
    type: 'pipeline',
    position: { x: node.positionX, y: node.positionY },
    data: { label: node.label, nodeType: node.type, connectorKey: node.connectorKey },
    draggable: !readonly,
    connectable: !readonly,
    deletable: !readonly,
    ariaLabel: `${node.label}, ${node.type.toLowerCase()} node`,
  };
}

export function apiEdgeToFlow(edge: PipelineDesignEdge, readonly = false): PipelineFlowEdge {
  return {
    id: edge.id,
    source: edge.sourceNodeId,
    target: edge.targetNodeId,
    type: 'smoothstep',
    deletable: !readonly,
    focusable: true,
    markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
  };
}

export function apiDesignToFlow(design: PipelineDesign, readonly = false) {
  return {
    nodes: design.nodes.map((node) => apiNodeToFlow(node, readonly)),
    edges: design.edges.map((edge) => apiEdgeToFlow(edge, readonly)),
  };
}

export function flowNodeToApi(node: PipelineFlowNode): PipelineDesignNode {
  return {
    id: node.id,
    type: node.data.nodeType,
    label: node.data.label,
    connectorKey: node.data.connectorKey,
    positionX: Math.round(node.position.x),
    positionY: Math.round(node.position.y),
  };
}

export function flowEdgeToApi(edge: PipelineFlowEdge): PipelineDesignEdge {
  return { id: edge.id, sourceNodeId: edge.source, targetNodeId: edge.target };
}

export function flowToApiDesign(
  persisted: Pick<PipelineDesign, 'pipelineId' | 'revision' | 'updatedAt'>,
  nodes: PipelineFlowNode[],
  edges: PipelineFlowEdge[],
): PipelineDesign {
  return {
    ...persisted,
    nodes: nodes.map(flowNodeToApi),
    edges: edges.map(flowEdgeToApi),
  };
}
