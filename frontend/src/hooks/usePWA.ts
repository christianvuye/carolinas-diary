import { useState, useEffect } from 'react';
import { pwaInstallPrompt } from '../utils/serviceWorkerRegistration';

interface PWAState {
  isInstallable: boolean;
  isInstalled: boolean;
  showInstallPrompt: boolean;
}

export const usePWA = () => {
  const [state, setState] = useState<PWAState>({
    isInstallable: false,
    isInstalled: false,
    showInstallPrompt: false
  });

  useEffect(() => {
    // Check initial state
    setState({
      isInstallable: pwaInstallPrompt.isInstallable(),
      isInstalled: pwaInstallPrompt.isAppInstalled(),
      showInstallPrompt: false
    });

    // Listen for install prompt availability
    const handleInstallAvailable = () => {
      setState(prev => ({
        ...prev,
        isInstallable: true,
        showInstallPrompt: true
      }));
    };

    const handleInstallHidden = () => {
      setState(prev => ({
        ...prev,
        isInstallable: false,
        showInstallPrompt: false,
        isInstalled: true
      }));
    };

    window.addEventListener('pwa-install-available', handleInstallAvailable);
    window.addEventListener('pwa-install-hidden', handleInstallHidden);

    return () => {
      window.removeEventListener('pwa-install-available', handleInstallAvailable);
      window.removeEventListener('pwa-install-hidden', handleInstallHidden);
    };
  }, []);

  const installApp = async (): Promise<boolean> => {
    const success = await pwaInstallPrompt.promptInstall();
    if (success) {
      setState(prev => ({
        ...prev,
        isInstallable: false,
        showInstallPrompt: false,
        isInstalled: true
      }));
    }
    return success;
  };

  const dismissInstallPrompt = () => {
    setState(prev => ({
      ...prev,
      showInstallPrompt: false
    }));
  };

  return {
    ...state,
    installApp,
    dismissInstallPrompt
  };
};

// Hook for detecting if app is running as PWA
export const useIsStandalone = () => {
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    const checkStandalone = () => {
      const isStandaloneMode = 
        window.matchMedia('(display-mode: standalone)').matches ||
        (window.navigator as any).standalone === true ||
        document.referrer.includes('android-app://');
      
      setIsStandalone(isStandaloneMode);
    };

    checkStandalone();
    window.addEventListener('resize', checkStandalone);

    return () => {
      window.removeEventListener('resize', checkStandalone);
    };
  }, []);

  return isStandalone;
};

// Hook for online/offline status
export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
};