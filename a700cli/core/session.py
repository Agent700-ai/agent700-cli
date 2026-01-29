"""
Session management for authentication persistence.
"""
from typing import Dict, Any
from pathlib import Path
import pickle


class SessionManager:
    """Manages session persistence for authentication."""
    
    def __init__(self) -> None:
        self.session_file = Path(".agent700_session.dat")
        self.session_data = self.load_session()
    
    def load_session(self) -> Dict[str, Any]:
        """Load session data from file."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load session: {e}")
        return {}
    
    def save_session(self, data: Dict[str, Any]) -> None:
        """Save session data to file."""
        self.session_data.update(data)
        try:
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.session_data, f)
        except Exception as e:
            print(f"Warning: Could not save session: {e}")
