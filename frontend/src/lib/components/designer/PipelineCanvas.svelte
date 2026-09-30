<script lang="ts">
  import '@xyflow/svelte/dist/style.css';
  import { Background, BackgroundVariant, Controls, MiniMap, SvelteFlow, useSvelteFlow, type Connection } from '@xyflow/svelte';
  import Icon from '$lib/components/ui/Icon.svelte';
  import type { PipelineFlowEdge, PipelineFlowNode } from '$lib/designer/graph-model';
  import PipelineNode from './PipelineNode.svelte';

  let { nodes = $bindable(), edges = $bindable(), readonly, fitRequest, connectionMessage, onselectnode, onselectedge, onclear, onbeforeconnect, onconnected, ondragstart, ondragstop, ondelete, ondropnode }: {
    nodes: PipelineFlowNode[]; edges: PipelineFlowEdge[]; readonly: boolean; fitRequest: number; connectionMessage: string;
    onselectnode:(id:string)=>void; onselectedge:(id:string)=>void; onclear:()=>void;
    onbeforeconnect:(connection:Connection)=>PipelineFlowEdge|false; onconnected:()=>void; ondragstart:()=>void; ondragstop:()=>void; ondelete:(nodes:PipelineFlowNode[],edges:PipelineFlowEdge[])=>void;
    ondropnode:(kind:string,position:{x:number;y:number})=>void;
  } = $props();
  const nodeTypes = { pipeline: PipelineNode };
  const { fitView, screenToFlowPosition } = useSvelteFlow<PipelineFlowNode, PipelineFlowEdge>();
  let initialized = $state(false), lastFitRequest = $state(0);
  $effect(() => { if (initialized && fitRequest !== lastFitRequest) { lastFitRequest = fitRequest; void fitView({ padding: .22, maxZoom: 1.15, duration: 240 }); } });
</script>

<section class="canvas" aria-label="Pipeline design canvas" ondragover={(event)=>{if(!readonly){event.preventDefault();if(event.dataTransfer)event.dataTransfer.dropEffect='copy'}}} ondrop={(event)=>{event.preventDefault();const kind=event.dataTransfer?.getData('application/x-nexetl-node-kind');if(kind&&!readonly)ondropnode(kind,screenToFlowPosition({x:event.clientX,y:event.clientY}))}}>
  <SvelteFlow bind:nodes bind:edges {nodeTypes} fitView={nodes.length > 0} fitViewOptions={{ padding: .22, maxZoom: 1.1 }}
    nodesDraggable={!readonly} nodesConnectable={!readonly} elementsSelectable={true} minZoom={.35} maxZoom={1.8}
    panOnDrag={true} zoomOnScroll={true} snapGrid={[10,10]} defaultEdgeOptions={{ type:'smoothstep' }}
    deleteKey={readonly ? null : ['Backspace','Delete']} oninit={() => initialized = true}
    onnodeclick={({node}) => onselectnode(node.id)} onedgeclick={({edge}) => onselectedge(edge.id)} onpaneclick={onclear}
    onnodedragstart={ondragstart} onnodedragstop={ondragstop} onbeforeconnect={onbeforeconnect} onconnect={onconnected}
    ondelete={({nodes:deletedNodes,edges:deletedEdges}) => ondelete(deletedNodes,deletedEdges)} colorMode="light">
    <Background variant={BackgroundVariant.Dots} gap={20} size={1.25} patternColor="#c9d2de" />
    <Controls position="bottom-left" showLock={false} />
    {#if nodes.length>5}<MiniMap position="bottom-right" pannable zoomable maskColor="rgb(242 245 250 / 72%)" />{/if}
  </SvelteFlow>
  {#if nodes.length===0}<div class="empty"><span><Icon name="pipelines" size={25}/></span><h2>Build your Pipeline</h2><p>Add a Source, Transform or Target from the node palette.</p></div>{/if}
  {#if connectionMessage}<div class="connection-message" role="status">{connectionMessage}</div>{/if}
  <div class="canvas-meta">{nodes.length} nodes · {edges.length} connections</div>
</section>

<style>
  .canvas{position:relative;min-width:0;min-height:0;height:100%;overflow:hidden;background:#f7f9fc}
  :global(.svelte-flow){background:#f7f9fc}:global(.svelte-flow__node){border:0!important;background:transparent!important;padding:0!important;box-shadow:none!important}:global(.svelte-flow__edge-path){stroke:#8996a8;stroke-width:1.6}:global(.svelte-flow__edge.selected .svelte-flow__edge-path),:global(.svelte-flow__edge:focus .svelte-flow__edge-path){stroke:var(--accent);stroke-width:2.4}:global(.svelte-flow__controls){overflow:hidden;border:1px solid var(--border-default);border-radius:8px;background:#fff;box-shadow:var(--shadow-md)}:global(.svelte-flow__controls-button){border-bottom-color:var(--border-subtle);color:var(--text-secondary)}
  .empty{position:absolute;inset:0;z-index:2;display:grid;place-content:center;justify-items:center;color:var(--text-muted);text-align:center;pointer-events:none}.empty span{display:grid;width:3.4rem;height:3.4rem;place-items:center;border:1px solid var(--border-default);border-radius:13px;background:#fff;color:var(--accent);box-shadow:var(--shadow-sm)}.empty h2{margin:.9rem 0 .2rem;color:var(--text-secondary);font-size:1rem}.empty p{margin:0;font-size:.76rem}
  .canvas-meta{position:absolute;right:1rem;bottom:1rem;z-index:4;border:1px solid var(--border-default);border-radius:999px;background:rgb(255 255 255 / 92%);padding:.26rem .58rem;color:var(--text-muted);font-size:.62rem;pointer-events:none}.connection-message{position:absolute;top:1rem;left:50%;z-index:5;transform:translateX(-50%);border:1px solid #efd3a4;border-radius:7px;background:#fff9ed;padding:.42rem .7rem;color:#8e5711;font-size:.68rem;box-shadow:var(--shadow-sm)}
</style>
