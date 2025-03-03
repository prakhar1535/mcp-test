#!/usr/bin/env python3
import logging
from typing import Dict, Any
from .parser import Command
from .automation import SystemAutomation

logger = logging.getLogger(__name__)

class ActionController:
    """Control the execution of parsed commands"""
    
    def __init__(self):
        """Initialize the action controller"""
        logger.info("Action Controller initialized")
    
    def execute(self, command: Command, automation: SystemAutomation) -> Dict[str, Any]:
        """Execute a parsed command using the automation module"""
        result = {
            'success': False,
            'description': command.description,
            'type': command.type,
            'output': '',
            'error': ''
        }
        
        try:
            if command.type == 'command_line':
                stdout, stderr, return_code = automation.execute_command(command.action['command'])
                result['success'] = (return_code == 0)
                result['output'] = stdout
                result['error'] = stderr
                
            elif command.type == 'gui_action':
                action_success = automation.perform_gui_action(
                    action=command.action['action'],
                    target=command.action.get('target'),
                    coordinates=command.action.get('coordinates'),
                    text=command.action.get('text')
                )
                result['success'] = action_success
                if not action_success:
                    result['error'] = "Failed to perform GUI action"
                
            elif command.type == 'file_operation':
                file_success, file_result = automation.file_operation(
                    action=command.action['action'],
                    path=command.action['path'],
                    content=command.action.get('content')
                )
                result['success'] = file_success
                if file_success:
                    result['output'] = file_result
                else:
                    result['error'] = file_result
            
            else:
                result['error'] = f"Unknown command type: {command.type}"
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            result['error'] = str(e)
        
        return result 