import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';
import { afterEach, describe, expect, it, vi } from 'vitest';
import NodePalette from './NodePalette.svelte';
import NodeInspector from './NodeInspector.svelte';
import type { ConnectionDefinition, NodeTypeDefinition, PipelineDesignEdge, PipelineDesignNode } from '$lib/api/pipelines';

const nodes: PipelineDesignNode[] = [
  { id: 'source-1', type: 'SOURCE', kind:'database_source', label: 'PostgreSQL Orders', connectorKey: 'postgresql',configurationVersion:1,configuration:{},inputSchema:[],outputSchema:[], positionX: 80, positionY: 90 },
  { id: 'transform-1', type: 'TRANSFORM',kind:'filter', label: 'Clean Orders', connectorKey: null,configurationVersion:1,configuration:{predicate:{}},inputSchema:[],outputSchema:[], positionX: 360, positionY: 90 },
  { id: 'target-1', type: 'TARGET',kind:'database_target', label: 'Warehouse', connectorKey: 'postgresql',configurationVersion:1,configuration:{},inputSchema:[],outputSchema:[], positionX: 640, positionY: 90 },
];
const edges: PipelineDesignEdge[] = [{ id: 'edge-1', sourceNodeId: 'source-1',sourcePort:'output', targetNodeId: 'transform-1',targetPort:'input' }];
const connections: ConnectionDefinition[] = [];
const nodeTypes:NodeTypeDefinition[]=[{key:'database_source',displayName:'Source',category:'SOURCE',description:'Source',icon:'database',inputs:[],outputs:[{key:'output',displayName:'Output',multiple:true}],configurationSchema:{},configurationDefaults:{},executorKey:'database_source',supportsPreview:true,supportsSchemaInference:true},{key:'filter',displayName:'Transform',category:'TRANSFORM',description:'Transform',icon:'transform',inputs:[{key:'input',displayName:'Input',multiple:false}],outputs:[{key:'output',displayName:'Output',multiple:true}],configurationSchema:{},configurationDefaults:{},executorKey:'filter',supportsPreview:true,supportsSchemaInference:true},{key:'database_target',displayName:'Target',category:'TARGET',description:'Target',icon:'target',inputs:[{key:'input',displayName:'Input',multiple:false}],outputs:[],configurationSchema:{},configurationDefaults:{},executorKey:'database_target',supportsPreview:false,supportsSchemaInference:true}];
afterEach(cleanup);

describe('Pipeline Designer components', () => {
  it('adds each authoring node type from the palette', async () => {
    const onadd = vi.fn();
    render(NodePalette, { readonly: false,nodeTypes, onadd });
    await fireEvent.click(screen.getByRole('button', { name: /Source/ }));
    await fireEvent.click(screen.getByRole('button', { name: /Transform/ }));
    await fireEvent.click(screen.getByRole('button', { name: /Target/ }));
    expect(onadd.mock.calls.map(([type]) => type)).toEqual(['database_source', 'filter', 'database_target']);
  });

  it('edits and deletes through the node inspector', async () => {
    const onLabel = vi.fn(), onDeleteNode = vi.fn();
    render(NodeInspector, { node: nodes[0], selectedEdge: null, nodes, edges, pipelineName:'Customer Warehouse Load', pipelineState:'DRAFT', connections, revision: 4, readonly: false, validation: null, onLabel,onConfiguration:vi.fn(),onSchema:vi.fn(), onConnector: vi.fn(), onDeleteNode, onDeleteEdge: vi.fn(), onDeleteEdgeById:vi.fn(), onConnect: vi.fn(), onSelectNode: vi.fn() });
    await fireEvent.input(screen.getByLabelText('Label'), { target: { value: 'Orders source' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Delete node' }));
    expect(onLabel).toHaveBeenCalledWith('Orders source');
    expect(onDeleteNode).toHaveBeenCalledOnce();
  });

  it('shows validation issues as selectable node guidance', async () => {
    const onSelectNode = vi.fn();
    render(NodeInspector, { node: null, selectedEdge: null, nodes, edges, pipelineName:'Customer Warehouse Load', pipelineState:'DRAFT', connections, revision: 4, readonly: false, validation: { valid: false, issues: [{ code: 'TARGET_REQUIRED', message: 'Pipeline requires a Target', nodeId: 'target-1' }] }, onLabel: vi.fn(),onConfiguration:vi.fn(),onSchema:vi.fn(), onConnector: vi.fn(), onDeleteNode: vi.fn(), onDeleteEdge: vi.fn(), onDeleteEdgeById:vi.fn(), onConnect: vi.fn(), onSelectNode });
    await fireEvent.click(screen.getByRole('button', { name: 'Pipeline requires a Target' }));
    expect(onSelectNode).toHaveBeenCalledWith('target-1');
    expect(screen.getByText('1 issue')).toBeTruthy();
  });

  it('disables authoring actions in archived mode', () => {
    render(NodePalette, { readonly: true,nodeTypes, onadd: vi.fn() });
    expect(screen.getByRole('button', { name: /Source/ }).hasAttribute('disabled')).toBe(true);
    expect(screen.getByText('This archived design is read only.')).toBeTruthy();
  });
});
