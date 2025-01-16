#!/bin/bash

# Define the virtual environment path
VENV_PATH="./my_venv"  # Or any other path

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
  python3 -m venv "$VENV_PATH"
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Install rembg (only if not already installed, improve with pip freeze)
pip freeze | grep -q "rembg" || pip install rembg

# Run your Python script
python3 main.py

# Deactivate the virtual environment (optional, but good practice)
deactivate
