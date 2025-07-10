import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useSearchParams } from 'react-router-dom';
import './App.css';
import JournalEntry from './components/JournalEntry';
import AllEntries from './components/AllEntries';
import Header from './components/Header';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import PWAInstallBanner from './components/PWAInstallBanner';
import OfflineIndicator from './components/OfflineIndicator';
import { AuthProvider, useAuth } from './context/AuthContext';
import { apiService } from './services/api';

function JournalPage() {
  const [searchParams] = useSearchParams();
  const [currentDate, setCurrentDate] = useState(() => {
    const dateParam = searchParams.get('date');
    return dateParam ? new Date(dateParam) : new Date();
  });
  const { currentUser } = useAuth();

  // Register user when they first authenticate
  useEffect(() => {
    if (currentUser) {
      apiService.registerUser().catch(console.error);
    }
  }, [currentUser]);

  // Update date when URL parameter changes
  useEffect(() => {
    const dateParam = searchParams.get('date');
    if (dateParam) {
      setCurrentDate(new Date(dateParam));
    }
  }, [searchParams]);

  const handleDateChange = (newDate: Date) => {
    setCurrentDate(newDate);
    // Update URL parameter
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set('date', newDate.toISOString().split('T')[0]);
    window.history.replaceState({}, '', `${window.location.pathname}?${searchParams}`);
  };

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <JournalEntry 
          date={currentDate} 
          onDateChange={handleDateChange}
        />
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <PWAInstallBanner />
        <OfflineIndicator />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <JournalPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/entries"
            element={
              <ProtectedRoute>
                <div className="App">
                  <Header />
                  <main className="main-content">
                    <AllEntries />
                  </main>
                </div>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
