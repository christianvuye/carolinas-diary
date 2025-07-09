import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { firestoreService, JournalEntryFirestore } from '../services/firestore';
import { Calendar, Heart, Brain, BookOpen, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './AllEntries.css';

const AllEntries: React.FC = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [entries, setEntries] = useState<JournalEntryFirestore[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterEmotion, setFilterEmotion] = useState('');

  useEffect(() => {
    loadAllEntries();
  }, [currentUser]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadAllEntries = async () => {
    if (!currentUser) return;
    
    setLoading(true);
    try {
      const allEntries = await firestoreService.getAllJournalEntries(currentUser.uid);
      setEntries(allEntries);
    } catch (error) {
      console.error('Error loading entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatShortDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
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
      'doubt': '#8395a7'
    };
    return colorMap[emotion?.toLowerCase()] || '#ff6b9d';
  };

  const getPreviewText = (entry: JournalEntryFirestore) => {
    const gratitudeText = entry.gratitude_answers?.filter(answer => answer.trim()).join(' ') || '';
    const emotionText = entry.emotion_answers?.filter(answer => answer.trim()).join(' ') || '';
    const customText = entry.custom_text || '';
    
    const fullText = `${gratitudeText} ${emotionText} ${customText}`.trim();
    return fullText.length > 150 ? fullText.substring(0, 150) + '...' : fullText;
  };

  const handleEntryClick = (entry: JournalEntryFirestore) => {
    // Navigate to the specific date
    navigate(`/?date=${entry.date}`);
  };

  const filteredEntries = entries.filter(entry => {
    const matchesSearch = searchTerm === '' || 
      getPreviewText(entry).toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.emotion?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesEmotion = filterEmotion === '' || entry.emotion === filterEmotion;
    
    return matchesSearch && matchesEmotion;
  });

  const uniqueEmotions = Array.from(new Set(entries.map(entry => entry.emotion).filter(Boolean))) as string[];

  if (loading) {
    return (
      <div className="all-entries">
        <div className="entries-header">
          <h1>All Journal Entries</h1>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading your journal entries...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="all-entries">
      <div className="entries-header">
        <div className="header-content">
          <h1>All Journal Entries</h1>
          <p className="entries-count">{entries.length} entries found</p>
        </div>
        
        <div className="entries-filters">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search entries..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <select
            value={filterEmotion}
            onChange={(e) => setFilterEmotion(e.target.value)}
            className="emotion-filter"
          >
            <option value="">All Emotions</option>
            {uniqueEmotions.map(emotion => (
              <option key={emotion} value={emotion}>{emotion}</option>
            ))}
          </select>
        </div>
      </div>

      {filteredEntries.length === 0 ? (
        <div className="empty-state">
          <BookOpen size={48} />
          <h3>No entries found</h3>
          <p>
            {entries.length === 0 
              ? "Start your journaling journey by creating your first entry!"
              : "Try adjusting your search or filter criteria."
            }
          </p>
          <button 
            className="create-entry-btn"
            onClick={() => navigate('/')}
          >
            Create Entry
          </button>
        </div>
      ) : (
        <div className="entries-grid">
          {filteredEntries.map((entry) => (
            <div 
              key={entry.id} 
              className="entry-card"
              onClick={() => handleEntryClick(entry)}
            >
              <div className="entry-header">
                <div className="entry-date">
                  <Calendar size={16} />
                  <span className="date-text">{formatShortDate(entry.date)}</span>
                </div>
                {entry.emotion && (
                  <div 
                    className="entry-emotion"
                    style={{ backgroundColor: getEmotionColor(entry.emotion) }}
                  >
                    <Brain size={14} />
                    <span>{entry.emotion}</span>
                  </div>
                )}
              </div>
              
              <div className="entry-content">
                <div className="entry-full-date">
                  {formatDate(entry.date)}
                </div>
                
                {entry.gratitude_answers && entry.gratitude_answers.some(answer => answer.trim()) && (
                  <div className="entry-gratitude">
                    <Heart size={16} />
                    <span>
                      {entry.gratitude_answers.filter(answer => answer.trim()).length} gratitude notes
                    </span>
                  </div>
                )}
                
                <div className="entry-preview">
                  {getPreviewText(entry) || 'No content available'}
                </div>
              </div>
              
              <div className="entry-footer">
                <span className="entry-time">
                  {entry.updatedAt.toDate().toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AllEntries;