#!/bin/bash

# Unset problematic environment variables
unset PYTHONHOME PYTHONPATH

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Not running in a virtual environment."
    echo "For best results, create and activate a virtual environment:"
    echo "  python -m venv mcp_env"
    echo "  source mcp_env/bin/activate"
    echo "  pip install -e ."
    echo ""
    echo "Continuing with system Python..."
fi

# Run the MCP tool
python main.py "$@" 