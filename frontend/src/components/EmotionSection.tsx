import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Brain, Quote } from 'lucide-react';
import { useAnalytics } from '../hooks/useAnalytics';
import './EmotionSection.css';

interface EmotionSectionProps {
  selectedEmotion?: string;
  emotionAnswers: string[];
  onUpdateEmotion: (emotion: string) => void;
  onUpdateAnswers: (answers: string[]) => void;
}

interface EmotionQuestion {
  id: number;
  question: string;
}

interface QuoteData {
  quote: string;
  author: string;
}

const EmotionSection: React.FC<EmotionSectionProps> = ({
  selectedEmotion,
  emotionAnswers,
  onUpdateEmotion,
  onUpdateAnswers
}) => {
  const analytics = useAnalytics();
  const [emotions, setEmotions] = useState<string[]>([]);
  const [questions, setQuestions] = useState<EmotionQuestion[]>([]);
  const [quote, setQuote] = useState<QuoteData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadEmotions();
  }, []);

  useEffect(() => {
    if (selectedEmotion) {
      loadEmotionQuestions();
      loadQuote();
    }
  }, [selectedEmotion]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadEmotions = async () => {
    try {
      const response = await apiService.getEmotions();
      setEmotions(response || []);
    } catch (error) {
      console.error('Error loading emotions:', error);
      // Fallback emotions when backend is not available
      setEmotions([
        'happiness',
        'sadness', 
        'anxiety',
        'excitement',
        'stress',
        'anger',
        'joy',
        'feeling overwhelmed',
        'fatigue',
        'insecurity'
      ]);
    }
  };

  const loadEmotionQuestions = async () => {
    if (!selectedEmotion) return;
    
    setIsLoading(true);
    try {
      const response = await apiService.getEmotionQuestions(selectedEmotion);
      setQuestions(response || []);
    } catch (error) {
      console.error('Error loading emotion questions:', error);
      // Fallback questions when backend is not available
      setQuestions([
        { id: 1, question: `What triggered your ${selectedEmotion} today?` },
        { id: 2, question: `How did this ${selectedEmotion} affect your day?` },
        { id: 3, question: `What would help you feel better right now?` }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadQuote = async () => {
    if (!selectedEmotion) return;
    
    try {
      const response = await apiService.getQuote(selectedEmotion);
      setQuote(response || null);
    } catch (error) {
      console.error('Error loading quote:', error);
    }
  };

  const handleEmotionSelect = (emotion: string) => {
    onUpdateEmotion(emotion);
    onUpdateAnswers([]);
    
    // Track emotion selection
    analytics.trackEmotionSelected(emotion);
  };

  const handleAnswerChange = (index: number, value: string) => {
    const newAnswers = [...(emotionAnswers || [])];
    newAnswers[index] = value;
    onUpdateAnswers(newAnswers);
  };

  const getEmotionColor = (emotion: string) => {
    const colorMap: { [key: string]: string } = {
      'anxiety': '#ff6b6b',
      'sadness': '#4ecdc4',
      'stress': '#ff9f43',
      'excitement': '#feca57',
      'anger': '#ff3838',
      'happiness': '#2ed573',
      'joy': '#ffa502',
      'feeling overwhelmed': '#ff6b9d',
      'jealousy': '#a55eea',
      'fatigue': '#778ca3',
      'insecurity': '#f8b500',
      'doubt': '#8395a7',
      'catastrophic thinking': '#ff6b6b'
    };
    return colorMap[emotion] || '#ff6b9d';
  };

  return (
    <div className="emotion-section">
      <div className="section-header">
        <Brain className="section-icon" />
        <h3>How Are You Feeling Today?</h3>
      </div>

      <div className="emotions-grid">
        {(emotions || []).map((emotion) => (
          <button
            key={emotion}
            className={`emotion-button ${selectedEmotion === emotion ? 'selected' : ''}`}
            style={{
              backgroundColor: selectedEmotion === emotion ? getEmotionColor(emotion) : 'transparent',
              borderColor: getEmotionColor(emotion),
              color: selectedEmotion === emotion ? 'white' : getEmotionColor(emotion)
            }}
            onClick={() => handleEmotionSelect(emotion)}
          >
            {emotion}
          </button>
        ))}
      </div>

      {selectedEmotion && (
        <div className="emotion-content">
          {quote && (
            <div className="quote-section">
              <Quote className="quote-icon" />
              <blockquote className="quote">
                <p>"{quote.quote}"</p>
                <cite>— {quote.author}</cite>
              </blockquote>
            </div>
          )}

          {isLoading ? (
            <div className="loading">Loading questions...</div>
          ) : (
            <div className="emotion-questions">
              <h4>Reflection Questions about {selectedEmotion}</h4>
              {(questions || []).map((question, index) => (
                <div key={question.id} className="question-item">
                  <label className="question-label">
                    {question.question}
                  </label>
                  <textarea
                    className="answer-input"
                    value={(emotionAnswers || [])[index] || ''}
                    onChange={(e) => handleAnswerChange(index, e.target.value)}
                    placeholder="Take your time to reflect and write your thoughts..."
                    rows={3}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EmotionSection;