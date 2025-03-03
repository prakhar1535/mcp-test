#!/usr/bin/env python3
import argparse
import os
import sys
import logging
from typing import Dict, Any

# Configure basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Check environment before imports that might fail
try:
    from mcp.environment import check_environment, fix_environment
    
    # Check and fix environment
    if not check_environment():
        if not fix_environment():
            logger.critical("Cannot fix Python environment issues automatically. Please see error messages above.")
            sys.exit(1)
except ImportError:
    # If we can't even import the environment module, provide basic guidance
    sys.stderr.write("ERROR: Cannot import environment checker. Try unsetting PYTHONHOME and PYTHONPATH variables.\n")
    sys.exit(1)

# Now try importing our modules
try:
    from mcp.interface import LLMInterface
    from mcp.parser import CommandParser
    from mcp.controller import ActionController
    from mcp.automation import SystemAutomation
    from mcp.display import FeedbackDisplay
except ImportError as e:
    logger.critical(f"Failed to import required modules: {e}")
    sys.stderr.write(f"ERROR: Failed to import required modules: {e}\nPlease ensure you've installed all dependencies with 'pip install -e .'\n")
    sys.exit(1)

class MCPTool:
    """Main class for the Model Context Protocol tool"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the MCP tool with configuration"""
        self.config = config
        
        # Initialize components
        self.llm = LLMInterface(config['llm'])
        self.parser = CommandParser()
        self.controller = ActionController()
        self.automation = SystemAutomation()
        
        # Set up safety configurations
        if 'safety' in config:
            self.automation.restricted_paths = config['safety'].get('restricted_paths', [])
        
        # Initialize output directory
        self.automation.init_output_directory()
        
        self.display = FeedbackDisplay()
        
        logger.info("MCP Tool initialized")
    
    def run(self):
        """Run the MCP tool main loop"""
        self.display.show_welcome()
        
        try:
            while True:
                # Get user input
                user_prompt = self.display.get_user_input()
                
                if user_prompt.lower() in ['exit', 'quit']:
                    break
                
                # Process through pipeline
                llm_response = self.llm.process_prompt(user_prompt)
                parsed_commands = self.parser.parse(llm_response)
                
                # Execute commands with real-time feedback
                for cmd in parsed_commands:
                    self.display.update_status(f"Executing: {cmd.description}")
                    result = self.controller.execute(cmd, self.automation)
                    self.display.show_result(result)
                
        except KeyboardInterrupt:
            logger.info("User interrupted the program")
        finally:
            self.display.show_exit_message()
            
def main():
    """Entry point for the MCP tool"""
    parser = argparse.ArgumentParser(description="MCP Tool - Control your computer with LLM prompts")
    parser.add_argument('--config', type=str, default='config.json', help='Path to configuration file')
    args = parser.parse_args()
    
    # Load configuration
    import json
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.critical(f"Failed to load configuration file: {e}")
        sys.stderr.write(f"ERROR: Failed to load configuration from {args.config}: {e}\n")
        sys.exit(1)
    
    # Initialize and run the tool
    mcp = MCPTool(config)
    mcp.run()

if __name__ == "__main__":
    main() 