# Carolina's Diary 💕

A beautiful, personalized journaling web application designed specifically for Carolina. This app combines daily gratitude practice with emotional awareness and visual customization.

## Features

- **Daily Gratitude Practice**: 5 rotating questions to help cultivate gratitude
- **Emotion Tracking**: Select from 13 different emotions with tailored reflection questions
- **Inspirational Quotes**: Famous quotes related to your current emotion
- **Visual Customization**: Colors, fonts, and stickers (flowers, hearts, Barbie, Taylor Swift themes, etc.)
- **Persistent Storage**: All entries are saved in a database and accessible across devices
- **Responsive Design**: Works beautifully on all screen sizes

## Emotions Supported

- Anxiety
- Sadness
- Stress
- Excitement
- Anger
- Happiness
- Joy
- Feeling Overwhelmed
- Jealousy
- Fatigue
- Insecurity
- Doubt
- Catastrophic Thinking

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: SQLite
- **Frontend**: React with TypeScript
- **Styling**: Custom CSS with gradients and animations

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will start on `http://localhost:3000`

## Usage

1. **Start Your Day**: The app will show you today's date and 5 random gratitude questions
2. **Express Gratitude**: Answer the gratitude questions to start your day positively
3. **Check In With Emotions**: Select how you're feeling from the emotion buttons
4. **Reflect**: Answer the personalized questions related to your emotion
5. **Get Inspired**: Read the quote from a famous person related to your emotion
6. **Customize**: Use the customize button to change colors, fonts, and add stickers
7. **Save**: Click save to store your entry in the database

## Database

The app uses SQLite to store:
- Journal entries with dates
- Gratitude and emotion answers
- Visual customization settings
- Question banks for gratitude and emotions
- Inspirational quotes

## Customization Features

- **Colors**: 10 background colors and 10 text colors
- **Fonts**: 8 different font families
- **Font Sizes**: 6 different sizes
- **Stickers**: 30+ stickers including flowers, hearts, stars, and fun emojis

## Future Enhancements

- User authentication for multiple users
- Export entries to PDF
- Calendar view of past entries
- Mood tracking over time
- Mobile app version

---

Made with 💕 for Carolina