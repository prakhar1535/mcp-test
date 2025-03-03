#!/usr/bin/env python3
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Command:
    """Class for representing a parsed command"""
    type: str
    action: Dict[str, Any]
    description: str

class CommandParser:
    """Parse structured LLM responses into executable commands"""
    
    def __init__(self):
        """Initialize the command parser"""
        logger.info("Command Parser initialized")
    
    def parse(self, llm_response: Dict[str, Any]) -> List[Command]:
        """Parse an LLM response into a list of executable commands"""
        commands = []
        
        try:
            actions = llm_response.get('actions', [])
            
            for action in actions:
                cmd_type = action.get('type')
                description = action.get('description', 'No description provided')
                
                if cmd_type == 'command_line':
                    cmd = Command(
                        type='command_line',
                        action={'command': action.get('command', '')},
                        description=description
                    )
                    commands.append(cmd)
                
                elif cmd_type == 'gui_action':
                    cmd = Command(
                        type='gui_action',
                        action={
                            'action': action.get('action', ''),
                            'target': action.get('target', ''),
                            'coordinates': action.get('coordinates', [0, 0]),
                            'text': action.get('text', '')
                        },
                        description=description
                    )
                    commands.append(cmd)
                
                elif cmd_type == 'file_operation':
                    cmd = Command(
                        type='file_operation',
                        action={
                            'action': action.get('action', ''),
                            'path': action.get('path', ''),
                            'content': action.get('content', '')
                        },
                        description=description
                    )
                    commands.append(cmd)
                
                else:
                    logger.warning(f"Unknown command type: {cmd_type}")
            
            logger.info(f"Parsed {len(commands)} commands from LLM response")
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
        
        return commands 