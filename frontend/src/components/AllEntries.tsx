import { Calendar, Heart, Brain, BookOpen, Search } from 'lucide-react';
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';
import { firestoreService, JournalEntryFirestore } from '../services/firestore';
import { logger } from '../services/logger';
import './AllEntries.css';

// Global cache for entries to persist across component mounts
const entriesCache = new Map<string, JournalEntryFirestore[]>();

// Function to refresh cache when entries are updated
/**
 * Clears the journal entries cache for a specific user and triggers a UI update.
 * @example
 * refreshEntriesCache('user-123')
 * // Cache for user-123 is removed, and a UI update is triggered.
 * @param {string} userId - The ID of the user whose entries cache should be cleared.
 * @returns {void} No return value.
 * @description
 *   - Deletes the user's cached journal entries from the `entriesCache` Map.
 *   - Dispatches a `CustomEvent` named 'entriesUpdated' to notify the system of the cache update.
 *   - Intended to prompt a UI refresh wherever this cache influences the display of user's data.
 */
export const refreshEntriesCache = (userId: string) => {
  entriesCache.delete(userId);
  // Trigger a re-render by dispatching a custom event
  window.dispatchEvent(
    new CustomEvent('entriesUpdated', { detail: { userId } })
  );
};

const AllEntries: React.FC = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [entries, setEntries] = useState<JournalEntryFirestore[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterEmotion, setFilterEmotion] = useState('');

  useEffect(() => {
    if (!currentUser) return;

    // Use consistent user ID for development
    const userId = 'dev-user-123';

    // Check cache first for instant loading
    const cacheKey = userId;
    const cachedEntries = entriesCache.get(cacheKey);

    if (cachedEntries) {
      setEntries(cachedEntries);
      setLoading(false);
      // Still refresh in background
      loadAllEntries(true);
    } else {
      loadAllEntries(false);
    }

    // Listen for entry updates
    const handleEntriesUpdated = (event: CustomEvent) => {
      if (event.detail.userId === userId) {
        loadAllEntries(false);
      }
    };

    window.addEventListener(
      'entriesUpdated',
      handleEntriesUpdated as EventListener
    );

    return () => {
      window.removeEventListener(
        'entriesUpdated',
        handleEntriesUpdated as EventListener
      );
    };
  }, [currentUser]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadAllEntries = async (isBackgroundRefresh = false) => {
    if (!currentUser) return;

    const userId = 'dev-user-123'; // For development consistency

    if (!isBackgroundRefresh) {
      setLoading(true);
    }

    try {
      // Try to load from localStorage first for instant loading
      const allEntriesKey = `all_entries_${userId}`;
      const localEntries = localStorage.getItem(allEntriesKey);

      if (localEntries && !isBackgroundRefresh) {
        try {
          const parsedEntries = JSON.parse(localEntries);

          // Validate and fix entries data structure
          const validatedEntries = parsedEntries.map(
            (entry: Partial<JournalEntryFirestore>) => ({
              ...entry,
              updatedAt:
                typeof entry.updatedAt === 'string'
                  ? entry.updatedAt
                  : new Date().toISOString(),
              createdAt:
                typeof entry.createdAt === 'string'
                  ? entry.createdAt
                  : new Date().toISOString(),
            })
          );

          setEntries(validatedEntries);
          entriesCache.set(userId, validatedEntries);
          setLoading(false);

          // Load from Firestore in background to sync
          setTimeout(() => {
            loadFromFirestore(userId, true);
          }, 100);
          return;
        } catch (error) {
          // Clear invalid localStorage entries
          localStorage.removeItem(allEntriesKey);
        }
      }

      // If no localStorage entries, show empty state immediately and try Firestore quickly
      if (!localEntries && !isBackgroundRefresh) {
        setEntries([]);
        setLoading(false);

        // Try Firestore briefly in background
        setTimeout(() => {
          loadFromFirestore(userId, true);
        }, 100);
        return;
      }

      // Fallback to Firestore
      await loadFromFirestore(userId, isBackgroundRefresh);
    } catch (error) {
      logger.error('Error loading entries', { error });
      setLoading(false);
    }
  };

  const loadFromFirestore = async (
    userId: string,
    isBackgroundRefresh: boolean
  ) => {
    try {
      const allEntriesKey = `all_entries_${userId}`;

      // Load recent entries first for faster initial display
      const recentEntries = await firestoreService.getRecentJournalEntries(
        userId,
        50
      );

      if (recentEntries.length > 0) {
        setEntries(recentEntries);
        entriesCache.set(userId, recentEntries);

        // Update localStorage cache
        localStorage.setItem(allEntriesKey, JSON.stringify(recentEntries));
      }

      if (!isBackgroundRefresh) {
        setLoading(false);
      }

      // Then load all entries in the background if needed
      if (recentEntries.length === 50) {
        const allEntries = await firestoreService.getAllJournalEntries(userId);
        setEntries(allEntries);
        entriesCache.set(userId, allEntries);
        localStorage.setItem(allEntriesKey, JSON.stringify(allEntries));
      }
    } catch (error) {
      logger.error('Error loading from Firestore', { error });
      if (!isBackgroundRefresh) {
        setLoading(false);
      }
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatShortDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getEmotionColor = (emotion: string) => {
    const colorMap: { [key: string]: string } = {
      anxiety: '#ff6b6b',
      sadness: '#4ecdc4',
      stress: '#ff9f43',
      excitement: '#feca57',
      anger: '#ff3838',
      happiness: '#2ed573',
      joy: '#ffa502',
      'feeling overwhelmed': '#ff6b9d',
      jealousy: '#a55eea',
      fatigue: '#778ca3',
      insecurity: '#f8b500',
      doubt: '#8395a7',
    };
    return colorMap[emotion?.toLowerCase()] || '#ff6b9d';
  };

  const getPreviewText = (entry: JournalEntryFirestore) => {
    const gratitudeText =
      entry.gratitude_answers?.filter(answer => answer.trim()).join(' ') || '';
    const emotionText =
      entry.emotion_answers?.filter(answer => answer.trim()).join(' ') || '';
    const customText = entry.custom_text || '';

    const fullText = `${gratitudeText} ${emotionText} ${customText}`.trim();
    return fullText.length > 150
      ? fullText.substring(0, 150) + '...'
      : fullText;
  };

  const handleEntryClick = (entry: JournalEntryFirestore) => {
    // Navigate to the specific date
    navigate(`/?date=${entry.date}`);
  };

  const filteredEntries = entries.filter(entry => {
    const matchesSearch =
      searchTerm === '' ||
      getPreviewText(entry).toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.emotion?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesEmotion =
      filterEmotion === '' || entry.emotion === filterEmotion;

    return matchesSearch && matchesEmotion;
  });

  const uniqueEmotions = Array.from(
    new Set(entries.map(entry => entry.emotion).filter(Boolean))
  ) as string[];

  if (loading && entries.length === 0) {
    return (
      <div className="all-entries">
        <div className="entries-header">
          <h1>All Journal Entries</h1>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading entries...</p>
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
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            value={filterEmotion}
            onChange={e => setFilterEmotion(e.target.value)}
            className="emotion-filter"
          >
            <option value="">All Emotions</option>
            {uniqueEmotions.map(emotion => (
              <option key={emotion} value={emotion}>
                {emotion}
              </option>
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
              ? 'Start your journaling journey by creating your first entry!'
              : 'Try adjusting your search or filter criteria.'}
          </p>
          <button className="create-entry-btn" onClick={() => navigate('/')}>
            Create Entry
          </button>
        </div>
      ) : (
        <div className="entries-grid">
          {filteredEntries.map(entry => (
            <div
              key={entry.id}
              className="entry-card"
              onClick={() => handleEntryClick(entry)}
              onKeyDown={e => {
                if (e.key === 'Enter' || e.key === ' ') {
                  handleEntryClick(entry);
                }
              }}
              role="button"
              tabIndex={0}
            >
              <div className="entry-header">
                <div className="entry-date">
                  <Calendar size={16} />
                  <span className="date-text">
                    {formatShortDate(entry.date)}
                  </span>
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
                <div className="entry-full-date">{formatDate(entry.date)}</div>

                {entry.gratitude_answers?.some(answer => answer.trim()) && (
                  <div className="entry-gratitude">
                    <Heart size={16} />
                    <span>
                      {
                        entry.gratitude_answers.filter(answer => answer.trim())
                          .length
                      }{' '}
                      gratitude notes
                    </span>
                  </div>
                )}

                <div className="entry-preview">
                  {getPreviewText(entry) || 'No content available'}
                </div>
              </div>

              <div className="entry-footer">
                <span className="entry-time">
                  {(() => {
                    try {
                      if (typeof entry.updatedAt === 'string') {
                        return new Date(entry.updatedAt).toLocaleDateString();
                      } else if (
                        entry.updatedAt &&
                        typeof entry.updatedAt.toDate === 'function'
                      ) {
                        return entry.updatedAt.toDate().toLocaleDateString();
                      } else {
                        return new Date().toLocaleDateString();
                      }
                    } catch (error) {
                      logger.warn('Error formatting date', { error });
                      return new Date().toLocaleDateString();
                    }
                  })()}
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
