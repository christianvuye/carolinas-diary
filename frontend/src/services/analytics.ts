import posthog from 'posthog-js';

// Initialize PostHog
const POSTHOG_API_KEY = process.env.REACT_APP_POSTHOG_API_KEY || 'phc_test_key';
const POSTHOG_HOST = process.env.REACT_APP_POSTHOG_HOST || 'https://app.posthog.com';

// Initialize PostHog
if (typeof window !== 'undefined') {
  posthog.init(POSTHOG_API_KEY, {
    api_host: POSTHOG_HOST,
    loaded: (posthog) => {
      if (process.env.NODE_ENV === 'development') {
        posthog.debug();
      }
    },
    capture_pageview: false, // We'll handle this manually
    capture_pageleave: true,
    autocapture: true,
    disable_session_recording: false,
    session_recording: {
      maskAllInputs: true,
      maskInputOptions: {
        password: true,
        email: true,
        tel: true,
      },
    },
  });
}

export interface AnalyticsEvent {
  event: string;
  properties?: Record<string, any>;
  userId?: string;
}

export interface UserProperties {
  user_id: string;
  email?: string;
  name?: string;
  registration_date?: string;
  last_login?: string;
  total_entries?: number;
  streak_days?: number;
  preferred_emotion?: string;
  average_entry_length?: number;
  time_of_day_preference?: string;
}

export interface SessionData {
  session_id: string;
  start_time: string;
  end_time?: string;
  duration?: number;
  pages_visited: string[];
  features_used: string[];
  entry_completed: boolean;
}

class AnalyticsService {
  private sessionStartTime: number;
  private sessionId: string;
  private currentUserId: string | null = null;
  private sessionData: SessionData;

  constructor() {
    this.sessionStartTime = Date.now();
    this.sessionId = this.generateSessionId();
    this.sessionData = {
      session_id: this.sessionId,
      start_time: new Date().toISOString(),
      pages_visited: [],
      features_used: [],
      entry_completed: false,
    };
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Initialize user tracking
  public identifyUser(userId: string, properties?: Partial<UserProperties>): void {
    this.currentUserId = userId;
    
    posthog.identify(userId, {
      ...properties,
      user_id: userId,
      last_login: new Date().toISOString(),
    });

    // Track user login
    this.trackEvent('user_logged_in', {
      user_id: userId,
      login_method: 'firebase',
      ...properties,
    });
  }

  // Track page views
  public trackPageView(pageName: string, properties?: Record<string, any>): void {
    this.sessionData.pages_visited.push(pageName);
    
    posthog.capture('page_viewed', {
      page_name: pageName,
      session_id: this.sessionId,
      user_id: this.currentUserId,
      ...properties,
    });
  }

  // Track journal entry events
  public trackEntryStarted(date: string, properties?: Record<string, any>): void {
    this.trackEvent('entry_started', {
      entry_date: date,
      time_of_day: this.getTimeOfDay(),
      day_of_week: this.getDayOfWeek(),
      ...properties,
    });
  }

  public trackEntrySaved(date: string, entryData: any, properties?: Record<string, any>): void {
    const entryLength = this.calculateEntryLength(entryData);
    const hasGratitude = entryData.gratitude_answers?.some((answer: string) => answer.trim().length > 0);
    const hasEmotion = !!entryData.emotion;
    const hasCustomText = !!entryData.custom_text?.trim();

    this.sessionData.entry_completed = true;

    this.trackEvent('entry_saved', {
      entry_date: date,
      entry_length: entryLength,
      has_gratitude: hasGratitude,
      has_emotion: hasEmotion,
      has_custom_text: hasCustomText,
      gratitude_count: entryData.gratitude_answers?.filter((answer: string) => answer.trim().length > 0).length || 0,
      emotion_answers_count: entryData.emotion_answers?.length || 0,
      time_of_day: this.getTimeOfDay(),
      day_of_week: this.getDayOfWeek(),
      session_duration: Date.now() - this.sessionStartTime,
      ...properties,
    });
  }

  public trackEntryLoaded(date: string, properties?: Record<string, any>): void {
    this.trackEvent('entry_loaded', {
      entry_date: date,
      time_of_day: this.getTimeOfDay(),
      day_of_week: this.getDayOfWeek(),
      ...properties,
    });
  }

  // Track feature usage
  public trackFeatureUsed(featureName: string, properties?: Record<string, any>): void {
    this.sessionData.features_used.push(featureName);
    
    this.trackEvent('feature_used', {
      feature_name: featureName,
      session_id: this.sessionId,
      time_of_day: this.getTimeOfDay(),
      ...properties,
    });
  }

  // Track emotion selection
  public trackEmotionSelected(emotion: string, properties?: Record<string, any>): void {
    this.trackEvent('emotion_selected', {
      emotion: emotion,
      time_of_day: this.getTimeOfDay(),
      day_of_week: this.getDayOfWeek(),
      ...properties,
    });
  }

  // Track gratitude answers
  public trackGratitudeAnswered(questionIndex: number, answerLength: number, properties?: Record<string, any>): void {
    this.trackEvent('gratitude_answered', {
      question_index: questionIndex,
      answer_length: answerLength,
      time_of_day: this.getTimeOfDay(),
      ...properties,
    });
  }

  // Track customization changes
  public trackCustomizationChanged(setting: string, value: any, properties?: Record<string, any>): void {
    this.trackEvent('customization_changed', {
      setting: setting,
      value: value,
      time_of_day: this.getTimeOfDay(),
      ...properties,
    });
  }

  // Track session end
  public trackSessionEnd(): void {
    const sessionDuration = Date.now() - this.sessionStartTime;
    this.sessionData.end_time = new Date().toISOString();
    this.sessionData.duration = sessionDuration;

    this.trackEvent('session_ended', {
      session_id: this.sessionId,
      session_duration: sessionDuration,
      pages_visited: this.sessionData.pages_visited,
      features_used: this.sessionData.features_used,
      entry_completed: this.sessionData.entry_completed,
      time_of_day: this.getTimeOfDay(),
    });
  }

  // Track user retention events
  public trackUserRetention(daysSinceRegistration: number, properties?: Record<string, any>): void {
    this.trackEvent('user_retention', {
      days_since_registration: daysSinceRegistration,
      retention_cohort: this.getRetentionCohort(daysSinceRegistration),
      ...properties,
    });
  }

  // Track daily/weekly/monthly active user events
  public trackActiveUser(period: 'daily' | 'weekly' | 'monthly', properties?: Record<string, any>): void {
    this.trackEvent('active_user', {
      period: period,
      date: new Date().toISOString().split('T')[0],
      ...properties,
    });
  }

  // Track entry completion rates
  public trackEntryCompletionRate(completed: boolean, totalEntries: number, properties?: Record<string, any>): void {
    this.trackEvent('entry_completion_rate', {
      completed: completed,
      total_entries: totalEntries,
      completion_rate: completed ? 100 : 0,
      time_of_day: this.getTimeOfDay(),
      day_of_week: this.getDayOfWeek(),
      ...properties,
    });
  }

  // Track user engagement metrics
  public trackEngagement(metric: string, value: number, properties?: Record<string, any>): void {
    this.trackEvent('user_engagement', {
      metric: metric,
      value: value,
      time_of_day: this.getTimeOfDay(),
      day_of_week: this.getDayOfWeek(),
      ...properties,
    });
  }

  // Track error events
  public trackError(errorType: string, errorMessage: string, properties?: Record<string, any>): void {
    this.trackEvent('error_occurred', {
      error_type: errorType,
      error_message: errorMessage,
      page: window.location.pathname,
      session_id: this.sessionId,
      ...properties,
    });
  }

  // Track performance metrics
  public trackPerformance(metric: string, value: number, properties?: Record<string, any>): void {
    this.trackEvent('performance_metric', {
      metric: metric,
      value: value,
      page: window.location.pathname,
      ...properties,
    });
  }

  // Helper methods
  private trackEvent(eventName: string, properties?: Record<string, any>): void {
    if (typeof window !== 'undefined' && posthog) {
      posthog.capture(eventName, {
        user_id: this.currentUserId,
        session_id: this.sessionId,
        timestamp: new Date().toISOString(),
        ...properties,
      });
    }
  }

  private getTimeOfDay(): string {
    const hour = new Date().getHours();
    if (hour < 6) return 'early_morning';
    if (hour < 12) return 'morning';
    if (hour < 17) return 'afternoon';
    if (hour < 21) return 'evening';
    return 'night';
  }

  private getDayOfWeek(): string {
    const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    return days[new Date().getDay()];
  }

  private getRetentionCohort(days: number): string {
    if (days <= 1) return 'day_1';
    if (days <= 7) return 'week_1';
    if (days <= 30) return 'month_1';
    if (days <= 90) return 'month_3';
    return 'month_6_plus';
  }

  private calculateEntryLength(entryData: any): number {
    let totalLength = 0;
    
    // Calculate gratitude answers length
    if (entryData.gratitude_answers) {
      totalLength += entryData.gratitude_answers.reduce((sum: number, answer: string) => sum + answer.length, 0);
    }
    
    // Calculate emotion answers length
    if (entryData.emotion_answers) {
      totalLength += entryData.emotion_answers.reduce((sum: number, answer: string) => sum + answer.length, 0);
    }
    
    // Add custom text length
    if (entryData.custom_text) {
      totalLength += entryData.custom_text.length;
    }
    
    return totalLength;
  }

  // Get current session data
  public getSessionData(): SessionData {
    return { ...this.sessionData };
  }

  // Reset session data
  public resetSession(): void {
    this.sessionStartTime = Date.now();
    this.sessionId = this.generateSessionId();
    this.sessionData = {
      session_id: this.sessionId,
      start_time: new Date().toISOString(),
      pages_visited: [],
      features_used: [],
      entry_completed: false,
    };
  }

  // Set user properties
  public setUserProperties(properties: Partial<UserProperties>): void {
    if (this.currentUserId) {
      posthog.people.set({
        ...properties,
        user_id: this.currentUserId,
      });
    }
  }

  // Increment user properties
  public incrementUserProperty(property: string, value: number = 1): void {
    if (this.currentUserId) {
      // Note: PostHog people.increment is not available in all versions
      // Using set with a simple increment approach
      posthog.people.set(property, value.toString());
    }
  }
}

// Create singleton instance
export const analyticsService = new AnalyticsService();

// Export PostHog instance for direct access if needed
export { posthog };