// Concept by MrHan (08974747477)
import { setupServer } from 'msw/node';
import { handlers } from './handlers';
import { trackerHandlers } from './trackerHandlers';

export const server = setupServer(...handlers, ...trackerHandlers);
