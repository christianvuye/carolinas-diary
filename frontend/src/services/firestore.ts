import {
  collection,
  doc,
  setDoc,
  getDoc,
  getDocs,
  query,
  where,
  orderBy,
  limit,
  Timestamp,
} from 'firebase/firestore';

import { db } from '../firebase/config';
import { logger } from './logger';

export interface JournalEntryFirestore {
  id?: string;
  userId: string;
  date: string;
  gratitude_answers: string[];
  emotion?: string | null;
  emotion_answers: string[];
  custom_text?: string | null;
  visual_settings?: {
    backgroundColor: string;
    textColor: string;
    fontFamily: string;
    fontSize: string;
    stickers: Array<{
      id: string;
      type: string;
      position: { x: number; y: number };
    }>;
  } | null;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export const firestoreService = {
  // Save or update a journal entry
  async saveJournalEntry(
    userId: string,
    date: string,
    entryData: Omit<
      JournalEntryFirestore,
      'id' | 'userId' | 'date' | 'createdAt' | 'updatedAt'
    >
  ): Promise<void> {
    logger.debug('Saving journal entry', { userId, date, entryData });

    const entryId = `${userId}_${date}`;
    const entryRef = doc(db, 'journal_entries', entryId);

    const now = Timestamp.now();

    // Check if entry exists to determine if this is an update
    const existingEntry = await getDoc(entryRef);

    const entryToSave: JournalEntryFirestore = {
      id: entryId,
      userId,
      date,
      ...entryData,
      createdAt: existingEntry.exists() ? existingEntry.data().createdAt : now,
      updatedAt: now,
    };

    logger.debug('Saving entry to Firestore', { entryToSave });
    await setDoc(entryRef, entryToSave);
    logger.info('Entry saved successfully');
  },

  // Get a specific journal entry by date
  async getJournalEntry(
    userId: string,
    date: string
  ): Promise<JournalEntryFirestore | null> {
    const entryId = `${userId}_${date}`;
    const entryRef = doc(db, 'journal_entries', entryId);
    const entrySnap = await getDoc(entryRef);

    if (entrySnap.exists()) {
      return entrySnap.data() as JournalEntryFirestore;
    }
    return null;
  },

  // Get all journal entries for a user
  async getAllJournalEntries(userId: string): Promise<JournalEntryFirestore[]> {
    const entriesRef = collection(db, 'journal_entries');
    const q = query(
      entriesRef,
      where('userId', '==', userId),
      orderBy('date', 'desc')
    );

    const querySnapshot = await getDocs(q);
    const entries: JournalEntryFirestore[] = [];

    querySnapshot.forEach(doc => {
      entries.push(doc.data() as JournalEntryFirestore);
    });

    return entries;
  },

  // Get journal entries for a specific month
  async getJournalEntriesForMonth(
    userId: string,
    year: number,
    month: number
  ): Promise<JournalEntryFirestore[]> {
    const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
    const endDate = `${year}-${String(month).padStart(2, '0')}-31`;

    const entriesRef = collection(db, 'journal_entries');
    const q = query(
      entriesRef,
      where('userId', '==', userId),
      where('date', '>=', startDate),
      where('date', '<=', endDate),
      orderBy('date', 'desc')
    );

    const querySnapshot = await getDocs(q);
    const entries: JournalEntryFirestore[] = [];

    querySnapshot.forEach(doc => {
      entries.push(doc.data() as JournalEntryFirestore);
    });

    return entries;
  },

  // Get recent journal entries (last N entries)
  async getRecentJournalEntries(
    userId: string,
    limitCount = 10
  ): Promise<JournalEntryFirestore[]> {
    logger.debug('Fetching recent entries for user', { userId, limitCount });

    const entriesRef = collection(db, 'journal_entries');
    const q = query(
      entriesRef,
      where('userId', '==', userId),
      orderBy('date', 'desc'),
      limit(limitCount)
    );

    const querySnapshot = await getDocs(q);
    const entries: JournalEntryFirestore[] = [];

    querySnapshot.forEach(doc => {
      const entry = doc.data() as JournalEntryFirestore;
      logger.debug('Found entry', { entry });
      entries.push(entry);
    });

    logger.debug('Total entries found', { count: entries.length });
    return entries;
  },
};
