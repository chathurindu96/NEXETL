<script lang="ts">
  import { beforeNavigate } from '$app/navigation';
  import { page } from '$app/state';
  import { onDestroy, onMount } from 'svelte';
  import { SvelteFlowProvider, type Connection } from '@xyflow/svelte';
  import { getPipelineDefinition,getPipelineDesign,listConnectors,pipelineErrorMessage,savePipelineDesign,validatePipelineDesign,type ConnectorDefinition,type NexetlError,type PipelineDefinition,type PipelineDesign,type PipelineDesignNodeType,type PipelineDesignValidationResult } from '$lib/api/pipelines';
  import { apiDesignToFlow, apiEdgeToFlow, flowNodeToApi, flowToApiDesign } from '$lib/designer/graph-mapping';
  import type { PipelineFlowEdge, PipelineFlowNode } from '$lib/designer/graph-model';
  import { checkConnection } from '$lib/designer/graph-validation';
  import { routeEntity } from '$lib/route-context';
  import Alert from '$lib/components/ui/Alert.svelte'; import Icon from '$lib/components/ui/Icon.svelte';
  import PipelineDesignerHeader from '$lib/components/designer/PipelineDesignerHeader.svelte'; import NodePalette from '$lib/components/designer/NodePalette.svelte'; import PipelineCanvas from '$lib/components/designer/PipelineCanvas.svelte'; import NodeInspector from '$lib/components/designer/NodeInspector.svelte';

  let pipeline=$state<PipelineDefinition|null>(null), persisted=$state<PipelineDesign|null>(null), connectors=$state<ConnectorDefinition[]>([]);
  let nodes=$state.raw<PipelineFlowNode[]>([]),edges=$state.raw<PipelineFlowEdge[]>([]),selectedNodeId=$state<string|null>(null),selectedEdgeId=$state<string|null>(null);
  let loading=$state(true),saving=$state(false),dirty=$state(false),error=$state(''),conflict=$state(false),validation=$state<PipelineDesignValidationResult|null>(null),fitRequest=$state(0),connectionMessage=$state('');
  let status=$derived<'saved'|'dirty'|'error'|'conflict'>(conflict?'conflict':error&&persisted?'error':dirty?'dirty':'saved');
  let selectedNode=$derived(nodes.find(n=>n.id===selectedNodeId)??null),selectedEdge=$derived(edges.find(e=>e.id===selectedEdgeId)??null),readonly=$derived(pipeline?.state==='ARCHIVED');

  $effect(()=>{const id=page.params.pipelineDefinitionId;if(id)void load(id)});
  beforeNavigate(({cancel})=>{if(dirty&&!saving&&!confirm('You have unsaved Pipeline changes. Leave without saving?'))cancel()});
  onMount(()=>{const before=(event:BeforeUnloadEvent)=>{if(dirty){event.preventDefault();event.returnValue=''}};const keys=(event:KeyboardEvent)=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='s'){event.preventDefault();if(dirty&&!saving&&!readonly)void save()}};window.addEventListener('beforeunload',before);window.addEventListener('keydown',keys);return()=>{window.removeEventListener('beforeunload',before);window.removeEventListener('keydown',keys)}});
  onDestroy(()=>routeEntity.set(null));

  async function load(id:string){loading=true;error='';conflict=false;validation=null;try{const[p,d,c]=await Promise.all([getPipelineDefinition(id),getPipelineDesign(id),listConnectors()]);pipeline=p;routeEntity.set(p.name);persisted=d;connectors=c.items.filter(item=>item.availability==='AVAILABLE');const graph=apiDesignToFlow(d,p.state==='ARCHIVED');nodes=graph.nodes;edges=graph.edges;selectedNodeId=null;selectedEdgeId=null;dirty=false;requestAnimationFrame(()=>fitRequest++)}catch(failure){error=pipelineErrorMessage(failure as NexetlError)}finally{loading=false}}
  function changed(){if(readonly)return;dirty=true;validation=null;error='';conflict=false}
  function selectNode(id:string|null){selectedNodeId=id;selectedEdgeId=null;nodes=nodes.map(node=>({...node,selected:node.id===id}));edges=edges.map(edge=>({...edge,selected:false}))}
  function selectEdge(id:string|null){selectedEdgeId=id;selectedNodeId=null;edges=edges.map(edge=>({...edge,selected:edge.id===id}));nodes=nodes.map(node=>({...node,selected:false}))}
  function clearSelection(){selectedNodeId=null;selectedEdgeId=null;nodes=nodes.map(node=>({...node,selected:false}));edges=edges.map(edge=>({...edge,selected:false}))}
  function add(type:PipelineDesignNodeType){if(readonly)return;const connector=type==='TRANSFORM'?null:connectors[0]?.key??null,index=nodes.length,id=crypto.randomUUID();nodes=[...nodes,{id,type:'pipeline',position:{x:80+(index%3)*270,y:80+Math.floor(index/3)*150},data:{label:type==='TRANSFORM'?'Transform':`${connectors.find(c=>c.key===connector)?.displayName??type} ${type==='SOURCE'?'Source':'Target'}`,nodeType:type,connectorKey:connector},draggable:true,connectable:true,deletable:true,selected:true}];changed();selectNode(id)}
  function updateNode(values:Partial<{label:string;connectorKey:string}>){if(!selectedNodeId||readonly)return;nodes=nodes.map(node=>node.id===selectedNodeId?{...node,data:{...node.data,...values}}:node);changed()}
  function removeNode(){if(!selectedNodeId||readonly)return;const id=selectedNodeId;nodes=nodes.filter(node=>node.id!==id);edges=edges.filter(edge=>edge.source!==id&&edge.target!==id);selectedNodeId=null;changed()}
  function connect(source:string,target:string){if(readonly)return;const result=checkConnection({source,target},nodes,edges);if(!result.valid){connectionMessage=result.message;setTimeout(()=>connectionMessage='',3200);return}const edge={id:crypto.randomUUID(),source,target,type:'smoothstep' as const,deletable:true,focusable:true};edges=[...edges,apiEdgeToFlow({id:edge.id,sourceNodeId:source,targetNodeId:target})];connectionMessage='Connection added.';setTimeout(()=>connectionMessage='',1600);changed()}
  function beforeVisualConnect(connection:Connection):PipelineFlowEdge|false{const result=checkConnection(connection,nodes,edges);if(!result.valid){connectionMessage=result.message;setTimeout(()=>connectionMessage='',3200);return false}changed();return apiEdgeToFlow({id:crypto.randomUUID(),sourceNodeId:connection.source!,targetNodeId:connection.target!})}
  function visualConnected(){connectionMessage='Connection added.';setTimeout(()=>connectionMessage='',1600)}
  function removeEdge(){if(!selectedEdgeId||readonly)return;edges=edges.filter(edge=>edge.id!==selectedEdgeId);selectedEdgeId=null;changed()}
  function removeEdgeById(id:string){if(readonly)return;edges=edges.filter(edge=>edge.id!==id);if(selectedEdgeId===id)selectedEdgeId=null;changed()}
  function deleted(deletedNodes:PipelineFlowNode[],deletedEdges:PipelineFlowEdge[]){if(readonly)return;if(deletedNodes.length||deletedEdges.length){selectedNodeId=null;selectedEdgeId=null;changed()}}
  async function save():Promise<boolean>{if(!persisted||readonly)return true;saving=true;error='';conflict=false;try{const payload=flowToApiDesign(persisted,nodes,edges);persisted=await savePipelineDesign(persisted.pipelineId,payload);const graph=apiDesignToFlow(persisted,false);nodes=graph.nodes;edges=graph.edges;dirty=false;return true}catch(failure){const typed=failure as NexetlError;conflict=typed.code==='NEXETL_PIPELINE_DESIGN_REVISION_CONFLICT';error=conflict?'A newer version of this Pipeline Design was saved elsewhere. Your local version was not overwritten.':pipelineErrorMessage(typed);return false}finally{saving=false}}
  async function validate(){if(!persisted)return;if(dirty&&!await save())return;error='';try{validation=await validatePipelineDesign(persisted.pipelineId)}catch(failure){error=pipelineErrorMessage(failure as NexetlError)}}
</script>

<svelte:head><title>{pipeline?.name??'Pipeline'} Design | NEXETL</title></svelte:head>
{#if loading}<div class="loading" role="status"><span></span>Preparing Pipeline Designer…</div>
{:else if error&&!persisted}<div class="load-error"><Alert variant="error">{error}</Alert></div>
{:else if persisted&&pipeline}
  <div class="workspace"><div class:has-notice={Boolean(error)} class="desktop-workspace">
    <PipelineDesignerHeader {pipeline} revision={persisted.revision} {status} {saving} onfit={()=>fitRequest++} onvalidate={validate} onsave={save}/>
    {#if error}<div class:conflict class="notice" role="alert"><Icon name="check" size={17}/><span>{error}</span>{#if conflict}<button onclick={()=>load(persisted!.pipelineId)}>Reload latest</button>{/if}</div>{/if}
    <div class="designer-grid"><NodePalette {readonly} onadd={add}/><SvelteFlowProvider><PipelineCanvas bind:nodes bind:edges {readonly} {fitRequest} {connectionMessage} onselectnode={selectNode} onselectedge={selectEdge} onclear={clearSelection} onbeforeconnect={beforeVisualConnect} onconnected={visualConnected} ondragstop={changed} ondelete={deleted}/></SvelteFlowProvider><NodeInspector node={selectedNode ? flowNodeToApi(selectedNode) : null} selectedEdge={selectedEdge?{id:selectedEdge.id,sourceNodeId:selectedEdge.source,targetNodeId:selectedEdge.target}:null} nodes={nodes.map(flowNodeToApi)} edges={edges.map(edge=>({id:edge.id,sourceNodeId:edge.source,targetNodeId:edge.target}))} pipelineName={pipeline.name} pipelineState={pipeline.state} connectors={connectors} revision={persisted.revision} {readonly} {validation} onLabel={(label)=>updateNode({label})} onConnector={(connectorKey)=>updateNode({connectorKey})} onDeleteNode={removeNode} onDeleteEdge={removeEdge} onDeleteEdgeById={removeEdgeById} onConnect={connect} onSelectNode={selectNode}/></div>
  </div><div class="mobile-limitation"><span><Icon name="pipelines" size={24}/></span><h1>Use a larger screen to edit this Pipeline.</h1><p>The complete graph remains available from the Pipeline details page. Desktop authoring protects precise node placement.</p><a href={`/pipelines/${pipeline.id}`}>View Pipeline details</a></div></div>
{/if}

<style>
  .workspace{height:100%;min-height:0;overflow:hidden;background:var(--bg-canvas)}.desktop-workspace{display:grid;height:100%;min-height:0;grid-template-rows:auto minmax(0,1fr);overflow:hidden}.desktop-workspace.has-notice{grid-template-rows:auto auto minmax(0,1fr)}.designer-grid{display:grid;min-height:0;overflow:hidden;grid-template-columns:232px minmax(360px,1fr) 304px}.notice{z-index:7;display:flex;align-items:center;gap:.6rem;border-bottom:1px solid #f0d0cd;background:#fff3f2;padding:.58rem 1rem;color:var(--danger);font-size:.72rem}.notice button{margin-left:auto;border:1px solid currentColor;border-radius:var(--radius-sm);background:transparent;padding:.28rem .55rem;color:inherit;font-size:.68rem;font-weight:650;cursor:pointer}.notice.conflict{background:#fff8ed;color:var(--warning);border-color:#f0dbb9}.loading{display:flex;height:100%;align-items:center;justify-content:center;gap:.65rem;color:var(--text-muted)}.loading span{width:1rem;height:1rem;border:2px solid var(--border-default);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite}.load-error{padding:2rem}.mobile-limitation{display:none}@keyframes spin{to{transform:rotate(360deg)}}
  @media(max-width:1100px) and (min-width:769px){.designer-grid{grid-template-columns:190px minmax(300px,1fr) 264px}}
  @media(max-width:768px){.desktop-workspace{display:none}.mobile-limitation{display:grid;height:100%;place-content:center;justify-items:center;padding:2rem;text-align:center}.mobile-limitation span{display:grid;width:3.5rem;height:3.5rem;place-items:center;border:1px solid var(--border-default);border-radius:var(--radius-lg);background:#fff;color:var(--accent)}.mobile-limitation h1{max-width:24rem;margin:1rem 0 .4rem;font-size:1.1rem}.mobile-limitation p{max-width:28rem;margin:0 0 1rem;color:var(--text-muted);font-size:.8rem}.mobile-limitation a{border:1px solid var(--border-default);border-radius:var(--radius-sm);background:#fff;padding:.5rem .75rem;font-size:.75rem;font-weight:650}}
</style>
