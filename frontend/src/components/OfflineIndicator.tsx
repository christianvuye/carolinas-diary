import { WifiOff, Wifi } from 'lucide-react';
import React, { useState, useEffect } from 'react';

import { useOnlineStatus } from '../hooks/usePWA';
import './OfflineIndicator.css';

const OfflineIndicator: React.FC = () => {
  const isOnline = useOnlineStatus();
  const [showIndicator, setShowIndicator] = useState(false);

  useEffect(() => {
    if (!isOnline) {
      setShowIndicator(true);
    } else {
      // Show "back online" briefly, then hide
      if (showIndicator) {
        const timer = setTimeout(() => setShowIndicator(false), 3000);
        return () => clearTimeout(timer);
      }
    }
    return undefined;
  }, [isOnline, showIndicator]);

  if (!showIndicator) {
    return null;
  }

  return (
    <div className={`offline-indicator ${isOnline ? 'online' : 'offline'}`}>
      <div className="offline-content">
        {isOnline ? (
          <>
            <Wifi size={16} />
            <span>Back online! Your entries will sync.</span>
          </>
        ) : (
          <>
            <WifiOff size={16} />
            <span>You&apos;re offline. Your entries are saved locally.</span>
          </>
        )}
      </div>
    </div>
  );
};

export default OfflineIndicator;
