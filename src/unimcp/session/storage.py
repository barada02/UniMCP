"""
Session storage and persistence layer.
Handles saving and loading sessions to/from disk.
"""

import json
import os
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from .session import Session


class SessionStorage:
    """
    Handles serialization and deserialization of sessions.
    Supports JSON format for now, can be extended for SQLite, etc.
    """
    
    @staticmethod
    async def save(session: "Session", filepath: str) -> None:
        """
        Save a session to a JSON file.
        
        Args:
            session: Session object to save
            filepath: Path where to save the session
        
        Raises:
            IOError: If file cannot be written
        """
        try:
            # Create directories if they don't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize session
            data = session.to_dict()
            
            # Write to JSON file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            raise IOError(f"Failed to save session to '{filepath}': {e}") from e
    
    @staticmethod
    async def load(filepath: str) -> "Session":
        """
        Load a session from a JSON file.
        
        Args:
            filepath: Path to load the session from
        
        Returns:
            Session object
        
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Session file not found: '{filepath}'")
            
            # Read from JSON file
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Import here to avoid circular import
            from .session import Session
            
            # Deserialize session
            session = Session.from_dict(data)
            return session
        
        except FileNotFoundError:
            raise
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in session file '{filepath}': {e.msg}",
                e.doc,
                e.pos
            ) from e
        except Exception as e:
            raise IOError(f"Failed to load session from '{filepath}': {e}") from e
    
    @staticmethod
    def list_sessions(directory: str = "./sessions") -> list:
        """
        List all saved sessions in a directory.
        
        Args:
            directory: Directory to search for sessions
        
        Returns:
            List of session file paths
        """
        if not os.path.exists(directory):
            return []
        
        sessions = []
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)
                sessions.append(filepath)
        
        return sorted(sessions)
    
    @staticmethod
    def delete_session(filepath: str) -> None:
        """
        Delete a saved session file.
        
        Args:
            filepath: Path to the session file
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Session file not found: '{filepath}'")
            
            os.remove(filepath)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise IOError(f"Failed to delete session '{filepath}': {e}") from e
