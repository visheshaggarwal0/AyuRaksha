/**
 * Firebase Service Configuration (Optional Auth & 5GB Cloud Storage)
 * 
 * To activate:
 * 1. Create a project on https://console.firebase.google.com
 * 2. Enable Firebase Auth (Google Sign-In) and Firebase Storage
 * 3. Add credentials to your .env file
 */

export const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyDummyKeyForDevelopment",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "ayuraksha-demo.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "ayuraksha-demo",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "ayuraksha-demo.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "1234567890",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:1234567890:web:abcdef"
};

export const isFirebaseConfigured = () => {
  return Boolean(import.meta.env.VITE_FIREBASE_API_KEY);
};
