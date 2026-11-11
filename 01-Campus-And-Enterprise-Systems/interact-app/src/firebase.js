import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSy_your_gemini_api_key_here",
  authDomain: "intaract-9b396.firebaseapp.com",
  projectId: "intaract-9b396",
  storageBucket: "intaract-9b396.firebasestorage.app",
  messagingSenderId: "1072777863130",
  appId: "1:1072777863130:web:cc55b754b6229ccceeeae3"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);