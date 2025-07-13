// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock Firebase App
jest.mock('firebase/app', () => ({
  initializeApp: jest.fn(() => ({})),
}));

// Mock Firebase Auth functions
/**
 * Mocks Firebase authentication methods for testing purposes.
 * @example
 * const auth = getAuth();
 * auth.signInWithEmailAndPassword('email', 'password');
 * // Mocked authentication process returns void.
 * @param {void} - No arguments are required.
 * @returns {object} A mock Firebase auth object.
 * @description
 *   - The function creates jest mock functions for all Firebase auth methods.
 *   - Useful for testing components that rely on Firebase authentication without making actual API calls.
 *   - It returns an object that mimics the structure and methods of Firebase authentication.
 *   - Designed to be compatible with `@testing-library/jest-dom` and Jest environment setups.
 */
jest.mock('firebase/auth', () => ({
  getAuth: jest.fn(() => ({
    currentUser: null,
    onAuthStateChanged: jest.fn(),
    signInWithEmailAndPassword: jest.fn(),
    createUserWithEmailAndPassword: jest.fn(),
    signOut: jest.fn(),
    updateProfile: jest.fn(),
    signInWithPopup: jest.fn(),
  })),
  onAuthStateChanged: jest.fn(),
  signInWithEmailAndPassword: jest.fn(),
  createUserWithEmailAndPassword: jest.fn(),
  signOut: jest.fn(),
  updateProfile: jest.fn(),
  GoogleAuthProvider: jest.fn(),
  signInWithPopup: jest.fn(),
}));

// Mock Firebase Firestore functions
jest.mock('firebase/firestore', () => ({
  getFirestore: jest.fn(() => ({
    collection: jest.fn(),
    doc: jest.fn(),
    getDocs: jest.fn(),
    getDoc: jest.fn(),
    addDoc: jest.fn(),
    updateDoc: jest.fn(),
    deleteDoc: jest.fn(),
  })),
  collection: jest.fn(),
  doc: jest.fn(),
  getDocs: jest.fn(),
  getDoc: jest.fn(),
  addDoc: jest.fn(),
  updateDoc: jest.fn(),
  deleteDoc: jest.fn(),
  query: jest.fn(),
  where: jest.fn(),
  orderBy: jest.fn(),
  limit: jest.fn(),
  Timestamp: {
    now: jest.fn(),
    fromDate: jest.fn(),
  },
}));

// Mock Firebase config
jest.mock('./firebase/config', () => ({
  auth: {
    currentUser: null,
    onAuthStateChanged: jest.fn(),
    signInWithEmailAndPassword: jest.fn(),
    createUserWithEmailAndPassword: jest.fn(),
    signOut: jest.fn(),
    updateProfile: jest.fn(),
    signInWithPopup: jest.fn(),
  },
  db: {
    collection: jest.fn(),
    doc: jest.fn(),
    getDocs: jest.fn(),
    getDoc: jest.fn(),
    addDoc: jest.fn(),
    updateDoc: jest.fn(),
    deleteDoc: jest.fn(),
  },
  default: {},
}));
