#!/bin/bash
# Quick activation helper for dvdrental_live environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if venv exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$SCRIPT_DIR/venv"
    echo "✓ Virtual environment created"
fi

# Activate venv
source "$SCRIPT_DIR/venv/bin/activate"

echo "============================================"
echo "✓ dvdrental_live environment activated"
echo "============================================"
echo ""
echo "Python: $(python --version)"
echo "Location: $(which python)"
echo ""
echo "Available commands:"
echo "  • cd level_1_basic && python generator.py"
echo "  • cd level_3_master_simulation && python master_simulation.py"
echo "  • cd level_4_advanced_master && python run_advanced_simulation.py"
echo ""
echo "To deactivate: type 'deactivate'"
echo ""
