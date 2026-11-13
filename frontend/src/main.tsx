import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './app/App';
import { createDevClient } from './services/dev/devAdapter';
import './styles/main.css';

// Development build: the labelled dev adapter (real planner export for UH-001 only).
// The HTTP adapter for /api/v1 replaces it when the backend serves milestone 1.
const client = createDevClient();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App client={client} />
  </StrictMode>,
);
