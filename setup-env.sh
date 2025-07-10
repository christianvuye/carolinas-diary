#!/bin/bash

echo "🚀 Setting up Google OAuth for Carolina's Diary"
echo "================================================"
echo ""

# Check if .env files exist
if [ ! -f "frontend/.env" ]; then
    echo "📝 Creating frontend .env file..."
    cp frontend/.env.example frontend/.env
    echo "✅ Frontend .env file created"
    echo "⚠️  Please update frontend/.env with your Firebase configuration"
else
    echo "✅ Frontend .env file already exists"
fi

if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend .env file..."
    cp backend/.env.example backend/.env
    echo "✅ Backend .env file created"
    echo "⚠️  Please update backend/.env with your Firebase Admin SDK configuration"
else
    echo "✅ Backend .env file already exists"
fi

echo ""
echo "📋 Next steps:"
echo "1. Create a Firebase project at https://console.firebase.google.com/"
echo "2. Enable Google Authentication in Firebase Console"
echo "3. Get your Firebase configuration from Project Settings"
echo "4. Update frontend/.env with your Firebase config"
echo "5. Set up Firebase Admin SDK credentials"
echo "6. Update backend/.env with your credentials"
echo ""
echo "📖 See GOOGLE_AUTH_SETUP.md for detailed instructions"
echo ""
echo "🎯 To test the setup:"
echo "  cd backend && uvicorn main:app --reload"
echo "  cd frontend && npm start"