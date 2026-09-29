<script lang="ts">
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import Icon from '$lib/components/ui/Icon.svelte';
  import type { PipelineFlowNode } from '$lib/designer/graph-model';

  let { data, selected }: NodeProps<PipelineFlowNode> = $props();
  const icon = $derived(data.nodeType === 'SOURCE' ? 'database' : data.nodeType === 'TARGET' ? 'target' : 'transform');
</script>

<div class:selected class="pipeline-node {data.nodeType.toLowerCase()}">
  {#if data.nodeType !== 'SOURCE'}<Handle id="input" type="target" position={Position.Left} class="pipeline-handle input-handle" />{/if}
  <span class="node-icon"><Icon name={icon} size={18}/></span>
  <span class="identity"><strong>{data.label}</strong><small>{data.nodeType}</small></span>
  {#if data.nodeType !== 'TRANSFORM'}<span class="connector">{data.connectorKey ?? 'No connector'}</span>{/if}
  {#if data.nodeType !== 'TARGET'}<Handle id="output" type="source" position={Position.Right} class="pipeline-handle output-handle" />{/if}
</div>

<style>
  .pipeline-node{display:grid;grid-template-columns:2.15rem 1fr;width:220px;min-height:82px;align-items:center;border:1px solid var(--border-strong);border-top:3px solid var(--node-transform);border-radius:10px;background:var(--bg-surface);padding:.72rem .78rem .58rem;box-shadow:0 4px 14px rgb(20 31 50 / 9%);text-align:left;user-select:none;transition:border-color .14s,box-shadow .14s,transform .14s}
  .pipeline-node:hover{border-color:#99a7b9;box-shadow:0 8px 22px rgb(20 31 50 / 13%)}
  .pipeline-node.selected{border-color:var(--accent);box-shadow:0 0 0 3px rgb(49 87 213 / 15%),0 10px 24px rgb(20 31 50 / 14%)}
  .pipeline-node.source{border-top-color:var(--node-source)}.pipeline-node.target{border-top-color:var(--node-target)}
  .node-icon{display:grid;width:1.9rem;height:1.9rem;place-items:center;border-radius:7px;background:#f2effb;color:var(--node-transform)}
  .source .node-icon{background:#e8f5fa;color:var(--node-source)}.target .node-icon{background:#e9f6f1;color:var(--node-target)}
  .identity{display:block;min-width:0;padding-left:.25rem}.identity strong{display:block;overflow:hidden;color:var(--text-primary);font-size:.8rem;font-weight:680;text-overflow:ellipsis;white-space:nowrap}.identity small{display:block;margin-top:.14rem;color:var(--text-muted);font-size:.56rem;font-weight:780;letter-spacing:.11em}
  .connector{grid-column:1/-1;margin:.58rem -.78rem -.58rem;padding:.4rem .78rem;border-top:1px solid var(--border-subtle);color:var(--text-muted);font-family:var(--font-mono);font-size:.62rem}
  :global(.pipeline-handle){width:12px!important;height:12px!important;border:2px solid #fff!important;background:#7d899a!important;box-shadow:0 0 0 1px #7d899a}
  :global(.source .pipeline-handle){background:var(--node-source)!important;box-shadow:0 0 0 1px var(--node-source)}
  :global(.target .pipeline-handle){background:var(--node-target)!important;box-shadow:0 0 0 1px var(--node-target)}
  :global(.pipeline-handle.connectingto),:global(.pipeline-handle.valid){box-shadow:0 0 0 4px rgb(49 87 213 / 20%)}
</style>
