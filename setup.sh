#!/bin/bash

# Check and install required Python packages first
if [ -f /etc/fedora-release ]; then
    echo "Installing required Python packages..."
    sudo dnf install -y python3-libs python3-devel python3
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv || {
        echo "Failed to create virtual environment. Please ensure Python is properly installed."
        exit 1
    }
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg is not installed. Installing..."
    if [ -f /etc/fedora-release ]; then
        sudo dnf install -y ffmpeg
    elif [ -f /etc/debian_version ]; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    else
        echo "Please install ffmpeg manually for your distribution"
    fi
fi

# Check for portaudio development files
if [ -f /etc/fedora-release ]; then
    sudo dnf install -y portaudio-devel python3-devel
elif [ -f /etc/debian_version ]; then
    sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-dev
fi

echo "Setup complete! Run 'source venv/bin/activate' to activate the virtual environment" 