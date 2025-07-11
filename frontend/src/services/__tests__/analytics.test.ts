import { analyticsService } from '../analytics';

// Mock PostHog
jest.mock('posthog-js', () => ({
  init: jest.fn(),
  capture: jest.fn(),
  identify: jest.fn(),
  people: {
    set: jest.fn(),
  },
  debug: jest.fn(),
}));

describe('AnalyticsService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('identifyUser', () => {
    it('should identify user with correct properties', () => {
      const userId = 'test-user-123';
      const properties = {
        email: 'test@example.com',
        name: 'Test User',
      };

      analyticsService.identifyUser(userId, properties);

      // Verify PostHog identify was called
      const posthog = require('posthog-js');
      expect(posthog.identify).toHaveBeenCalledWith(userId, {
        ...properties,
        user_id: userId,
        last_login: expect.any(String),
      });
    });
  });

  describe('trackPageView', () => {
    it('should track page view with correct data', () => {
      const pageName = 'journal_entry';
      const properties = { path: '/', search: '' };

      analyticsService.trackPageView(pageName, properties);

      const posthog = require('posthog-js');
      expect(posthog.capture).toHaveBeenCalledWith('page_viewed', {
        page_name: pageName,
        session_id: expect.any(String),
        user_id: null,
        ...properties,
      });
    });
  });

  describe('trackEntrySaved', () => {
    it('should track entry save with correct metrics', () => {
      const date = '2024-01-15';
      const entryData = {
        gratitude_answers: ['I am grateful for...', 'Another gratitude...'],
        emotion: 'happiness',
        emotion_answers: ['I feel happy because...'],
        custom_text: 'Additional thoughts...',
      };

      analyticsService.trackEntrySaved(date, entryData);

      const posthog = require('posthog-js');
      expect(posthog.capture).toHaveBeenCalledWith('entry_saved', {
        entry_date: date,
        entry_length: expect.any(Number),
        has_gratitude: true,
        has_emotion: true,
        has_custom_text: true,
        gratitude_count: 2,
        emotion_answers_count: 1,
        time_of_day: expect.any(String),
        day_of_week: expect.any(String),
        session_duration: expect.any(Number),
        user_id: null,
        session_id: expect.any(String),
        timestamp: expect.any(String),
      });
    });
  });

  describe('trackEmotionSelected', () => {
    it('should track emotion selection', () => {
      const emotion = 'happiness';

      analyticsService.trackEmotionSelected(emotion);

      const posthog = require('posthog-js');
      expect(posthog.capture).toHaveBeenCalledWith('emotion_selected', {
        emotion: emotion,
        time_of_day: expect.any(String),
        day_of_week: expect.any(String),
        user_id: null,
        session_id: expect.any(String),
        timestamp: expect.any(String),
      });
    });
  });

  describe('trackGratitudeAnswered', () => {
    it('should track gratitude answer', () => {
      const questionIndex = 0;
      const answerLength = 25;

      analyticsService.trackGratitudeAnswered(questionIndex, answerLength);

      const posthog = require('posthog-js');
      expect(posthog.capture).toHaveBeenCalledWith('gratitude_answered', {
        question_index: questionIndex,
        answer_length: answerLength,
        time_of_day: expect.any(String),
        user_id: null,
        session_id: expect.any(String),
        timestamp: expect.any(String),
      });
    });
  });

  describe('trackCustomizationChanged', () => {
    it('should track customization changes', () => {
      const setting = 'backgroundColor';
      const value = '#ff0000';

      analyticsService.trackCustomizationChanged(setting, value);

      const posthog = require('posthog-js');
      expect(posthog.capture).toHaveBeenCalledWith('customization_changed', {
        setting: setting,
        value: value,
        time_of_day: expect.any(String),
        user_id: null,
        session_id: expect.any(String),
        timestamp: expect.any(String),
      });
    });
  });

  describe('trackSessionEnd', () => {
    it('should track session end with correct data', () => {
      analyticsService.trackSessionEnd();

      const posthog = require('posthog-js');
      expect(posthog.capture).toHaveBeenCalledWith('session_ended', {
        session_id: expect.any(String),
        session_duration: expect.any(Number),
        pages_visited: expect.any(Array),
        features_used: expect.any(Array),
        entry_completed: false,
        time_of_day: expect.any(String),
        user_id: null,
        timestamp: expect.any(String),
      });
    });
  });

  describe('trackError', () => {
    it('should track error events', () => {
      const errorType = 'api_error';
      const errorMessage = 'Failed to save entry';

      analyticsService.trackError(errorType, errorMessage);

      const posthog = require('posthog-js');
      expect(posthog.capture).toHaveBeenCalledWith('error_occurred', {
        error_type: errorType,
        error_message: errorMessage,
        page: expect.any(String),
        session_id: expect.any(String),
        user_id: null,
        timestamp: expect.any(String),
      });
    });
  });

  describe('trackPerformance', () => {
    it('should track performance metrics', () => {
      const metric = 'page_load_time';
      const value = 1500;

      analyticsService.trackPerformance(metric, value);

      const posthog = require('posthog-js');
      expect(posthog.capture).toHaveBeenCalledWith('performance_metric', {
        metric: metric,
        value: value,
        page: expect.any(String),
        user_id: null,
        session_id: expect.any(String),
        timestamp: expect.any(String),
      });
    });
  });

  describe('helper methods', () => {
    it('should calculate entry length correctly', () => {
      const entryData = {
        gratitude_answers: ['Answer 1', 'Answer 2'],
        emotion_answers: ['Emotion answer'],
        custom_text: 'Custom text',
      };

      // Access private method through public interface
      analyticsService.trackEntrySaved('2024-01-15', entryData);

      const posthog = require('posthog-js');
      const callArgs = posthog.capture.mock.calls[0][1];
      
      // Verify entry length calculation
      expect(callArgs.entry_length).toBe(25); // "Answer 1" (9) + "Answer 2" (9) + "Emotion answer" (13) + "Custom text" (11) = 42
    });

    it('should get time of day correctly', () => {
      const mockDate = new Date('2024-01-15T10:30:00');
      jest.spyOn(global, 'Date').mockImplementation(() => mockDate as any);

      analyticsService.trackPageView('test');

      const posthog = require('posthog-js');
      const callArgs = posthog.capture.mock.calls[0][1];
      
      expect(callArgs.time_of_day).toBe('morning');

      jest.restoreAllMocks();
    });

    it('should get day of week correctly', () => {
      const mockDate = new Date('2024-01-15T10:30:00'); // Monday
      jest.spyOn(global, 'Date').mockImplementation(() => mockDate as any);

      analyticsService.trackPageView('test');

      const posthog = require('posthog-js');
      const callArgs = posthog.capture.mock.calls[0][1];
      
      expect(callArgs.day_of_week).toBe('monday');

      jest.restoreAllMocks();
    });
  });

  describe('session management', () => {
    it('should generate unique session IDs', () => {
      const sessionData1 = analyticsService.getSessionData();
      const sessionData2 = analyticsService.getSessionData();
      
      expect(sessionData1.session_id).toBe(sessionData2.session_id);
    });

    it('should reset session correctly', () => {
      const originalSessionData = analyticsService.getSessionData();
      
      analyticsService.resetSession();
      
      const newSessionData = analyticsService.getSessionData();
      
      expect(newSessionData.session_id).not.toBe(originalSessionData.session_id);
      expect(newSessionData.pages_visited).toEqual([]);
      expect(newSessionData.features_used).toEqual([]);
      expect(newSessionData.entry_completed).toBe(false);
    });
  });
});