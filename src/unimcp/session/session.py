"""
Session class for managing conversation state and persistence.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .storage import SessionStorage


class Session:
    """
    Manages a conversation session with optional persistence.
    
    A session can be:
    - Temporary (in-memory): Auto-garbage collected when done
    - Persistent: Saved to disk for later retrieval
    
    Attributes:
        name: Optional name for the session (for identification)
        system_prompt: System prompt for the LLM
        messages: List of message dicts in OpenAI format
        created_at: Timestamp of session creation
        updated_at: Timestamp of last update
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        auto_save: bool = False
    ):
        """
        Initialize a new session.
        
        Args:
            name: Optional name for the session (useful for identification)
            system_prompt: Initial system prompt for the LLM
            auto_save: If True, saves to memory on each chat (not to disk)
        """
        self.name = name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.system_prompt = system_prompt
        self.messages: List[Dict[str, Any]] = []
        self.auto_save = auto_save
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        # Add system prompt to messages if provided
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt
            })
    
    async def save(self, filepath: str) -> None:
        """
        Save the session to a file.
        
        Args:
            filepath: Path where to save the session (JSON format)
        
        Example:
            await session.save("conversations/support_ticket_123.json")
        """
        self.updated_at = datetime.now().isoformat()
        await SessionStorage.save(self, filepath)
    
    @staticmethod
    async def load(filepath: str) -> "Session":
        """
        Load a session from a file.
        
        Args:
            filepath: Path to load the session from
        
        Returns:
            Loaded Session object
        
        Example:
            session = await Session.load("conversations/support_ticket_123.json")
        """
        return await SessionStorage.load(filepath)
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the session (internal use).
        
        Args:
            role: "user", "assistant", or "tool"
            content: Message content
        """
        self.messages.append({
            "role": role,
            "content": content
        })
        self.updated_at = datetime.now().isoformat()
    
    def add_tool_result(self, tool_call_id: str, tool_name: str, content: str) -> None:
        """
        Add a tool execution result to the session (internal use).
        
        Args:
            tool_call_id: ID of the tool call
            tool_name: Name of the tool that was called
            content: Result content
        """
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": content
        })
        self.updated_at = datetime.now().isoformat()
    
    def clear_history(self) -> None:
        """
        Clear all messages except system prompt.
        
        Useful for starting a new conversation in the same session.
        """
        if self.system_prompt:
            self.messages = [{"role": "system", "content": self.system_prompt}]
        else:
            self.messages = []
        self.updated_at = datetime.now().isoformat()
    
    def get_message_count(self) -> int:
        """Get total number of messages in the session."""
        return len(self.messages)
    
    def get_conversation_turns(self) -> int:
        """Get number of user-assistant conversation turns (excluding system/tool messages)."""
        turns = 0
        for msg in self.messages:
            if msg.get("role") == "user":
                turns += 1
        return turns
    
    def export_transcript(self) -> str:
        """
        Export the conversation as a formatted transcript.
        
        Returns:
            Formatted string with the entire conversation
        
        Example:
            transcript = session.export_transcript()
            print(transcript)
        """
        lines = []
        lines.append(f"Session: {self.name}")
        lines.append(f"Created: {self.created_at}")
        lines.append(f"Updated: {self.updated_at}")
        lines.append("-" * 60)
        
        for msg in self.messages:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            
            if role == "SYSTEM":
                lines.append(f"[SYSTEM]\n{content}\n")
            elif role == "USER":
                lines.append(f"👤 User:\n{content}\n")
            elif role == "ASSISTANT":
                lines.append(f"🤖 Assistant:\n{content}\n")
            elif role == "TOOL":
                tool_name = msg.get("name", "unknown")
                lines.append(f"🔧 Tool Result ({tool_name}):\n{content}\n")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary for serialization.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "messages": self.messages,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Session":
        """
        Create a session from dictionary (for deserialization).
        
        Args:
            data: Dictionary with session data
        
        Returns:
            Session object
        """
        session = Session(
            name=data.get("name"),
            system_prompt=None  # Will be restored from messages
        )
        session.messages = data.get("messages", [])
        session.created_at = data.get("created_at")
        session.updated_at = data.get("updated_at")
        return session
    
    def __repr__(self) -> str:
        return f"Session(name='{self.name}', messages={self.get_message_count()}, turns={self.get_conversation_turns()})"
