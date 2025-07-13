# Testing Guide: Multi-User Authentication

## 🚀 Quick Setup

### 1. Firebase Configuration

1. **Create Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Click "Create a project"
   - Follow setup wizard

2. **Enable Authentication**:
   - In Firebase Console → Authentication → Sign-in method
   - Enable "Email/Password" and "Google" providers

3. **Get Configuration**:
   - Project Settings → General → Your apps
   - Add web app and copy config

4. **Update Frontend Config**:
   ```bash
   # Copy the example file
   cp frontend/.env.example frontend/.env

   # Edit frontend/.env with your Firebase config
   REACT_APP_FIREBASE_API_KEY=your_actual_api_key
   REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   # ... etc
   ```

5. **Backend Service Account**:
   - Project Settings → Service accounts → Generate private key
   - Download JSON file and set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"
   ```

### 2. Database Migration

The database has been migrated to support multi-user. Your existing entries are preserved under a "Default User".

```bash
cd backend
python migrate_database.py  # Already done, but safe to run again
```

## 🧪 Testing Steps

### Backend Testing

1. **Start Backend Server**:
   ```bash
   cd backend
   source venv/bin/activate
   venv/bin/python main.py
   ```

2. **Test Endpoints** (without auth first):
   ```bash
   # Test public endpoints
   curl http://localhost:8000/
   curl http://localhost:8000/emotions
   curl http://localhost:8000/gratitude-questions
   ```

### Frontend Testing

1. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```
   Should open http://localhost:3000

2. **Test Authentication Flow**:
   - Should redirect to `/login` (no authentication)
   - Try creating account with email/password
   - Try Google sign-in
   - After login, should see main app with user menu in header

### Manual Test Scenarios

#### Scenario 1: New User Registration
1. Visit http://localhost:3000
2. Should redirect to login page
3. Click "Sign up" link
4. Fill form and submit
5. Should redirect to main app
6. User menu should show in header

#### Scenario 2: User Isolation
1. Create journal entry as User A
2. Logout
3. Create second account (User B)
4. Login as User B
5. Should see empty journal (not User A's entries)

#### Scenario 3: Data Persistence
1. Create journal entry
2. Logout and login again
3. Entry should persist for same user

#### Scenario 4: Multiple Users Same Date
1. User A creates entry for today
2. User B creates entry for today
3. Both should work (no unique constraint conflict)

## 🔧 Testing Without Firebase (Development)

If you want to test without setting up Firebase:

1. **Mock Authentication**:
   Create `backend/test_without_firebase.py`:
   ```python
   # Disable Firebase authentication for testing
   from fastapi import FastAPI, Depends
   from main import app, get_db

   # Mock user data
   mock_user = {
       "uid": "test_user_123",
       "email": "test@example.com",
       "name": "Test User"
   }

   # Override auth dependency
   def mock_get_current_user():
       return mock_user

   app.dependency_overrides[get_current_user] = mock_get_current_user

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

2. **Run Mock Server**:
   ```bash
   cd backend
   source venv/bin/activate
   python test_without_firebase.py
   ```

## 🐛 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: firebase_admin"**:
   ```bash
   cd backend
   source venv/bin/activate
   pip install firebase-admin
   ```

2. **"User not found" errors**:
   - Check that `/users/register` is called after login
   - Verify Firebase token is valid

3. **Database errors**:
   - Run migration script: `python migrate_database.py`
   - Check database permissions

4. **CORS errors**:
   - Backend allows `http://localhost:3000`
   - Check if frontend is running on different port

5. **Firebase config errors**:
   - Verify all environment variables are set
   - Check Firebase project settings

### Debug API Calls

Add logging to see what's happening:

```bash
# Backend logs
cd backend
tail -f debug.log

# Check API requests in browser dev tools
# Network tab → XHR → Check headers for Authorization: Bearer <token>
```

## ✅ Success Indicators

- ✅ Backend starts without errors
- ✅ Frontend loads at http://localhost:3000
- ✅ Redirects to login when not authenticated
- ✅ Can register/login successfully
- ✅ User menu appears in header after login
- ✅ Can create and save journal entries
- ✅ Different users see different entries
- ✅ Logout works and redirects to login

## 📊 Database Schema Verification

Check that migration worked:

```sql
-- Connect to database
sqlite3 backend/carolinas_diary.db

-- Verify schema
.schema users
.schema journal_entries

-- Check data
SELECT id, email, name FROM users;
SELECT id, user_id, date FROM journal_entries LIMIT 5;
```

Your app now supports multiple users with complete data isolation! 🎉
