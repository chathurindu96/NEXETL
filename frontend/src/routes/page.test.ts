import { describe, expect, it } from 'vitest';

import { load } from './+page';

describe('root navigation', () => {
  it('redirects to the authenticated workspace home', () => {
    try {
      load();
    } catch (error) {
      expect(error).toMatchObject({ status: 307, location: '/home' });
      return;
    }
    throw new Error('Expected a SvelteKit redirect');
  });
});
