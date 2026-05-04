# Session Management - Stage 1

## Overview

Stage 1 adds **Session Management** to UniMCP, enabling persistent and multi-turn conversations with automatic context preservation.

**Key Insight**: Sessions are **optional**. By default, `llm.chat()` uses an ephemeral in-memory session that's auto-garbage collected.

---

## Core Concepts

### **Two Types of Sessions**

#### 1. **Ephemeral Session** (Default - In-Memory)
```python
llm = UniLLM(client)

# Uses implicit temporary session
await llm.chat("Question 1")      # Session created, message added
await llm.chat("Question 2")      # Same session, context preserved
# Session auto-garbage collected when done
```

**Use cases:**
- Quick testing
- One-off queries
- Conversations you don't need to save

**Benefits:**
- No extra code
- Automatic cleanup
- Memory efficient

---

#### 2. **Persistent Session** (Explicit - Saved to Disk)
```python
session = llm.create_session(name="support_ticket_123")

await llm.chat("First message", session=session)
await llm.chat("Follow-up", session=session)

await session.save("conversations/123.json")  # Save to disk
```

**Use cases:**
- Multi-turn conversations you want to keep
- Support/help desk tickets
- Chat history for auditing
- Resuming conversations later

**Benefits:**
- Full conversation history saved
- Can load and continue anytime
- Exportable for analysis
- Perfect for UIs and web apps

---

## API Reference

### **Creating Sessions**

#### **Default Ephemeral**
```python
# Implicit - no explicit session created
response = await llm.chat("Your question")
```

#### **Explicit Persistent**
```python
# Create with optional name and system prompt
session = llm.create_session(
    name="my_conversation",
    system_prompt="You are a helpful assistant"
)

response = await llm.chat("Your question", session=session)
```

---

### **Session Methods**

#### **Save Session**
```python
await session.save("path/to/conversation.json")
```

Saves the entire session (messages, metadata) to a JSON file.

#### **Load Session**
```python
session = await UniLLM.load_session("path/to/conversation.json")
```

Loads a previously saved session. Can then continue chatting:
```python
response = await llm.chat("Continue here", session=session)
```

#### **Clear History**
```python
session.clear_history()
```

Clears all messages except system prompt. Useful for:
- Starting fresh in same session
- Reducing memory usage
- Resetting context

#### **Export Transcript**
```python
transcript = session.export_transcript()
print(transcript)
```

Returns formatted conversation as string. Perfect for:
- Displaying in UI
- Saving to text files
- Email notifications
- Logs and auditing

#### **Get Statistics**
```python
count = session.get_message_count()        # Total messages
turns = session.get_conversation_turns()   # User-assistant turns
```

---

## Usage Examples

### **Example 1: Simple Ephemeral Chat**
```python
async with UniClient(endpoint) as client:
    llm = UniLLM(client)
    
    response1 = await llm.chat("What tools do you have?")
    response2 = await llm.chat("Tell me more about X")
    # Session auto-cleaned up
```

### **Example 2: Save Conversation**
```python
async with UniClient(endpoint) as client:
    llm = UniLLM(client)
    
    session = llm.create_session(name="user_123_chat")
    
    response1 = await llm.chat("Hello", session=session)
    response2 = await llm.chat("How are you?", session=session)
    
    await session.save("conversations/123.json")
```

### **Example 3: Resume Conversation**
```python
async with UniClient(endpoint) as client:
    llm = UniLLM(client)
    
    # Load previous conversation
    session = await UniLLM.load_session("conversations/123.json")
    
    # Continue from where we left off
    response = await llm.chat("Any updates?", session=session)
    
    # Save updated conversation
    await session.save("conversations/123.json")
```

### **Example 4: Export for Display**
```python
session = llm.create_session()

await llm.chat("What's the weather?", session=session)
await llm.chat("What about tomorrow?", session=session)

# Get formatted transcript
transcript = session.export_transcript()

# Display in UI or save to file
print(transcript)
with open("transcript.txt", "w") as f:
    f.write(transcript)
```

### **Example 5: Multi-Session Management**
```python
# Create multiple independent sessions
session_1 = llm.create_session(name="conversation_1")
session_2 = llm.create_session(name="conversation_2")

# Use independently
await llm.chat("Message for session 1", session=session_1)
await llm.chat("Message for session 2", session=session_2)

# Save separately
await session_1.save("sessions/conv_1.json")
await session_2.save("sessions/conv_2.json")

# Later: Load and continue any one
session_1_loaded = await UniLLM.load_session("sessions/conv_1.json")
await llm.chat("Continue session 1", session=session_1_loaded)
```

---

## Architecture

```
UniLLM
├── self.messages        # Kept for backward compatibility
├── chat(user_input, session=None)
│   └── If no session provided → creates ephemeral Session()
│   └── Uses session.messages for conversation history
├── create_session(name, system_prompt, auto_save)
│   └── Returns new Session object
└── load_session(filepath) [static]
    └── Loads Session from disk

Session
├── self.name              # Session identifier
├── self.messages          # Conversation history
├── self.system_prompt     # System prompt
├── self.created_at        # Timestamp
├── self.updated_at        # Timestamp
├── save(filepath)         # Save to disk
├── load(filepath) [static]
├── clear_history()        # Clear messages
├── export_transcript()    # Format as string
├── get_message_count()    # Stats
└── get_conversation_turns() # Stats

SessionStorage [Internal]
├── save(session, filepath)      # Serialize to JSON
├── load(filepath)               # Deserialize from JSON
├── list_sessions(directory)     # List all saved sessions
└── delete_session(filepath)     # Delete session file
```

---

## Backward Compatibility

The default behavior is **unchanged**:

```python
# OLD CODE (still works)
llm = UniLLM(client)
response = await llm.chat("Question")

# NEW CODE (optional)
session = llm.create_session()
response = await llm.chat("Question", session=session)
```

---

## File Organization

```
src/unimcp/
├── session/
│   ├── __init__.py        # Session, SessionStorage exports
│   ├── session.py         # Session class
│   └── storage.py         # SessionStorage (save/load)
└── llm.py                 # Updated with session support

tests/
├── example_chat.py        # Original chat example (unchanged)
└── example_session.py     # New session examples
```

---

## Implementation Details

### **Why This Design?**

1. **Simplicity First**: Default ephemeral behavior requires no changes to existing code
2. **Opt-in Persistence**: Users only save when they need to
3. **Garbage Collection**: Temporary sessions auto-cleaned
4. **Flexible API**: Same `llm.chat()` works for both cases
5. **UI-Friendly**: Enables building chat UIs easily

### **JSON Format**
Sessions are stored as JSON:
```json
{
  "name": "conversation_1",
  "system_prompt": "You are helpful",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "created_at": "2026-05-01T10:30:00",
  "updated_at": "2026-05-01T10:35:00"
}
```

---

## Next Steps (Future Stages)

- **Stage 2**: Execution Pipeline (tool validation, retries, logging)
- **Stage 3**: Streaming Responses (real-time output)
- **Stage 4**: CLI Playground (interactive UI)
- **Future**: SQLite backend, session versioning, auto-save to cloud

