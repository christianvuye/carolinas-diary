import { Heart, LogOut, User, BookOpen, Edit3 } from 'lucide-react';
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';
import { logger } from '../services/logger';

import './Header.css';

const Header: React.FC = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      logger.error('Failed to logout', { error });
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <Heart className="heart-icon" />
          <h1>Carolina&apos;s Diary</h1>
        </div>
        <div className="header-right">
          {currentUser && (
            <nav className="header-nav">
              <button
                className={`nav-btn ${
                  location.pathname === '/' ? 'active' : ''
                }`}
                onClick={() => navigate('/')}
              >
                <Edit3 size={16} />
                Write
              </button>
              <button
                className={`nav-btn ${
                  location.pathname === '/entries' ? 'active' : ''
                }`}
                onClick={() => navigate('/entries')}
              >
                <BookOpen size={16} />
                All Entries
              </button>
            </nav>
          )}
          <div className="header-date">
            {new Date().toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </div>
          {currentUser && (
            <div className="user-menu">
              <div className="user-info">
                <User className="user-icon" />
                <span className="user-name">
                  {currentUser.displayName || currentUser.email}
                </span>
              </div>
              <button onClick={handleLogout} className="logout-button">
                <LogOut className="logout-icon" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
