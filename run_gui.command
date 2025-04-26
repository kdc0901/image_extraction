#!/bin/zsh

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    source venv/bin/activate
    PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"
else
    # If no virtual environment, try to use system Python3
    PYTHON_PATH=$(which python3)
    if [ -z "$PYTHON_PATH" ]; then
        echo "Error: Python3 not found. Please install Python3 or create a virtual environment."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Run the GUI application
"$PYTHON_PATH" -m src.gui.app

# Keep the terminal window open
read -p "Press Enter to close this window..." 