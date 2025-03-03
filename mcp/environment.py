#!/usr/bin/env python3
import os
import sys
import logging

logger = logging.getLogger(__name__)

def check_environment():
    """Check and report Python environment issues"""
    # Check for environment variables that might cause conflicts
    env_vars = {
        'PYTHONHOME': os.environ.get('PYTHONHOME'),
        'PYTHONPATH': os.environ.get('PYTHONPATH'),
        'VIRTUAL_ENV': os.environ.get('VIRTUAL_ENV')
    }
    
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    
    # Log environment variables
    for var, value in env_vars.items():
        if value:
            logger.info(f"{var} is set to: {value}")
    
    # Check if encodings module is accessible
    try:
        import encodings
        logger.info("Encodings module found successfully")
    except ImportError:
        logger.critical("Cannot import encodings module - critical Python environment issue")
        sys.stderr.write("""
ERROR: Python environment configuration issue detected!

Your PYTHONHOME environment variable is causing conflicts.
Try running the following command before starting the MCP tool:

unset PYTHONHOME PYTHONPATH
python -m pip install -e .

Or create a virtual environment:

python -m venv mcp_env
source mcp_env/bin/activate
pip install -e .
python main.py
""")
        return False
    
    return True

def fix_environment():
    """Attempt to fix common Python environment issues"""
    # Clear problematic environment variables
    if 'PYTHONHOME' in os.environ:
        logger.warning(f"Unsetting PYTHONHOME (was: {os.environ['PYTHONHOME']})")
        del os.environ['PYTHONHOME']
    
    # Add more fixes if needed
    return True 