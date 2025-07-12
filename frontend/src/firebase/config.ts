import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Firebase configuration
// Replace with your Firebase project configuration
function getRequiredEnvVar(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(
      `Missing required Firebase environment variable: ${name}\n` +
      'Please check your .env file and ensure all Firebase configuration variables are set.'
    );
  }
  return value;
}

const firebaseConfig = {
  apiKey: getRequiredEnvVar('REACT_APP_FIREBASE_API_KEY'),
  authDomain: getRequiredEnvVar('REACT_APP_FIREBASE_AUTH_DOMAIN'),
  projectId: getRequiredEnvVar('REACT_APP_FIREBASE_PROJECT_ID'),
  storageBucket: getRequiredEnvVar('REACT_APP_FIREBASE_STORAGE_BUCKET'),
  messagingSenderId: getRequiredEnvVar(
    'REACT_APP_FIREBASE_MESSAGING_SENDER_ID'
  ),
  appId: getRequiredEnvVar('REACT_APP_FIREBASE_APP_ID'),
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Cloud Firestore and get a reference to the service
export const db = getFirestore(app);

export default app;
