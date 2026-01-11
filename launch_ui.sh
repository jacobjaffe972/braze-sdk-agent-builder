#!/bin/bash
# Launch script for Braze SDK Landing Page Generator UI

# Set the working directory to the code directory
cd "$(dirname "$0")/code"

# Use the venv Python from braze-docs-mcp
PYTHON_BIN="../braze-docs-mcp/venv/bin/python"

# Check if venv exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Virtual environment not found at $PYTHON_BIN"
    echo "Please run: cd braze-docs-mcp && python3 -m venv venv"
    exit 1
fi

# Check if dependencies are installed
$PYTHON_BIN -c "import gradio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    $PYTHON_BIN -m pip install -q -r requirements.txt
fi

# Launch the UI
echo "Starting Braze SDK Landing Page Generator..."
echo "Access the UI at: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

$PYTHON_BIN -m braze_code_gen "$@"
