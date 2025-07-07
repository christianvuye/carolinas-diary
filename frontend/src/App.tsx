import React, { useState, useEffect } from 'react';
import './App.css';
import JournalEntry from './components/JournalEntry';
import Header from './components/Header';

function App() {
  const [currentDate, setCurrentDate] = useState(new Date());

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <JournalEntry date={currentDate} />
      </main>
    </div>
  );
}

export default App;
