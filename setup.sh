#!/bin/bash

echo "Setting up Campus IBN NMS Project..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p data

echo "Setup completed!"
echo "To run the project:"
echo "  source venv/bin/activate"
echo "  python main.py"