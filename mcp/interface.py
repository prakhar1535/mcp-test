#!/usr/bin/env python3
import logging
from typing import Dict, Any, Optional
import requests
import json

logger = logging.getLogger(__name__)

class LLMInterface:
    """Interface for interacting with LLM APIs"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LLM interface with configuration"""
        self.config = config
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'gpt-4')
        self.api_url = config.get('api_url')
        self.provider = config.get('provider', 'openai')
        
        # System prompt to instruct the LLM how to respond
        self.system_prompt = """
        You are a computer control assistant that helps users operate their Ubuntu 22.04 system.
        Given a user request, respond ONLY with a JSON object containing specific actions to take.
        
        Your response must follow this format:
        {
            "actions": [
                {
                    "type": "command_line", "command": "actual terminal command", "description": "human readable description"
                },
                {
                    "type": "gui_action", "action": "click|type|scroll|etc", 
                    "target": "description of target",
                    "coordinates": [x, y], 
                    "text": "text to type if applicable",
                    "description": "human readable description"
                },
                {
                    "type": "file_operation", "action": "read|write|delete", 
                    "path": "path/to/file", 
                    "content": "content if applicable",
                    "description": "human readable description"
                }
            ],
            "reasoning": "Your thought process and explanation for the user"
        }
        
        IMPORTANT RULES:
        1. For file operations, use realistic paths within the user's home directory like "~/Documents/file.txt" or relative paths like "./file.txt"
        2. NEVER use paths starting with /path/to/ or other placeholder paths
        3. For writing or modifying files, prefer paths in the current directory or user's home directory
        4. Do not include any other text outside the JSON structure
        
        For complex operations, break them down into multiple sequential actions.
        """
        
        logger.info(f"LLM Interface initialized with provider: {self.provider}")
    
    def process_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """Process a user prompt through the LLM and return structured commands"""
        try:
            if self.provider == 'openai':
                return self._call_openai_api(user_prompt)
            elif self.provider == 'anthropic':
                return self._call_anthropic_api(user_prompt)
            elif self.provider == 'local':
                return self._call_local_model(user_prompt)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            return {"actions": [], "reasoning": f"Error: {str(e)}"}
    
    def _call_openai_api(self, user_prompt: str) -> Dict[str, Any]:
        """Call the OpenAI API with the user prompt"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.2
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse the JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM response: {content}")
            return {"actions": [], "reasoning": "Error: Could not parse LLM response"}
    
    # Similar methods for other providers...
    def _call_anthropic_api(self, user_prompt: str) -> Dict[str, Any]:
        """Call the Anthropic API with the user prompt"""
        # Implementation for Anthropic Claude
        pass
    
    def _call_local_model(self, user_prompt: str) -> Dict[str, Any]:
        """Call a locally hosted model with the user prompt"""
        # Implementation for local models
        pass 