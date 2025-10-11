#!/bin/bash
# Agent700 API CLI Setup Script
# This script sets up a Python virtual environment and installs dependencies

set -e  # Exit on any error

echo "🚀 Setting up Agent700 API CLI environment..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf venv
    else
        echo "✅ Using existing virtual environment"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    if [ -f ".env.example" ]; then
        echo "📋 Copying .env.example to .env..."
        cp .env.example .env
        echo "✅ Created .env file from template"
        echo "📝 Please edit .env with your actual credentials"
    else
        echo "❌ No .env.example file found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To use the Agent700 CLI:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Edit .env with your credentials"
echo "3. Run: python run_agent.py \"Your message here\""
echo ""
echo "To deactivate the virtual environment: deactivate"
