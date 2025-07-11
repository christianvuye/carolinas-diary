import React, { useEffect, useState } from 'react';

import { useAuth } from '../context/AuthContext';
import { VisualSettings, apiService } from '../services/api';
import { firestoreService } from '../services/firestore';

import { refreshEntriesCache } from './AllEntries';
import CustomizationPanel from './CustomizationPanel';
import DatePicker from './DatePicker';
import EmotionSection from './EmotionSection';
import GratitudeSection from './GratitudeSection';
import './JournalEntry.css';

interface JournalEntryProps {
  date: Date;
  onDateChange: (date: Date) => void;
}

interface JournalData {
  id?: number;
  user_id?: number;
  date?: string;
  gratitude_answers: string[];
  emotion?: string | null | undefined;
  emotion_answers: string[];
  custom_text?: string | null | undefined;
  visual_settings?: VisualSettings | null | undefined;
  created_at?: string;
  updated_at?: string;
}

const JournalEntry: React.FC<JournalEntryProps> = ({ date, onDateChange }) => {
  const { currentUser } = useAuth();
  const [journalData, setJournalData] = useState<JournalData>({
    gratitude_answers: ['', '', '', '', ''],
    emotion_answers: [],
    visual_settings: {
      backgroundColor: '#ffffff',
      textColor: '#333333',
      fontFamily: 'Arial, sans-serif',
      fontSize: '16px',
      stickers: [],
    },
  });

  const [showCustomization, setShowCustomization] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
  const [, setIsInitialized] = useState(false);

  useEffect(() => {
    loadJournalEntry();
  }, [date]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadJournalEntry = async () => {
    if (!currentUser) return;

    try {
      const dateStr = date.toISOString().split('T')[0] || date.toISOString();
      const userId = 'dev-user-123'; // For development consistency

      // Try to load from localStorage first for instant loading
      const localStorageKey = `journal_${userId}_${dateStr}`;
      const localEntry = localStorage.getItem(localStorageKey);

      if (localEntry) {
        const parsedEntry = JSON.parse(localEntry);
        setJournalData({
          gratitude_answers: parsedEntry.gratitude_answers || [
            '',
            '',
            '',
            '',
            '',
          ],
          emotion: parsedEntry.emotion || null,
          emotion_answers: parsedEntry.emotion_answers || [],
          custom_text: parsedEntry.custom_text || null,
          visual_settings: parsedEntry.visual_settings || {
            backgroundColor: '#ffffff',
            textColor: '#333333',
            fontFamily: 'Arial, sans-serif',
            fontSize: '16px',
            stickers: [],
          },
        });
        setIsInitialized(true);
        return; // Exit early if we have local data
      }

      // Try to load from Firestore as fallback
      const firestoreEntry = await firestoreService.getJournalEntry(
        userId,
        dateStr
      );

      if (firestoreEntry) {
        setJournalData({
          gratitude_answers: firestoreEntry.gratitude_answers || [
            '',
            '',
            '',
            '',
            '',
          ],
          emotion: firestoreEntry.emotion || null,
          emotion_answers: firestoreEntry.emotion_answers || [],
          custom_text: firestoreEntry.custom_text || null,
          visual_settings: firestoreEntry.visual_settings || {
            backgroundColor: '#ffffff',
            textColor: '#333333',
            fontFamily: 'Arial, sans-serif',
            fontSize: '16px',
            stickers: [],
          },
        });
      } else {
        // Fallback to API if no Firestore entry exists
        try {
          const response = await apiService.getJournalEntry(dateStr);
          setJournalData({
            ...response,
            gratitude_answers: response.gratitude_answers || [
              '',
              '',
              '',
              '',
              '',
            ],
            emotion: response.emotion || null,
            emotion_answers: response.emotion_answers || [],
            custom_text: response.custom_text || null,
            visual_settings: response.visual_settings || {
              backgroundColor: '#ffffff',
              textColor: '#333333',
              fontFamily: 'Arial, sans-serif',
              fontSize: '16px',
              stickers: [],
            },
          });
        } catch (apiError) {
          // No existing entry found, starting fresh
        }
      }
    } catch (error) {
      console.error('Error loading journal entry:', error);
    } finally {
      setIsInitialized(true);
    }
  };

  const saveJournalEntry = async () => {
    if (!currentUser) return;

    setIsLoading(true);
    try {
      const dateStr = date.toISOString().split('T')[0] || date.toISOString();
      const dataToSave = {
        gratitude_answers: journalData.gratitude_answers || [
          '',
          '',
          '',
          '',
          '',
        ],
        emotion: journalData.emotion || null,
        emotion_answers: journalData.emotion_answers || [],
        custom_text: journalData.custom_text || null,
        visual_settings: journalData.visual_settings || {
          backgroundColor: '#ffffff',
          textColor: '#333333',
          fontFamily: 'Arial, sans-serif',
          fontSize: '16px',
          stickers: [],
        },
      };

      // Use consistent user ID for development
      const userId = 'dev-user-123'; // For development consistency

      // Save to localStorage immediately for instant performance
      const localStorageKey = `journal_${userId}_${dateStr}`;
      localStorage.setItem(
        localStorageKey,
        JSON.stringify({
          ...dataToSave,
          date: dateStr,
          userId,
          savedAt: new Date().toISOString(),
        })
      );

      // Update all entries cache in localStorage
      const allEntriesKey = `all_entries_${userId}`;
      const existingEntries = JSON.parse(
        localStorage.getItem(allEntriesKey) || '[]'
      );
      const entryIndex = existingEntries.findIndex(
        (entry: { date: string }) => entry.date === dateStr
      );

      const now = new Date();
      const entryToCache = {
        id: `${userId}_${dateStr}`,
        userId,
        date: dateStr,
        ...dataToSave,
        createdAt:
          entryIndex === -1
            ? now.toISOString()
            : existingEntries[entryIndex].createdAt,
        updatedAt: now.toISOString(),
      };

      if (entryIndex === -1) {
        existingEntries.unshift(entryToCache);
      } else {
        existingEntries[entryIndex] = entryToCache;
      }

      localStorage.setItem(allEntriesKey, JSON.stringify(existingEntries));

      // Try to save to Firestore in background (don't await)
      firestoreService
        .saveJournalEntry(userId, dateStr, dataToSave)
        .catch(() => {
          // Firestore save failed, but localStorage succeeded
        });

      // Also try to save to API as backup (don't await)
      apiService
        .saveJournalEntry({
          ...dataToSave,
          date: dateStr,
        })
        .catch(() => {
          // API save failed, but localStorage succeeded
        });

      setIsSaved(true);
      setShowPostSaveOptions(true);
      setTimeout(() => {
        setIsSaved(false);
        setShowPostSaveOptions(false);
      }, 5000);

      // Refresh entries cache to show updated data
      refreshEntriesCache(userId);
    } catch (error) {
      console.error('Error saving journal entry:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateJournalData = (updates: Partial<JournalData>) => {
    setJournalData(prev => ({ ...prev, ...updates }));
  };

  const updateVisualSettings = (settings: Partial<VisualSettings>) => {
    setJournalData(prev => ({
      ...prev,
      visual_settings: {
        ...prev.visual_settings,
        backgroundColor: '#ffffff',
        textColor: '#333333',
        fontFamily: 'Arial, sans-serif',
        fontSize: '16px',
        stickers: [],
        ...settings,
      },
    }));
  };

  const journalStyle = {
    backgroundColor: journalData.visual_settings?.backgroundColor || '#ffffff',
    color: journalData.visual_settings?.textColor || '#333333',
    fontFamily: journalData.visual_settings?.fontFamily || 'Arial, sans-serif',
    fontSize: journalData.visual_settings?.fontSize || '16px',
  };

  return (
    <div className="journal-entry" style={journalStyle}>
      <div className="journal-header">
        <div className="journal-title-section">
          <h2>Journal Entry</h2>
          <DatePicker selectedDate={date} onDateChange={onDateChange} />
        </div>
        <div className="journal-actions">
          <button
            className="customize-btn"
            onClick={() => setShowCustomization(!showCustomization)}
          >
            🎨 Customize
          </button>
        </div>
      </div>

      {showCustomization && (
        <CustomizationPanel
          visualSettings={
            journalData.visual_settings || {
              backgroundColor: '#ffffff',
              textColor: '#333333',
              fontFamily: 'Arial, sans-serif',
              fontSize: '16px',
              stickers: [],
            }
          }
          onUpdateSettings={updateVisualSettings}
        />
      )}

      <div className="journal-content">
        <GratitudeSection
          answers={journalData.gratitude_answers || ['', '', '', '', '']}
          onUpdateAnswers={answers =>
            updateJournalData({ gratitude_answers: answers })
          }
        />

        <EmotionSection
          selectedEmotion={journalData.emotion || ''}
          emotionAnswers={journalData.emotion_answers || []}
          onUpdateEmotion={emotion => updateJournalData({ emotion })}
          onUpdateAnswers={answers =>
            updateJournalData({ emotion_answers: answers })
          }
        />

        <div className="custom-text-section">
          <h3>Additional Thoughts</h3>
          <textarea
            className="custom-text-area"
            value={journalData.custom_text || ''}
            onChange={e => updateJournalData({ custom_text: e.target.value })}
            placeholder="Write any additional thoughts, experiences, or reflections here..."
            rows={6}
          />
        </div>
      </div>

      <div className="journal-footer">
        {!showPostSaveOptions ? (
          <button
            className={`save-btn ${isLoading ? 'saving' : ''} ${isSaved ? 'saved' : ''}`}
            onClick={saveJournalEntry}
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : isSaved ? '✓ Saved!' : 'Save Entry'}
          </button>
        ) : (
          <div className="post-save-options">
            <p className="save-success-message">✓ Entry saved successfully!</p>
            <div className="post-save-buttons">
              <button
                className="continue-editing-btn"
                onClick={() => setShowPostSaveOptions(false)}
              >
                Continue Editing
              </button>
              <button
                className="new-entry-btn"
                onClick={() => {
                  const today = new Date();
                  onDateChange(today);
                  setShowPostSaveOptions(false);
                }}
              >
                Create New Entry
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="stickers-container">
        {(journalData.visual_settings?.stickers || []).map(sticker => (
          <div
            key={sticker.id}
            className="sticker"
            style={{
              position: 'absolute',
              left: sticker.position.x,
              top: sticker.position.y,
            }}
          >
            {sticker.type}
          </div>
        ))}
      </div>
    </div>
  );
};

export default JournalEntry;
