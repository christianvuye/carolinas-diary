import axios from 'axios';

import { auth } from '../firebase/config';

import { logger } from './logger';

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authentication token
api.interceptors.request.use(
  async config => {
    const currentUser = auth.currentUser;
    if (currentUser) {
      const token = await currentUser.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      logger.error('Unauthorized access - redirecting to login');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface JournalEntry {
  id: number;
  user_id: number;
  date: string;
  gratitude_answers: string[];
  emotion: string | null;
  emotion_answers: string[];
  custom_text: string | null;
  visual_settings: VisualSettings | null;
  created_at: string;
  updated_at: string;
}

export interface JournalEntryCreate {
  gratitude_answers: string[];
  emotion?: string | null;
  emotion_answers: string[];
  custom_text?: string | null;
  visual_settings?: VisualSettings | null;
}

export interface UserPreferences {
  [key: string]: unknown;
}

export interface User {
  id: number;
  firebase_uid: string;
  email: string;
  name: string | null;
  picture: string | null;
  email_verified: boolean;
  preferences: UserPreferences;
  created_at: string;
  updated_at: string;
}

export interface EmotionQuestion {
  id: number;
  question: string;
}

export interface Quote {
  quote: string;
  author: string;
}

export interface VisualSettings {
  backgroundColor: string;
  textColor: string;
  fontFamily: string;
  fontSize: string;
  stickers: Array<{
    id: string;
    type: string;
    position: { x: number; y: number };
  }>;
}

// API methods
export const apiService = {
  // User endpoints
  registerUser: async (): Promise<User> => {
    const response = await api.post('/users/register');
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me');
    return response.data;
  },

  updateUser: async (userData: Partial<User>): Promise<User> => {
    const response = await api.put('/users/me', userData);
    return response.data;
  },

  // Journal endpoints
  createJournalEntry: async (
    entry: JournalEntryCreate
  ): Promise<JournalEntry> => {
    const response = await api.post('/journal-entry', entry);
    return response.data;
  },

  getJournalEntry: async (date: string): Promise<JournalEntry> => {
    const response = await api.get(`/journal-entry/${date}`);
    return response.data;
  },

  getAllJournalEntries: async (): Promise<JournalEntry[]> => {
    const response = await api.get('/journal-entries');
    return response.data;
  },

  // Other endpoints
  getGratitudeQuestions: async (): Promise<string[]> => {
    const response = await api.get('/gratitude-questions');
    return response.data;
  },

  getEmotionQuestions: async (emotion: string): Promise<EmotionQuestion[]> => {
    const response = await api.get(`/emotion-questions/${emotion}`);
    return response.data;
  },

  getQuote: async (emotion: string): Promise<Quote> => {
    const response = await api.get(`/quote/${emotion}`);
    return response.data;
  },

  getAvailableEmotions: async (): Promise<string[]> => {
    const response = await api.get('/emotions');
    return response.data;
  },

  getEmotions: async (): Promise<string[]> => {
    const response = await api.get('/emotions');
    return response.data;
  },

  saveJournalEntry: async (
    entry: JournalEntryCreate & { date?: string }
  ): Promise<JournalEntry> => {
    const response = await api.post('/journal-entry', entry);
    return response.data;
  },
};

export default api;
