import React from 'react';
import { Heart, LogOut, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Header.css';

const Header: React.FC = () => {
  const { currentUser, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <Heart className="heart-icon" />
          <h1>Carolina's Diary</h1>
        </div>
        <div className="header-right">
          <div className="header-date">
            {new Date().toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
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