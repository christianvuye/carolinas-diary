import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Heart } from 'lucide-react';
import { useAnalytics } from '../hooks/useAnalytics';
import './GratitudeSection.css';

interface GratitudeSectionProps {
  answers: string[];
  onUpdateAnswers: (answers: string[]) => void;
}

const GratitudeSection: React.FC<GratitudeSectionProps> = ({ answers, onUpdateAnswers }) => {
  const analytics = useAnalytics();
  const [questions, setQuestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadGratitudeQuestions();
  }, []);

  const loadGratitudeQuestions = async () => {
    try {
      const response = await apiService.getGratitudeQuestions();
      setQuestions(response || []);
    } catch (error) {
      console.error('Error loading gratitude questions:', error);
      // Fallback questions when backend is not available
      setQuestions([
        'What made you smile today?',
        'Who are you grateful for and why?',
        'What is something beautiful you noticed today?',
        'What is a small victory you experienced today?',
        'What comfort are you grateful for today?'
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerChange = (index: number, value: string) => {
    const newAnswers = [...(answers || ['', '', '', '', ''])];
    newAnswers[index] = value;
    onUpdateAnswers(newAnswers);
    
    // Track gratitude answer
    if (value.trim().length > 0) {
      analytics.trackGratitudeAnswered(index, value.length);
    }
  };

  if (isLoading) {
    return (
      <div className="gratitude-section">
        <div className="section-header">
          <Heart className="section-icon" />
          <h3>Loading gratitude questions...</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="gratitude-section">
      <div className="section-header">
        <Heart className="section-icon" />
        <h3>5 Things I'm Grateful For Today</h3>
      </div>
      <div className="questions-container">
        {(questions || []).map((question, index) => (
          <div key={index} className="question-item">
            <label className="question-label">
              {index + 1}. {question}
            </label>
            <textarea
              className="answer-input"
              value={(answers || [])[index] || ''}
              onChange={(e) => handleAnswerChange(index, e.target.value)}
              placeholder="Write your answer here..."
              rows={2}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default GratitudeSection;