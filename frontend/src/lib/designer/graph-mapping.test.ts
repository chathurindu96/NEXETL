import { describe, expect, it } from 'vitest';
import type { PipelineDesign } from '$lib/api/pipelines';
import { apiDesignToFlow, flowEdgeToApi, flowNodeToApi, flowToApiDesign } from './graph-mapping';

const design: PipelineDesign = {
  pipelineId:'pipeline-1', revision:3, updatedAt:'2026-09-29T10:00:00Z',
  nodes:[
    {id:'source',type:'SOURCE',kind:'database_source',label:'Orders',connectorKey:'postgresql',configurationVersion:1,configuration:{},inputSchema:[],outputSchema:[],positionX:80,positionY:120},
    {id:'target',type:'TARGET',kind:'database_target',label:'Warehouse',connectorKey:'postgresql',configurationVersion:1,configuration:{},inputSchema:[],outputSchema:[],positionX:520,positionY:240},
  ],
  edges:[{id:'edge-1',sourceNodeId:'source',sourcePort:'output',targetNodeId:'target',targetPort:'input'}],
};

describe('graph mapping',()=>{
  it('maps API nodes into graph-space positions and typed data',()=>{const graph=apiDesignToFlow(design);expect(graph.nodes[0].position).toEqual({x:80,y:120});expect(graph.nodes[0].data).toMatchObject({label:'Orders',nodeType:'SOURCE',nodeKind:'database_source',connectorKey:'postgresql',configuration:{}})});
  it('maps API edges without leaking domain field names into the graph',()=>{const graph=apiDesignToFlow(design);expect(graph.edges[0]).toMatchObject({id:'edge-1',source:'source',target:'target',type:'smoothstep'})});
  it('locks graph elements when the Pipeline is archived',()=>{const graph=apiDesignToFlow(design,true);expect(graph.nodes.every(node=>node.draggable===false&&node.connectable===false)).toBe(true);expect(graph.edges[0].deletable).toBe(false)});
  it('rounds graph coordinates for persistence',()=>{const node=apiDesignToFlow(design).nodes[0];node.position={x:381.7,y:221.2};expect(flowNodeToApi(node)).toMatchObject({positionX:382,positionY:221})});
  it('maps graph edges back to the stable API contract',()=>{expect(flowEdgeToApi(apiDesignToFlow(design).edges[0])).toEqual(design.edges[0])});
  it('preserves revision metadata while serializing editor state',()=>{const graph=apiDesignToFlow(design);expect(flowToApiDesign(design,graph.nodes,graph.edges)).toEqual(design)});
});
