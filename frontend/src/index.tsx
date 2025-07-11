import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { register } from './utils/serviceWorkerRegistration';
import './sentry'; // Initialize Sentry
import * as Sentry from '@sentry/react';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<div>An error has occurred</div>}>
      <App />
    </Sentry.ErrorBoundary>
  </React.StrictMode>
);

// Register service worker for PWA functionality
register();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
