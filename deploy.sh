#!/bin/bash

# Resume Analyzer Deployment Script
# This script helps prepare your project for deployment

echo "🚀 Resume Analyzer Deployment Preparation"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "backend/app.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project structure verified"

# Check if .env files exist
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found"
    echo "   You'll need to set environment variables in Railway"
fi

# Check if requirements.txt exists
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: backend/requirements.txt not found"
    exit 1
fi

echo "✅ Backend requirements.txt found"

# Check if package.json exists
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: frontend/package.json not found"
    exit 1
fi

echo "✅ Frontend package.json found"

# Check if railway.json exists
if [ ! -f "railway.json" ]; then
    echo "❌ Error: railway.json not found"
    exit 1
fi

echo "✅ Railway configuration found"

# Check if config.py exists
if [ ! -f "backend/config.py" ]; then
    echo "❌ Error: backend/config.py not found"
    exit 1
fi

echo "✅ Backend configuration found"

echo ""
echo "🎉 Project is ready for deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Push your code to GitHub"
echo "2. Deploy backend to Railway:"
echo "   - Go to railway.app"
echo "   - Create new project from GitHub"
echo "   - Set root directory to 'backend'"
echo "   - Add PostgreSQL database"
echo "   - Set environment variables"
echo ""
echo "3. Deploy frontend to Vercel:"
echo "   - Go to vercel.com"
echo "   - Import project from GitHub"
echo "   - Set root directory to 'frontend'"
echo "   - Set environment variables"
echo ""
echo "4. Update frontend API URL in src/services/api.js"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "🔗 Useful URLs:"
echo "   - Railway: https://railway.app"
echo "   - Vercel: https://vercel.com"
echo "   - GitHub: https://github.com"
echo ""
echo "Good luck with your deployment! 🚀"
