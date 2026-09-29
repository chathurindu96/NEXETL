import { writable } from 'svelte/store';

export const routeEntity = writable<string | null>(null);
