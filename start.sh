#!/bin/bash

# Resume Analyzer Startup Script

echo "🚀 Starting Resume Analyzer System"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp backend/env_example.txt backend/.env
    echo "📝 Please edit backend/.env with your configuration"
    echo "   - Set your GEMINI_API_KEY"
    echo "   - Configure DATABASE_URL"
    echo "   - Set SECRET_KEY"
    echo ""
    echo "Press Enter when ready to continue..."
    read
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
cd backend
source venv/bin/activate

# Upgrade pip and install build tools first
echo "🔧 Upgrading pip and installing build tools..."
pip install --upgrade pip
pip install setuptools wheel

# Install dependencies
echo "📦 Installing project dependencies..."
pip install -r requirements.txt

cd ..

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Initialize database if needed
echo "🗄️  Initializing database..."
cd backend
source venv/bin/activate
python init_db.py
cd ..

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "To start the application:"
echo "1. Backend:  cd backend && source venv/bin/activate && python app.py"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "🌐 The application will be available at:"
echo "   - Frontend: http://localhost:3000"
  echo "   - Backend:  http://localhost:5001"
echo ""
echo "Happy analyzing! 🎉"
