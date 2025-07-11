import { Download, X, Smartphone } from 'lucide-react';
import React from 'react';

import { usePWA } from '../hooks/usePWA';
import './PWAInstallBanner.css';

const PWAInstallBanner: React.FC = () => {
  // Call hooks at the top level, outside of any try-catch
  const { showInstallPrompt, installApp, dismissInstallPrompt } = usePWA();

  if (!showInstallPrompt) {
    return null;
  }

  const handleInstall = async () => {
    try {
      const success = await installApp();
      if (success) {
        // Use console.log for development, could be replaced with proper logging
        console.log('PWA installed successfully');
      }
    } catch (error) {
      console.error('PWA installation failed:', error);
    }
  };

  const handleDismiss = () => {
    try {
      dismissInstallPrompt();
    } catch (error) {
      console.error('Error dismissing install prompt:', error);
    }
  };

  return (
    <div className="pwa-install-banner">
      <div className="pwa-banner-content">
        <div className="pwa-banner-icon">
          <Smartphone size={24} />
        </div>
        <div className="pwa-banner-text">
          <h3>Install Carolina&apos;s Diary</h3>
          <p>Get the full app experience on your device</p>
        </div>
        <div className="pwa-banner-actions">
          <button
            className="pwa-install-btn"
            onClick={handleInstall}
            aria-label="Install app"
          >
            <Download size={18} />
            Install
          </button>
          <button
            className="pwa-dismiss-btn"
            onClick={handleDismiss}
            aria-label="Dismiss install prompt"
          >
            <X size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default PWAInstallBanner;
