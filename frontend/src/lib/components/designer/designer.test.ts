import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';
import { afterEach, describe, expect, it, vi } from 'vitest';
import NodePalette from './NodePalette.svelte';
import NodeInspector from './NodeInspector.svelte';
import type { ConnectorDefinition, PipelineDesignEdge, PipelineDesignNode } from '$lib/api/pipelines';

const nodes: PipelineDesignNode[] = [
  { id: 'source-1', type: 'SOURCE', label: 'PostgreSQL Orders', connectorKey: 'postgresql', positionX: 80, positionY: 90 },
  { id: 'transform-1', type: 'TRANSFORM', label: 'Clean Orders', connectorKey: null, positionX: 360, positionY: 90 },
  { id: 'target-1', type: 'TARGET', label: 'Warehouse', connectorKey: 'postgresql', positionX: 640, positionY: 90 },
];
const edges: PipelineDesignEdge[] = [{ id: 'edge-1', sourceNodeId: 'source-1', targetNodeId: 'transform-1' }];
const connectors: ConnectorDefinition[] = [{ key: 'postgresql', displayName: 'PostgreSQL', category: 'BOTH', description: 'Database', vendor: 'PostgreSQL Global Development Group', version: '1', availability: 'AVAILABLE', capabilities: ['READ', 'WRITE'] }];
afterEach(cleanup);

describe('Pipeline Designer components', () => {
  it('adds each authoring node type from the palette', async () => {
    const onadd = vi.fn();
    render(NodePalette, { readonly: false, onadd });
    await fireEvent.click(screen.getByRole('button', { name: /Source/ }));
    await fireEvent.click(screen.getByRole('button', { name: /Transform/ }));
    await fireEvent.click(screen.getByRole('button', { name: /Target/ }));
    expect(onadd.mock.calls.map(([type]) => type)).toEqual(['SOURCE', 'TRANSFORM', 'TARGET']);
  });

  it('edits and deletes through the node inspector', async () => {
    const onLabel = vi.fn(), onDeleteNode = vi.fn();
    render(NodeInspector, { node: nodes[0], selectedEdge: null, nodes, edges, pipelineName:'Customer Warehouse Load', pipelineState:'DRAFT', connectors, revision: 4, readonly: false, validation: null, onLabel, onConnector: vi.fn(), onDeleteNode, onDeleteEdge: vi.fn(), onDeleteEdgeById:vi.fn(), onConnect: vi.fn(), onSelectNode: vi.fn() });
    await fireEvent.input(screen.getByLabelText('Label'), { target: { value: 'Orders source' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Delete node' }));
    expect(onLabel).toHaveBeenCalledWith('Orders source');
    expect(onDeleteNode).toHaveBeenCalledOnce();
  });

  it('shows validation issues as selectable node guidance', async () => {
    const onSelectNode = vi.fn();
    render(NodeInspector, { node: null, selectedEdge: null, nodes, edges, pipelineName:'Customer Warehouse Load', pipelineState:'DRAFT', connectors, revision: 4, readonly: false, validation: { valid: false, issues: [{ code: 'TARGET_REQUIRED', message: 'Pipeline requires a Target', nodeId: 'target-1' }] }, onLabel: vi.fn(), onConnector: vi.fn(), onDeleteNode: vi.fn(), onDeleteEdge: vi.fn(), onDeleteEdgeById:vi.fn(), onConnect: vi.fn(), onSelectNode });
    await fireEvent.click(screen.getByRole('button', { name: 'Pipeline requires a Target' }));
    expect(onSelectNode).toHaveBeenCalledWith('target-1');
    expect(screen.getByText('1 issue')).toBeTruthy();
  });

  it('disables authoring actions in archived mode', () => {
    render(NodePalette, { readonly: true, onadd: vi.fn() });
    expect(screen.getByRole('button', { name: /Source/ }).hasAttribute('disabled')).toBe(true);
    expect(screen.getByText('This archived design is read only.')).toBeTruthy();
  });
});
