"""
Conversation history management.
"""
from typing import List, Dict, Any
from pathlib import Path
import json
from datetime import datetime


class ConversationManager:
    """Manages conversation history persistence."""
    
    def __init__(self) -> None:
        self.conversation_file = Path(".agent700_conversation.json")
        self.conversation_history = self.load_conversation()
    
    def load_conversation(self) -> List[Dict[str, Any]]:
        """Load conversation history from file."""
        if self.conversation_file.exists():
            try:
                with open(self.conversation_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load conversation: {e}")
        return []
    
    def save_conversation(self) -> None:
        """Save conversation history to file."""
        try:
            with open(self.conversation_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save conversation: {e}")
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to conversation history."""
        self.conversation_history.append({
            "role": "user", "content": message, "timestamp": datetime.now().isoformat()
        })
        self.save_conversation()
    
    def add_agent_message(self, message: str) -> None:
        """Add an agent message to conversation history."""
        self.conversation_history.append({
            "role": "agent", "content": message, "timestamp": datetime.now().isoformat()
        })
        self.save_conversation()
    
    def get_conversation_context(self) -> List[Dict[str, Any]]:
        """Get recent conversation context (last 10 messages)."""
        return self.conversation_history[-10:]
