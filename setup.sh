#!/bin/bash

# Setup script for DVD Rental Live Database
# This script sets up MySQL and generates initial data

set -e

echo "============================================"
echo "DVD Rental Live - Database Setup"
echo "============================================"

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "MySQL is not installed. Please install MySQL first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Setting up database..."
python level_1_basic/generator.py

echo ""
echo "============================================"
echo "Setup complete!"
echo "============================================"
echo ""
echo "Database: dvdrental_live"
echo "To activate the environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
