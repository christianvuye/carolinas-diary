import React, { useState, useEffect } from 'react';
import { apiService, VisualSettings } from '../services/api';
import GratitudeSection from './GratitudeSection';
import EmotionSection from './EmotionSection';
import CustomizationPanel from './CustomizationPanel';
import './JournalEntry.css';

interface JournalEntryProps {
  date: Date;
}

interface JournalData {
  id?: number;
  user_id?: number;
  date?: string;
  gratitude_answers: string[];
  emotion?: string | null;
  emotion_answers: string[];
  custom_text?: string | null;
  visual_settings?: VisualSettings | null;
  created_at?: string;
  updated_at?: string;
}

const JournalEntry: React.FC<JournalEntryProps> = ({ date }) => {
  const [journalData, setJournalData] = useState<JournalData>({
    gratitude_answers: ['', '', '', '', ''],
    emotion_answers: [],
    visual_settings: {
      backgroundColor: '#ffffff',
      textColor: '#333333',
      fontFamily: 'Arial, sans-serif',
      fontSize: '16px',
      stickers: []
    }
  });

  const [showCustomization, setShowCustomization] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [, setIsInitialized] = useState(false);

  useEffect(() => {
    loadJournalEntry();
  }, [date]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadJournalEntry = async () => {
    try {
      const dateStr = date.toISOString().split('T')[0];
      const response = await apiService.getJournalEntry(dateStr);
      setJournalData({
        ...response,
        gratitude_answers: response.gratitude_answers || ['', '', '', '', ''],
        emotion_answers: response.emotion_answers || [],
        visual_settings: response.visual_settings || {
          backgroundColor: '#ffffff',
          textColor: '#333333',
          fontFamily: 'Arial, sans-serif',
          fontSize: '16px',
          stickers: []
        }
      });
    } catch (error) {
      console.log('No existing entry for today, starting fresh');
    } finally {
      setIsInitialized(true);
    }
  };

  const saveJournalEntry = async () => {
    setIsLoading(true);
    try {
      const dataToSave = {
        ...journalData,
        date: date.toISOString().split('T')[0],
        gratitude_answers: journalData.gratitude_answers || ['', '', '', '', ''],
        emotion_answers: journalData.emotion_answers || [],
        visual_settings: journalData.visual_settings || {
          backgroundColor: '#ffffff',
          textColor: '#333333',
          fontFamily: 'Arial, sans-serif',
          fontSize: '16px',
          stickers: []
        }
      };
      await apiService.saveJournalEntry(dataToSave);
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 2000);
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
        ...settings 
      }
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
        <h2>Today's Journal Entry</h2>
        <div className="journal-actions">
          <button
            className="customize-btn"
            onClick={() => setShowCustomization(!showCustomization)}
          >
            🎨 Customize
          </button>
          <button
            className="save-btn"
            onClick={saveJournalEntry}
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : isSaved ? 'Saved!' : 'Save Entry'}
          </button>
        </div>
      </div>

      {showCustomization && (
        <CustomizationPanel
          visualSettings={journalData.visual_settings || {
            backgroundColor: '#ffffff',
            textColor: '#333333',
            fontFamily: 'Arial, sans-serif',
            fontSize: '16px',
            stickers: []
          }}
          onUpdateSettings={updateVisualSettings}
        />
      )}

      <div className="journal-content">
        <GratitudeSection
          answers={journalData.gratitude_answers || ['', '', '', '', '']}
          onUpdateAnswers={(answers) => updateJournalData({ gratitude_answers: answers })}
        />

        <EmotionSection
          selectedEmotion={journalData.emotion || ''}
          emotionAnswers={journalData.emotion_answers || []}
          onUpdateEmotion={(emotion) => updateJournalData({ emotion })}
          onUpdateAnswers={(answers) => updateJournalData({ emotion_answers: answers })}
        />

        <div className="custom-text-section">
          <h3>Additional Thoughts</h3>
          <textarea
            className="custom-text-area"
            value={journalData.custom_text || ''}
            onChange={(e) => updateJournalData({ custom_text: e.target.value })}
            placeholder="Write any additional thoughts, experiences, or reflections here..."
            rows={6}
          />
        </div>
      </div>

      <div className="stickers-container">
        {(journalData.visual_settings?.stickers || []).map((sticker) => (
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