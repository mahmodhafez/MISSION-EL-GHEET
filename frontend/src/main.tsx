import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './app/App';
import { createDevClient } from './services/dev/devAdapter';
import { createHttpClient } from './services/http/httpAdapter';
import './styles/main.css';

// VITE_API_BASE set (e.g. /api/v1, proxied to the backend by `pnpm dev`) → HTTP adapter.
// Not set → the labelled dev adapter (real planner export for UH-001 only), for demos without a server.
const apiBase = import.meta.env.VITE_API_BASE as string | undefined;
const client = apiBase ? createHttpClient(apiBase) : createDevClient();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App client={client} />
  </StrictMode>,
);
