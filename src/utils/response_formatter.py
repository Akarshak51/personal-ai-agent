"""
Response formatting utilities for the Personal AI Agent.
"""

import logging
from typing import Dict, Any, Optional


class ResponseFormatter:
    """Formats agent responses based on configuration."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the response formatter."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.max_length = config.get('max_response_length', 2000)
        self.use_markdown = config.get('use_markdown', False)
        self.include_metadata = config.get('include_metadata', False)
        self.style = config.get('response_style', 'conversational')
        
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format response data into final response string.
        
        Args:
            response_data: Dictionary containing response information
            
        Returns:
            Formatted response string
        """
        text = response_data.get('text', '')
        
        # Truncate if too long
        if len(text) > self.max_length:
            text = text[:self.max_length - 3] + '...'
            
        # Apply formatting based on style
        if self.style == 'formal':
            text = self._apply_formal_formatting(text)
        elif self.style == 'casual':
            text = self._apply_casual_formatting(text)
        # 'conversational' is default, no special formatting needed
        
        # Add markdown formatting if enabled
        if self.use_markdown:
            text = self._apply_markdown_formatting(text, response_data)
            
        # Add metadata if enabled
        if self.include_metadata:
            text = self._add_metadata(text, response_data)
            
        return text.strip()
    
    def _apply_formal_formatting(self, text: str) -> str:
        """Apply formal formatting to text."""
        # Ensure text starts with capital letter
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
            
        # Ensure text ends with proper punctuation
        if text and text[-1] not in '.!?':
            text += '.'
            
        return text
    
    def _apply_casual_formatting(self, text: str) -> str:
        """Apply casual formatting to text."""
        # Add casual expressions occasionally
        casual_starters = ['Well, ', 'So, ', 'Actually, ', 'You know, ']
        
        # Simple logic to sometimes add casual starters
        if len(text) > 50 and not any(text.startswith(starter) for starter in casual_starters):
            if hash(text) % 3 == 0:  # Pseudo-random based on content
                text = casual_starters[hash(text) % len(casual_starters)] + text.lower()
                text = text[0].upper() + text[1:]  # Capitalize first letter
                
        return text
    
    def _apply_markdown_formatting(self, text: str, response_data: Dict[str, Any]) -> str:
        """Apply markdown formatting to text."""
        # Bold important terms based on intent
        intent = response_data.get('intent', '')
        
        if intent == 'task':
            # Bold action words
            import re
            text = re.sub(r'\b(help|assist|create|build|make)\b', r'**\\1**', text, flags=re.IGNORECASE)
            
        elif intent == 'question':
            # Italic question-related terms  
            import re
            text = re.sub(r'\b(question|answer|information|knowledge)\b', r'*\\1*', text, flags=re.IGNORECASE)
            
        return text
    
    def _add_metadata(self, text: str, response_data: Dict[str, Any]) -> str:
        """Add metadata to response."""
        metadata_parts = []
        
        intent = response_data.get('intent')
        if intent:
            metadata_parts.append(f"Intent: {intent}")
            
        confidence = response_data.get('confidence')
        if confidence is not None:
            metadata_parts.append(f"Confidence: {confidence:.2f}")
            
        sentiment = response_data.get('sentiment')
        if sentiment and sentiment != 'neutral':
            metadata_parts.append(f"Sentiment: {sentiment}")
            
        if metadata_parts:
            metadata_str = " | ".join(metadata_parts)
            text += f"\n\n*[{metadata_str}]*"
            
        return text
    
    def format_error(self, error_message: str, error_type: str = "Error") -> str:
        """
        Format error messages consistently.
        
        Args:
            error_message: The error message
            error_type: Type of error (Error, Warning, etc.)
            
        Returns:
            Formatted error message
        """
        if self.use_markdown:
            return f"**{error_type}**: {error_message}"
        else:
            return f"{error_type}: {error_message}"
    
    def format_list(self, items: list, title: Optional[str] = None) -> str:
        """
        Format a list of items.
        
        Args:
            items: List of items to format
            title: Optional title for the list
            
        Returns:
            Formatted list string
        """
        if not items:
            return ""
            
        result = ""
        if title:
            if self.use_markdown:
                result += f"**{title}:**\n"
            else:
                result += f"{title}:\n"
                
        if self.use_markdown:
            for item in items:
                result += f"- {item}\n"
        else:
            for i, item in enumerate(items, 1):
                result += f"{i}. {item}\n"
                
        return result.strip()
    
    def format_code(self, code: str, language: str = "") -> str:
        """
        Format code blocks.
        
        Args:
            code: Code to format
            language: Programming language for syntax highlighting
            
        Returns:
            Formatted code block
        """
        if self.use_markdown:
            return f"```{language}\n{code}\n```"
        else:
            lines = code.split('\n')
            return '\n'.join(f"    {line}" for line in lines)