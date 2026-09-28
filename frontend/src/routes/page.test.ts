import { describe, expect, it } from 'vitest';

import { load } from './+page';

describe('root navigation', () => {
  it('redirects to Pipeline Definition registration', () => {
    try {
      load();
    } catch (error) {
      expect(error).toMatchObject({ status: 307, location: '/pipelines/new' });
      return;
    }
    throw new Error('Expected a SvelteKit redirect');
  });
});
