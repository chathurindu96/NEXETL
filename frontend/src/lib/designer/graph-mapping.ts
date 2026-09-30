import { MarkerType } from '@xyflow/svelte';
import type { PipelineDesign, PipelineDesignEdge, PipelineDesignNode } from '$lib/api/pipelines';
import type { PipelineFlowEdge, PipelineFlowNode } from './graph-model';

export function apiNodeToFlow(node: PipelineDesignNode, readonly = false): PipelineFlowNode {
  const ports=portsForKind(node.kind,node.type);
  return {
    id: node.id,
    type: 'pipeline',
    position: { x: node.positionX, y: node.positionY },
    data: { label: node.label, nodeType: node.type, nodeKind:node.kind, connectorKey: node.connectorKey, configuration:node.configuration, inputSchema:node.inputSchema, outputSchema:node.outputSchema, ...ports },
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
    sourceHandle:edge.sourcePort,
    targetHandle:edge.targetPort,
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
    kind:node.data.nodeKind,
    label: node.data.label,
    connectorKey: node.data.connectorKey,
    configurationVersion:1,
    configuration:node.data.configuration,
    inputSchema:node.data.inputSchema,
    outputSchema:node.data.outputSchema,
    positionX: Math.round(node.position.x),
    positionY: Math.round(node.position.y),
  };
}

export function flowEdgeToApi(edge: PipelineFlowEdge): PipelineDesignEdge {
  return { id: edge.id, sourceNodeId: edge.source, sourcePort:edge.sourceHandle??'output', targetNodeId: edge.target, targetPort:edge.targetHandle??'input' };
}

export function portsForKind(kind:string,type:PipelineDesignNode['type']){
  if(type==='SOURCE')return{inputPorts:[],outputPorts:[{key:'output',displayName:'Output',multiple:true}]};
  if(type==='TARGET')return{inputPorts:[{key:'input',displayName:'Input',multiple:false}],outputPorts:[]};
  if(kind==='join')return{inputPorts:[{key:'left',displayName:'Left',multiple:false},{key:'right',displayName:'Right',multiple:false}],outputPorts:[{key:'output',displayName:'Output',multiple:true}]};
  if(kind==='lookup')return{inputPorts:[{key:'primary',displayName:'Primary',multiple:false},{key:'lookup',displayName:'Lookup',multiple:false}],outputPorts:[{key:'output',displayName:'Output',multiple:true}]};
  if(kind==='union')return{inputPorts:[{key:'input',displayName:'Input',multiple:true}],outputPorts:[{key:'output',displayName:'Output',multiple:true}]};
  if(kind==='split_router')return{inputPorts:[{key:'input',displayName:'Input',multiple:false}],outputPorts:[{key:'matched',displayName:'Routes',multiple:true}]};
  return{inputPorts:[{key:'input',displayName:'Input',multiple:false}],outputPorts:[{key:'output',displayName:'Output',multiple:true}]};
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
