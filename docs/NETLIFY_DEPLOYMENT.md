# Netlify Deployment Guide for Carolina's Diary

## Current Status: ⚠️ **Not Ready** - Requires fixes

### Issues to fix before deploying:

1. **Missing Dependencies**
   ```bash
   cd frontend
   npm install firebase react-router-dom
   ```

2. **Environment Variables Setup**
   - Create `.env` file in `frontend/` directory with your Firebase config:
   ```env
   REACT_APP_FIREBASE_API_KEY=your_api_key_here
   REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   REACT_APP_FIREBASE_PROJECT_ID=your_project_id
   REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
   REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef123456
   REACT_APP_API_BASE_URL=https://your-backend-api.herokuapp.com
   ```

3. **Backend API Configuration**
   - Update `frontend/src/services/api.ts` to use environment variable:
   ```typescript
   const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
   ```

4. **Netlify Configuration**
   - Add `frontend/public/_redirects` file:
   ```
   /*    /index.html   200
   ```

5. **Update Page Metadata**
   - Update `frontend/public/index.html` title and description

6. **Backend Deployment**
   - Deploy FastAPI backend to Heroku, Railway, or similar
   - Update CORS settings to allow your Netlify domain

### Netlify Deployment Steps:

1. **Fix the issues above**
2. **Connect to Netlify:**
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`
3. **Add environment variables in Netlify dashboard**
4. **Deploy backend separately**

### Frontend-only deployment (without backend):
The current frontend will deploy but won't function without the backend API.
