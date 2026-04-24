import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import { GoogleOAuthProvider } from '@react-oauth/google'
import App from './App.jsx'
import { AuthProvider } from './contexts/AuthContext.jsx'
import { ThemeProvider } from './contexts/ThemeContext.jsx'
import './index.css'
import ReactGA from 'react-ga4'

// Initialize Google Analytics
const gaId = import.meta.env.VITE_GA_ID
if (gaId) {
    ReactGA.initialize(gaId)
    console.log('✅ Google Analytics initialized with ID:', gaId)
}

// Configure Axios Base URL
// In development, this uses the proxy (undefined/empty string -> relative path)
// In production, this uses the VITE_API_URL environment variable
const apiUrl = import.meta.env.VITE_API_URL;
console.log('Current API URL:', apiUrl); // Debug log
axios.defaults.baseURL = apiUrl || '';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID"

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <AuthProvider>
                <ThemeProvider>
                    <App />
                </ThemeProvider>
            </AuthProvider>
        </GoogleOAuthProvider>
    </React.StrictMode>,
)
