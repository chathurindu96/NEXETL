<script lang="ts">
  import type { PipelineDesignEdge, PipelineDesignNode } from '$lib/api/pipelines';
  let { nodes, edges, selectedEdgeId, onselect }: { nodes: PipelineDesignNode[]; edges: PipelineDesignEdge[]; selectedEdgeId: string | null; onselect: (id: string) => void } = $props();
  function path(edge: PipelineDesignEdge) { const source=nodes.find((n)=>n.id===edge.sourceNodeId), target=nodes.find((n)=>n.id===edge.targetNodeId); if(!source||!target)return ''; const sx=source.positionX+208, sy=source.positionY+38, tx=target.positionX, ty=target.positionY+38, mid=sx+(tx-sx)/2; return `M ${sx} ${sy} C ${mid} ${sy}, ${mid} ${ty}, ${tx} ${ty}`; }
</script>
<svg class="edges" viewBox="0 0 2000 1200" preserveAspectRatio="none" aria-label="Pipeline connections">
  <defs><marker id="edge-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z"/></marker></defs>
  {#each edges as edge}
    <path class="edge-hit" d={path(edge)} role="button" tabindex="0" aria-label="Select connection" onclick={() => onselect(edge.id)} onkeydown={(event) => { if (event.key === 'Enter' || event.key === ' ') onselect(edge.id); }}><title>Select connection</title></path>
    <path class:selected={selectedEdgeId===edge.id} class="edge" d={path(edge)} marker-end="url(#edge-arrow)"></path>
  {/each}
</svg>
<style>.edges{position:absolute;inset:0;width:2000px;height:1200px;overflow:visible;pointer-events:none}.edge{fill:none;stroke:#98a4b3;stroke-width:2;marker-end:url(#edge-arrow);pointer-events:none}.edge.selected{stroke:var(--accent);stroke-width:2.5}marker path{fill:#98a4b3}.edge-hit{fill:none;stroke:transparent;stroke-width:14;pointer-events:stroke;cursor:pointer}</style>
