import * as Sentry from '@sentry/react';

// Initialize Sentry
Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN || 'YOUR_SENTRY_DSN_HERE',
  
  // Performance Monitoring
  tracesSampleRate: 1.0, // Capture 100% of the transactions, adjust in production.
  
  // Session Replay
  replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
  replaysOnErrorSampleRate: 1.0, // If you're not already sampling the session, change the line to: replaysOnErrorSampleRate: 0.1 to sample 10% of sessions where an error occurs.
  
  // Environment
  environment: process.env.NODE_ENV || 'development',
  
  // Release version
  release: process.env.REACT_APP_VERSION || '1.0.0',
  
  // Enable debug mode in development
  debug: process.env.NODE_ENV === 'development',
  
  // Before send callback to filter out certain errors
  beforeSend(event, hint) {
    // Don't send errors from localhost in development
    if (process.env.NODE_ENV === 'development' && window.location.hostname === 'localhost') {
      return null;
    }
    return event;
  },
});

export default Sentry;