"""
Memory Manager for Personal AI Agent

Handles short-term and long-term memory storage and retrieval.
"""

import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path


class MemoryManager:
    """Manages agent memory for context and learning."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the memory manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Memory settings
        self.memory_dir = Path(config.get('memory_dir', 'data/memory'))
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.memory_dir / 'memory.db'
        self.max_context_length = config.get('max_context_length', 10)
        self.memory_retention_days = config.get('memory_retention_days', 30)
        
        # Initialize database
        self._init_database()
        
        # Short-term memory (in-memory storage)
        self.short_term_memory = {}
        
    def _init_database(self):
        """Initialize the SQLite database for long-term memory."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    conversation_id TEXT,
                    user_input TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_context (
                    user_id TEXT PRIMARY KEY,
                    context_data TEXT NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_timestamp 
                ON interactions(user_id, timestamp)
            ''')
            
    def store_interaction(
        self,
        user_input: str,
        agent_response: str,
        user_id: str = "default",
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Store an interaction in memory."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO interactions 
                (user_id, conversation_id, user_input, agent_response, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                conversation_id,
                user_input,
                agent_response,
                json.dumps(metadata) if metadata else None
            ))
            
        self.logger.debug(f"Stored interaction for user {user_id}")
        
    def get_recent_interactions(
        self,
        user_id: str = "default",
        limit: int = None,
        conversation_id: Optional[str] = None
    ) -> List[Dict]:
        """Get recent interactions for context."""
        if limit is None:
            limit = self.max_context_length
            
        query = '''
            SELECT user_input, agent_response, timestamp, metadata
            FROM interactions
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if conversation_id:
            query += ' AND conversation_id = ?'
            params.append(conversation_id)
            
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            interactions = []
            for row in cursor:
                interaction = {
                    'user_input': row['user_input'],
                    'agent_response': row['agent_response'],
                    'timestamp': row['timestamp'],
                }
                
                if row['metadata']:
                    try:
                        interaction['metadata'] = json.loads(row['metadata'])
                    except json.JSONDecodeError:
                        pass
                        
                interactions.append(interaction)
                
            return list(reversed(interactions))  # Return in chronological order
            
    def get_relevant_context(
        self,
        current_input: str,
        user_id: str = "default",
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get relevant context for the current input."""
        context = {
            'recent_interactions': self.get_recent_interactions(
                user_id, 
                conversation_id=conversation_id
            ),
            'user_context': self.get_user_context(user_id),
        }
        
        # Add short-term memory if available
        if user_id in self.short_term_memory:
            context['short_term'] = self.short_term_memory[user_id]
            
        return context
        
    def store_user_context(self, user_id: str, context_data: Dict[str, Any]):
        """Store user context data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO user_context (user_id, context_data)
                VALUES (?, ?)
            ''', (user_id, json.dumps(context_data)))
            
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT context_data FROM user_context WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row and row['context_data']:
                try:
                    return json.loads(row['context_data'])
                except json.JSONDecodeError:
                    pass
                    
        return {}
        
    def add_to_short_term_memory(self, user_id: str, key: str, value: Any):
        """Add data to short-term memory."""
        if user_id not in self.short_term_memory:
            self.short_term_memory[user_id] = {}
            
        self.short_term_memory[user_id][key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        
    def clear_short_term_memory(self, user_id: str):
        """Clear short-term memory for a user."""
        if user_id in self.short_term_memory:
            del self.short_term_memory[user_id]
            
    def cleanup_old_memories(self):
        """Clean up old memories based on retention policy."""
        cutoff_date = datetime.now() - timedelta(days=self.memory_retention_days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM interactions 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            
        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} old interactions")
            
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Get interaction count
            cursor = conn.execute('SELECT COUNT(*) FROM interactions')
            interaction_count = cursor.fetchone()[0]
            
            # Get user count
            cursor = conn.execute('SELECT COUNT(DISTINCT user_id) FROM interactions')
            user_count = cursor.fetchone()[0]
            
            # Get recent activity
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor = conn.execute('''
                SELECT COUNT(*) FROM interactions WHERE timestamp > ?
            ''', (week_ago,))
            recent_interactions = cursor.fetchone()[0]
            
        return {
            'total_interactions': interaction_count,
            'unique_users': user_count,
            'interactions_last_week': recent_interactions,
            'short_term_memory_users': len(self.short_term_memory),
            'database_size_mb': self.db_path.stat().st_size / 1024 / 1024 if self.db_path.exists() else 0
        }