import { describe, expect, it } from 'vitest';

import { pipelineErrorMessage, pipelineErrorState } from './pipelines';

describe('Pipeline Definition public API errors', () => {
  it.each([
    ['NEXETL_AUTHENTICATION_REQUIRED', 'authentication'],
    ['NEXETL_AUTHORIZATION_DENIED', 'authorization'],
    ['NEXETL_PIPELINE_DEFINITION_NOT_FOUND', 'not_found'],
    ['NEXETL_VALIDATION_FAILED', 'validation'],
    ['NEXETL_CSRF_REJECTED', 'csrf'],
    ['NEXETL_INTERNAL_ERROR', 'service'],
  ])('maps %s to the stable client state %s', (code, state) => {
    expect(pipelineErrorState({ code })).toBe(state);
  });

  it('does not display a server-provided error string', () => {
    expect(pipelineErrorMessage({ code: 'NEXETL_INTERNAL_ERROR', message: 'internal detail' }))
      .not.toContain('internal detail');
  });
});
