import { useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { analyticsService } from '../services/analytics';
import { useAuth } from '../context/AuthContext';

export const useAnalytics = () => {
  const location = useLocation();
  const { currentUser } = useAuth();

  // Track page views automatically
  useEffect(() => {
    const pageName = location.pathname === '/' ? 'journal_entry' : location.pathname.slice(1);
    analyticsService.trackPageView(pageName, {
      path: location.pathname,
      search: location.search,
    });
  }, [location]);

  // Track session end when component unmounts
  useEffect(() => {
    return () => {
      analyticsService.trackSessionEnd();
    };
  }, []);

  // Identify user when they log in
  useEffect(() => {
    if (currentUser) {
      analyticsService.identifyUser(currentUser.uid, {
        email: currentUser.email || undefined,
        name: currentUser.displayName || undefined,
        registration_date: currentUser.metadata?.creationTime || undefined,
      });
    }
  }, [currentUser]);

  const trackEntryStarted = useCallback((date: string) => {
    analyticsService.trackEntryStarted(date);
  }, []);

  const trackEntrySaved = useCallback((date: string, entryData: any) => {
    analyticsService.trackEntrySaved(date, entryData);
  }, []);

  const trackEntryLoaded = useCallback((date: string) => {
    analyticsService.trackEntryLoaded(date);
  }, []);

  const trackFeatureUsed = useCallback((featureName: string, properties?: Record<string, any>) => {
    analyticsService.trackFeatureUsed(featureName, properties);
  }, []);

  const trackEmotionSelected = useCallback((emotion: string) => {
    analyticsService.trackEmotionSelected(emotion);
  }, []);

  const trackGratitudeAnswered = useCallback((questionIndex: number, answerLength: number) => {
    analyticsService.trackGratitudeAnswered(questionIndex, answerLength);
  }, []);

  const trackCustomizationChanged = useCallback((setting: string, value: any) => {
    analyticsService.trackCustomizationChanged(setting, value);
  }, []);

  const trackError = useCallback((errorType: string, errorMessage: string) => {
    analyticsService.trackError(errorType, errorMessage);
  }, []);

  const trackPerformance = useCallback((metric: string, value: number) => {
    analyticsService.trackPerformance(metric, value);
  }, []);

  const trackEngagement = useCallback((metric: string, value: number) => {
    analyticsService.trackEngagement(metric, value);
  }, []);

  const setUserProperties = useCallback((properties: any) => {
    analyticsService.setUserProperties(properties);
  }, []);

  const incrementUserProperty = useCallback((property: string, value: number = 1) => {
    analyticsService.incrementUserProperty(property, value);
  }, []);

  return {
    trackEntryStarted,
    trackEntrySaved,
    trackEntryLoaded,
    trackFeatureUsed,
    trackEmotionSelected,
    trackGratitudeAnswered,
    trackCustomizationChanged,
    trackError,
    trackPerformance,
    trackEngagement,
    setUserProperties,
    incrementUserProperty,
  };
};