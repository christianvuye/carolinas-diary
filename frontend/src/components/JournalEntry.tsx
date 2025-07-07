import React, { useState, useEffect } from 'react';
import axios from 'axios';
import GratitudeSection from './GratitudeSection';
import EmotionSection from './EmotionSection';
import CustomizationPanel from './CustomizationPanel';
import './JournalEntry.css';

interface JournalEntryProps {
  date: Date;
}

interface JournalData {
  id?: number;
  gratitude_answers: string[];
  emotion?: string;
  emotion_answers: string[];
  custom_text?: string;
  visual_settings: {
    backgroundColor: string;
    textColor: string;
    fontFamily: string;
    fontSize: string;
    stickers: Array<{
      id: string;
      type: string;
      position: { x: number; y: number };
    }>;
  };
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

  useEffect(() => {
    loadJournalEntry();
  }, [date]);

  const loadJournalEntry = async () => {
    try {
      const dateStr = date.toISOString().split('T')[0];
      const response = await axios.get(`http://localhost:8000/journal-entry/${dateStr}`);
      setJournalData(response.data);
    } catch (error) {
      console.log('No existing entry for today, starting fresh');
    }
  };

  const saveJournalEntry = async () => {
    setIsLoading(true);
    try {
      await axios.post('http://localhost:8000/journal-entry', journalData);
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

  const updateVisualSettings = (settings: Partial<JournalData['visual_settings']>) => {
    setJournalData(prev => ({
      ...prev,
      visual_settings: { ...prev.visual_settings, ...settings }
    }));
  };

  const journalStyle = {
    backgroundColor: journalData.visual_settings.backgroundColor,
    color: journalData.visual_settings.textColor,
    fontFamily: journalData.visual_settings.fontFamily,
    fontSize: journalData.visual_settings.fontSize,
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
          visualSettings={journalData.visual_settings}
          onUpdateSettings={updateVisualSettings}
        />
      )}

      <div className="journal-content">
        <GratitudeSection
          answers={journalData.gratitude_answers}
          onUpdateAnswers={(answers) => updateJournalData({ gratitude_answers: answers })}
        />

        <EmotionSection
          selectedEmotion={journalData.emotion}
          emotionAnswers={journalData.emotion_answers}
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
        {journalData.visual_settings.stickers.map((sticker) => (
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