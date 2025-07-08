import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import JournalEntry from './components/JournalEntry';
import Header from './components/Header';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './context/AuthContext';
import { apiService } from './services/api';

function MainApp() {
  const [currentDate] = useState(new Date());
  const { currentUser } = useAuth();

  // Register user when they first authenticate
  useEffect(() => {
    if (currentUser) {
      apiService.registerUser().catch(console.error);
    }
  }, [currentUser]);

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <JournalEntry date={currentDate} />
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainApp />
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
