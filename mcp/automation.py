#!/usr/bin/env python3
import logging
import subprocess
import os
import sys
from typing import Dict, Any, List, Tuple
import pyautogui
import time

logger = logging.getLogger(__name__)

class SystemAutomation:
    """Execute system actions on the Ubuntu system"""
    
    def __init__(self):
        """Initialize the system automation module"""
        # Configure PyAutoGUI safety features
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.5  # Add pause between GUI actions
        
        # Capture screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"System Automation initialized (Screen: {self.screen_width}x{self.screen_height})")
    
    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """Execute a shell command and return stdout, stderr, and return code"""
        try:
            logger.info(f"Executing command: {command}")
            
            # Run the command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Get the outputs
            stdout, stderr = process.communicate()
            return_code = process.returncode
            
            logger.info(f"Command completed with return code: {return_code}")
            return stdout, stderr, return_code
            
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return "", str(e), 1
    
    def perform_gui_action(self, action: str, target: str = None, 
                          coordinates: List[int] = None, text: str = None) -> bool:
        """Perform a GUI action like clicking or typing"""
        try:
            logger.info(f"Performing GUI action: {action} on {target or coordinates}")
            
            # Default to current position if no coordinates provided
            if coordinates is None:
                coordinates = pyautogui.position()
            
            # Execute the requested action
            if action == 'click':
                x, y = coordinates
                if 0 <= x < self.screen_width and 0 <= y < self.screen_height:
                    pyautogui.click(x, y)
                else:
                    logger.warning(f"Coordinates {coordinates} out of screen bounds")
                    return False
            
            elif action == 'right_click':
                x, y = coordinates
                if 0 <= x < self.screen_width and 0 <= y < self.screen_height:
                    pyautogui.rightClick(x, y)
                else:
                    logger.warning(f"Coordinates {coordinates} out of screen bounds")
                    return False
            
            elif action == 'double_click':
                x, y = coordinates
                if 0 <= x < self.screen_width and 0 <= y < self.screen_height:
                    pyautogui.doubleClick(x, y)
                else:
                    logger.warning(f"Coordinates {coordinates} out of screen bounds")
                    return False
            
            elif action == 'type':
                if text:
                    pyautogui.typewrite(text)
                else:
                    logger.warning("Type action called with no text")
                    return False
            
            elif action == 'press':
                if text:
                    pyautogui.press(text)
                else:
                    logger.warning("Press action called with no key")
                    return False
            
            elif action == 'hotkey':
                if text and '+' in text:
                    keys = text.split('+')
                    pyautogui.hotkey(*keys)
                else:
                    logger.warning("Hotkey action called with invalid format")
                    return False
                    
            elif action == 'scroll':
                amount = int(text) if text else 10
                pyautogui.scroll(amount)
            
            else:
                logger.warning(f"Unknown GUI action: {action}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error performing GUI action '{action}': {e}")
            return False
    
    def file_operation(self, action: str, path: str, content: str = None) -> Tuple[bool, str]:
        """Perform a file operation like reading, writing, or deleting"""
        try:
            logger.info(f"Performing file operation: {action} on {path}")
            
            # Validate and normalize the path
            path = os.path.expanduser(path)  # Expand ~ to home directory
            
            # Check if the path is a placeholder
            if '/path/to/' in path or '/your/' in path:
                # Create files in the current directory instead
                original_path = path
                path = os.path.join(os.getcwd(), 'mcp_output', os.path.basename(path))
                logger.warning(f"Path appears to be a placeholder: {original_path}")
                logger.warning(f"Redirecting to: {path}")
            
            # Safety checks
            if not self._is_path_safe(path):
                return False, f"Path not allowed for safety reasons: {path}"
            
            if action == 'read':
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return True, f.read()
                else:
                    return False, f"File not found: {path}"
            
            elif action in ['write', 'append']:
                # Ensure directory exists
                directory = os.path.dirname(path)
                try:
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory, exist_ok=True)
                        logger.info(f"Created directory: {directory}")
                except PermissionError:
                    return False, f"Permission denied when creating directory: {directory}"
                
                # Write to file
                try:
                    mode = 'a' if action == 'append' else 'w'
                    with open(path, mode) as f:
                        f.write(content or '')
                    return True, f"Successfully wrote to {path}"
                except PermissionError:
                    return False, f"Permission denied when writing to file: {path}"
            
            elif action == 'delete':
                if os.path.exists(path):
                    try:
                        if os.path.isfile(path):
                            os.remove(path)
                        else:
                            import shutil
                            shutil.rmtree(path)
                        return True, f"Successfully deleted {path}"
                    except PermissionError:
                        return False, f"Permission denied when deleting: {path}"
                else:
                    return False, f"File not found: {path}"
            
            else:
                return False, f"Unknown file operation: {action}"
            
        except Exception as e:
            logger.error(f"Error performing file operation '{action}' on '{path}': {e}")
            return False, str(e)
    
    def _is_path_safe(self, path: str) -> bool:
        """Check if a path is safe to access"""
        # Get the restricted paths from config if available
        restricted_paths = getattr(self, 'restricted_paths', 
                                  ['/etc/passwd', '/etc/shadow', '/boot', '/etc/sudoers',
                                   '/etc/ssh', '/root', '/var/log/auth.log'])
        
        # Normalize path for comparison
        path = os.path.abspath(path)
        
        # Check against restricted paths
        for restricted in restricted_paths:
            restricted = os.path.abspath(restricted)
            if path == restricted or path.startswith(restricted + os.sep):
                logger.warning(f"Access to restricted path denied: {path}")
                return False
        
        return True
    
    def init_output_directory(self):
        """Initialize a safe output directory for MCP generated files"""
        output_dir = os.path.join(os.getcwd(), 'mcp_output')
        
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
            
            # Create a README to explain what this directory is for
            readme_path = os.path.join(output_dir, 'README.txt')
            if not os.path.exists(readme_path):
                with open(readme_path, 'w') as f:
                    f.write("This directory contains files created by the MCP tool.\n")
                    f.write("It's used when the tool needs to write to example or placeholder paths.\n")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize output directory: {e}")
            return False 