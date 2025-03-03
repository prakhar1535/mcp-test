#!/usr/bin/env python3
import logging
from typing import Dict, Any
import time
import sys
import threading
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live

logger = logging.getLogger(__name__)

class FeedbackDisplay:
    """Display feedback and capture user input"""
    
    def __init__(self):
        """Initialize the feedback display"""
        self.console = Console()
        self.status_message = "Ready"
        self.command_history = []
        self.max_history = 10
        
        logger.info("Feedback Display initialized")
    
    def show_welcome(self):
        """Show the welcome message"""
        self.console.print(Panel.fit(
            "[bold green]MCP Tool - Control your computer with LLM prompts[/bold green]\n"
            "Type your instructions in natural language, or 'exit' to quit.",
            title="Welcome",
            border_style="green"
        ))
    
    def get_user_input(self) -> str:
        """Get input from the user"""
        self.console.print("\n[bold blue]What would you like me to do?[/bold blue]")
        user_input = input("> ")
        return user_input
    
    def update_status(self, message: str):
        """Update the status message"""
        self.status_message = message
        self.console.print(f"[yellow]Status:[/yellow] {message}")
    
    def show_result(self, result: Dict[str, Any]):
        """Show the result of a command execution"""
        # Add to history
        self.command_history.append(result)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        # Create a panel for the result
        if result['success']:
            title = f"[green]✓ {result['description']}[/green]"
        else:
            title = f"[red]✗ {result['description']}[/red]"
        
        content = []
        content.append(f"[bold]Type:[/bold] {result['type']}")
        
        if result['output']:
            content.append("\n[bold]Output:[/bold]")
            content.append(result['output'])
        
        if result['error']:
            content.append("\n[bold red]Error:[/bold red]")
            content.append(result['error'])
        
        panel = Panel("\n".join(content), title=title, border_style="blue")
        self.console.print(panel)
    
    def show_exit_message(self):
        """Show the exit message"""
        self.console.print(Panel.fit(
            "[bold]Thank you for using the MCP Tool![/bold]",
            title="Goodbye",
            border_style="green"
        )) 