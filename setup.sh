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

# Activate virtual environment
source dvdrental_live/bin/activate

echo ""
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Setting up database..."
python generator.py

echo ""
echo "============================================"
echo "Setup complete!"
echo "============================================"
echo ""
echo "Database: dvdrental_live"
echo "You can now run 'python generator.py' to add more weeks of data"
echo ""
