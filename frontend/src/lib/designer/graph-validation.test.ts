import { describe, expect, it } from 'vitest';
import { apiDesignToFlow } from './graph-mapping';
import { checkConnection } from './graph-validation';
import type { PipelineDesign } from '$lib/api/pipelines';

const graph=apiDesignToFlow({pipelineId:'p',revision:1,updatedAt:null,nodes:[
  {id:'s',type:'SOURCE',label:'Source',connectorKey:'postgresql',positionX:0,positionY:0},
  {id:'a',type:'TRANSFORM',label:'A',connectorKey:null,positionX:200,positionY:0},
  {id:'b',type:'TRANSFORM',label:'B',connectorKey:null,positionX:400,positionY:0},
  {id:'t',type:'TARGET',label:'Target',connectorKey:'postgresql',positionX:600,positionY:0},
],edges:[{id:'e1',sourceNodeId:'s',targetNodeId:'a'},{id:'e2',sourceNodeId:'a',targetNodeId:'b'}]} satisfies PipelineDesign);

describe('connection validation',()=>{
  it('accepts a valid forward connection',()=>expect(checkConnection({source:'b',target:'t'},graph.nodes,graph.edges)).toEqual({valid:true}));
  it('rejects missing endpoints',()=>expect(checkConnection({source:null,target:'t'},graph.nodes,graph.edges)).toMatchObject({valid:false}));
  it('rejects self connections',()=>expect(checkConnection({source:'a',target:'a'},graph.nodes,graph.edges)).toMatchObject({valid:false,message:'A node cannot connect to itself.'}));
  it('rejects connections originating from Targets',()=>expect(checkConnection({source:'t',target:'a'},graph.nodes,graph.edges)).toMatchObject({valid:false,message:'Target nodes cannot originate connections.'}));
  it('rejects connections entering Sources',()=>expect(checkConnection({source:'a',target:'s'},graph.nodes,graph.edges)).toMatchObject({valid:false,message:'Source nodes cannot receive connections.'}));
  it('rejects duplicate connections',()=>expect(checkConnection({source:'s',target:'a'},graph.nodes,graph.edges)).toMatchObject({valid:false,message:'That connection already exists.'}));
  it('rejects direct cycles',()=>expect(checkConnection({source:'b',target:'a'},graph.nodes,graph.edges)).toMatchObject({valid:false,message:'That connection would create a cycle.'}));
  it('rejects longer cycles',()=>expect(checkConnection({source:'b',target:'s'},graph.nodes,graph.edges)).toMatchObject({valid:false}));
  it('rejects stale node identifiers',()=>expect(checkConnection({source:'missing',target:'t'},graph.nodes,graph.edges)).toMatchObject({valid:false}));
});
