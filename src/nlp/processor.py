"""
Natural Language Processing Module

Handles intent recognition, entity extraction, and sentiment analysis.
"""

import logging
import re
from typing import Dict, List, Any, Optional


class NLPProcessor:
    """Basic NLP processor for understanding user input."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the NLP processor."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Intent patterns (basic rule-based system)
        self.intent_patterns = {
            'greeting': [
                r'\b(hello|hi|hey|good\s+(morning|afternoon|evening)|greetings)\b',
                r'\bhowdy\b',
                r'\bwhat\'?s\s+up\b'
            ],
            'question': [
                r'\b(what|how|why|when|where|who|which)\b',
                r'\?',
                r'\bcan\s+you\b',
                r'\bdo\s+you\s+know\b'
            ],
            'task': [
                r'\b(help|assist|do|create|make|build|generate|write)\b',
                r'\bcan\s+you\s+(help|assist|do)\b',
                r'\bi\s+need\b',
                r'\bplease\b'
            ],
            'personal': [
                r'\b(tell\s+me\s+about|about\s+you|who\s+are\s+you)\b',
                r'\byour\s+(name|purpose|function)\b',
                r'\bwhat\s+can\s+you\s+do\b'
            ]
        }
        
        # Sentiment keywords
        self.positive_words = {
            'great', 'awesome', 'excellent', 'good', 'nice', 'wonderful',
            'fantastic', 'amazing', 'perfect', 'thanks', 'thank you'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'wrong', 'error',
            'problem', 'issue', 'broken', 'failed', 'annoying'
        }
        
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text and extract intent, entities, and sentiment.
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary containing processed information
        """
        if not text or not isinstance(text, str):
            return self._empty_result()
            
        text_lower = text.lower().strip()
        
        # Extract intent
        intent = self._extract_intent(text_lower)
        
        # Extract entities
        entities = self._extract_entities(text, text_lower)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(text_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(intent, entities, sentiment)
        
        return {
            'intent': intent,
            'entities': entities,
            'sentiment': sentiment,
            'confidence': confidence,
            'original_text': text,
            'processed_text': text_lower
        }
    
    def _extract_intent(self, text: str) -> str:
        """Extract intent from text using pattern matching."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return intent
        return 'general'
    
    def _extract_entities(self, original_text: str, text_lower: str) -> Dict[str, Any]:
        """Extract entities from text."""
        entities = {}
        
        # Extract potential topics (simple noun detection)
        # Look for capitalized words (potential proper nouns)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', original_text)
        if proper_nouns:
            entities['proper_nouns'] = proper_nouns
            
        # Extract potential topics after question words
        topic_match = re.search(r'\b(about|regarding|concerning)\s+([^.!?]+)', text_lower)
        if topic_match:
            entities['topic'] = topic_match.group(2).strip()
            
        # Extract task types
        task_match = re.search(r'\b(help|assist)\s+with\s+([^.!?]+)', text_lower)
        if task_match:
            entities['task_type'] = task_match.group(2).strip()
            
        # Extract numbers
        numbers = re.findall(r'\b\d+\b', text_lower)
        if numbers:
            entities['numbers'] = numbers
            
        return entities
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text."""
        words = set(text.lower().split())
        
        positive_score = len(words.intersection(self.positive_words))
        negative_score = len(words.intersection(self.negative_words))
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_confidence(
        self, 
        intent: str, 
        entities: Dict[str, Any], 
        sentiment: str
    ) -> float:
        """Calculate confidence score for the analysis."""
        base_confidence = 0.5
        
        # Boost confidence if we found a clear intent
        if intent != 'general':
            base_confidence += 0.3
            
        # Boost confidence if we found entities
        if entities:
            base_confidence += 0.1 * min(len(entities), 3)
            
        # Slight boost for clear sentiment
        if sentiment != 'neutral':
            base_confidence += 0.1
            
        return min(base_confidence, 1.0)
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'intent': 'general',
            'entities': {},
            'sentiment': 'neutral',
            'confidence': 0.0,
            'original_text': '',
            'processed_text': ''
        }
    
    def add_intent_pattern(self, intent: str, pattern: str):
        """Add a new intent pattern."""
        if intent not in self.intent_patterns:
            self.intent_patterns[intent] = []
        self.intent_patterns[intent].append(pattern)
        
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents."""
        return list(self.intent_patterns.keys())