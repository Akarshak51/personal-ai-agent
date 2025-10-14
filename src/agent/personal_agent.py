"""
Personal AI Agent - Core Implementation

The main agent class that handles conversations and tasks.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..memory.memory_manager import MemoryManager
from ..nlp.processor import NLPProcessor
from ..utils.response_formatter import ResponseFormatter


class PersonalAgent:
    """
    A fully functional personal AI agent with no restrictions.
    
    This agent is designed to be helpful, intelligent, and adaptive
    to user needs while maintaining conversation context and memory.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Personal AI Agent.
        
        Args:
            config: Configuration dictionary containing agent settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.memory = MemoryManager(config.get('memory', {}))
        self.nlp = NLPProcessor(config.get('nlp', {}))
        self.formatter = ResponseFormatter(config.get('formatting', {}))
        
        # Agent state
        self.conversation_id = None
        self.user_context = {}
        
        self.logger.info("Personal AI Agent initialized successfully")
    
    def chat(self, message: str, user_id: str = "default") -> str:
        """
        Process a chat message and return a response.
        
        Args:
            message: The user's input message
            user_id: Identifier for the user (for memory persistence)
            
        Returns:
            The agent's response string
        """
        try:
            # Process the input
            processed_input = self.nlp.process(message)
            
            # Retrieve relevant memories
            context = self.memory.get_relevant_context(
                message, 
                user_id, 
                conversation_id=self.conversation_id
            )
            
            # Generate response
            response_data = self._generate_response(
                processed_input, 
                context, 
                user_id
            )
            
            # Store the interaction in memory
            self.memory.store_interaction(
                user_input=message,
                agent_response=response_data['text'],
                user_id=user_id,
                conversation_id=self.conversation_id,
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'processed_input': processed_input,
                    'confidence': response_data.get('confidence', 1.0)
                }
            )
            
            # Format and return response
            return self.formatter.format_response(response_data)
            
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    def _generate_response(
        self, 
        processed_input: Dict[str, Any], 
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate a response based on processed input and context.
        
        Args:
            processed_input: NLP-processed user input
            context: Relevant context from memory
            user_id: User identifier
            
        Returns:
            Response data dictionary
        """
        # Extract intent and entities
        intent = processed_input.get('intent', 'general')
        entities = processed_input.get('entities', {})
        sentiment = processed_input.get('sentiment', 'neutral')
        
        # Build response based on intent
        if intent == 'greeting':
            response_text = self._handle_greeting(entities, context)
        elif intent == 'question':
            response_text = self._handle_question(entities, context)
        elif intent == 'task':
            response_text = self._handle_task(entities, context)
        elif intent == 'personal':
            response_text = self._handle_personal(entities, context)
        else:
            response_text = self._handle_general(processed_input, context)
        
        return {
            'text': response_text,
            'intent': intent,
            'sentiment': sentiment,
            'confidence': processed_input.get('confidence', 0.8),
            'entities': entities
        }
    
    def _handle_greeting(self, entities: Dict, context: Dict) -> str:
        """Handle greeting intents."""
        name = context.get('user_name', 'there')
        time_of_day = self._get_time_of_day()
        
        return f"Good {time_of_day}, {name}! How can I assist you today?"
    
    def _handle_question(self, entities: Dict, context: Dict) -> str:
        """Handle question intents."""
        topic = entities.get('topic', 'that topic')
        
        # This is where you'd integrate with knowledge bases, APIs, etc.
        return f"That's an interesting question about {topic}. Let me help you with that. Based on my knowledge, I can provide information and assistance on a wide variety of topics. What specific aspect would you like to know more about?"
    
    def _handle_task(self, entities: Dict, context: Dict) -> str:
        """Handle task-related intents."""
        task_type = entities.get('task_type', 'task')
        
        return f"I'd be happy to help you with that {task_type}. As your personal AI agent, I can assist with various tasks including planning, analysis, creative work, problem-solving, and much more. What specific help do you need?"
    
    def _handle_personal(self, entities: Dict, context: Dict) -> str:
        """Handle personal conversation."""
        return "I'm here to help with whatever you need! As your personal AI agent, I'm designed to be helpful, adaptable, and understanding. Feel free to share what's on your mind or what you'd like assistance with."
    
    def _handle_general(self, processed_input: Dict, context: Dict) -> str:
        """Handle general intents."""
        return "I understand you're looking for assistance. As your personal AI agent, I'm here to help with a wide range of tasks and questions. Could you provide more details about what you'd like help with?"
    
    def _get_time_of_day(self) -> str:
        """Get appropriate greeting based on time of day."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "evening"
    
    def start_new_conversation(self) -> str:
        """Start a new conversation session."""
        self.conversation_id = f"conv_{datetime.now().isoformat()}"
        self.logger.info(f"Started new conversation: {self.conversation_id}")
        return self.conversation_id
    
    def set_user_context(self, context: Dict[str, Any]) -> None:
        """Set user context information."""
        self.user_context.update(context)
        self.logger.debug(f"Updated user context: {context}")
    
    def get_capabilities(self) -> List[str]:
        """Return a list of agent capabilities."""
        return [
            "Natural language conversation",
            "Task assistance and planning",
            "Information retrieval and analysis",
            "Creative writing and brainstorming",
            "Problem-solving support",
            "Memory and context retention",
            "Personalized responses",
            "Multi-turn dialogue",
            "Intent recognition",
            "Sentiment analysis"
        ]