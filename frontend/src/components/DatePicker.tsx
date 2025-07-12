import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import React, { useState } from 'react';
import './DatePicker.css';

interface DatePickerProps {
  selectedDate: Date;
  onDateChange: (date: Date) => void;
}

const DatePicker: React.FC<DatePickerProps> = ({
  selectedDate,
  onDateChange,
}) => {
  const [showCalendar, setShowCalendar] = useState(false);
  const [viewDate, setViewDate] = useState(new Date(selectedDate));

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatShortDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const goToPreviousDay = () => {
    const prevDay = new Date(selectedDate);
    prevDay.setDate(prevDay.getDate() - 1);
    onDateChange(prevDay);
  };

  const goToNextDay = () => {
    const nextDay = new Date(selectedDate);
    nextDay.setDate(nextDay.getDate() + 1);
    onDateChange(nextDay);
  };

  const goToToday = () => {
    onDateChange(new Date());
    setShowCalendar(false);
  };

  const handleDateSelect = (date: Date) => {
    onDateChange(date);
    setShowCalendar(false);
  };

  const generateCalendarDays = () => {
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const days = [];
    const currentDate = new Date(startDate);

    for (let week = 0; week < 6; week++) {
      for (let day = 0; day < 7; day++) {
        const date = new Date(currentDate);
        const isCurrentMonth = date.getMonth() === month;
        const isSelected = date.toDateString() === selectedDate.toDateString();
        const isToday = date.toDateString() === new Date().toDateString();

        days.push({
          date,
          isCurrentMonth,
          isSelected,
          isToday,
          dayNumber: date.getDate(),
        });

        currentDate.setDate(currentDate.getDate() + 1);
      }
    }

    return days;
  };

  const goToPreviousMonth = () => {
    const prevMonth = new Date(viewDate);
    prevMonth.setMonth(prevMonth.getMonth() - 1);
    setViewDate(prevMonth);
  };

  const goToNextMonth = () => {
    const nextMonth = new Date(viewDate);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    setViewDate(nextMonth);
  };

  const monthNames = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];

  return (
    <div className="date-picker">
      <div className="date-navigation">
        <button
          className="nav-btn prev-btn"
          onClick={goToPreviousDay}
          title="Previous day"
        >
          <ChevronLeft size={16} />
        </button>

        <button
          className="current-date-btn"
          onClick={() => setShowCalendar(!showCalendar)}
          title="Select date"
        >
          <Calendar size={16} />
          <span className="date-text">{formatShortDate(selectedDate)}</span>
        </button>

        <button
          className="nav-btn next-btn"
          onClick={goToNextDay}
          title="Next day"
        >
          <ChevronRight size={16} />
        </button>
      </div>

      {showCalendar && (
        <div className="calendar-dropdown">
          <div className="calendar-header">
            <button className="calendar-nav-btn" onClick={goToPreviousMonth}>
              <ChevronLeft size={16} />
            </button>

            <span className="calendar-month-year">
              {monthNames[viewDate.getMonth()]} {viewDate.getFullYear()}
            </span>

            <button className="calendar-nav-btn" onClick={goToNextMonth}>
              <ChevronRight size={16} />
            </button>
          </div>

          <div className="calendar-weekdays">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="weekday">
                {day}
              </div>
            ))}
          </div>

          <div className="calendar-days">
            {generateCalendarDays().map((day, index) => (
              <button
                key={index}
                className={`calendar-day ${
                  day.isCurrentMonth ? 'current-month' : 'other-month'
                } ${day.isSelected ? 'selected' : ''} ${day.isToday ? 'today' : ''}`}
                onClick={() => handleDateSelect(day.date)}
              >
                {day.dayNumber}
              </button>
            ))}
          </div>

          <div className="calendar-footer">
            <button className="today-btn" onClick={goToToday}>
              Today
            </button>
          </div>
        </div>
      )}

      <div className="full-date-display">{formatDate(selectedDate)}</div>
    </div>
  );
};

export default DatePicker;
