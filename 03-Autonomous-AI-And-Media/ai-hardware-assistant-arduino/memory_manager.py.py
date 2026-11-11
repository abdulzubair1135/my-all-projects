"""
Memory management system for CLEVER
Handles persistent storage of memories, notes, and preferences
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class CleverMemory:
    def __init__(self, memory_file: str = "memory/memories.json"):
        self.memory_file = memory_file
        self.memories = self.load()
        
    def load(self) -> Dict:
        """Load memories from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.get_default_memory()
        return self.get_default_memory()
    
    def get_default_memory(self) -> Dict:
        """Return default memory structure"""
        return {
            "user_info": {
                "name": "User",
                "preferences": {}
            },
            "notes": [],
            "conversations": [],
            "facts": [],
            "reminders": [],
            "system": {
                "first_run": time.time(),
                "last_run": time.time(),
                "total_conversations": 0
            }
        }
    
    def save(self):
        """Save memories to file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, indent=2, ensure_ascii=False)
    
    def add_note(self, note: str, category: str = "general"):
        """Add a new note"""
        self.memories["notes"].append({
            "id": len(self.memories["notes"]),
            "content": note,
            "category": category,
            "timestamp": time.time(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save()
        return len(self.memories["notes"]) - 1
    
    def get_notes(self, category: Optional[str] = None) -> List[Dict]:
        """Get all notes, optionally filtered by category"""
        if category:
            return [n for n in self.memories["notes"] if n["category"] == category]
        return self.memories["notes"]
    
    def add_conversation(self, user_input: str, clever_response: str):
        """Log a conversation"""
        self.memories["conversations"].append({
            "timestamp": time.time(),
            "user": user_input,
            "clever": clever_response
        })
        self.memories["system"]["total_conversations"] += 1
        self.memories["system"]["last_run"] = time.time()
        
        # Keep only last 100 conversations
        if len(self.memories["conversations"]) > 100:
            self.memories["conversations"] = self.memories["conversations"][-100:]
        
        self.save()
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preference"""
        self.memories["user_info"]["preferences"][key] = value
        self.save()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return self.memories["user_info"]["preferences"].get(key, default)
    
    def add_reminder(self, reminder: str, time_str: str):
        """Add a reminder"""
        self.memories["reminders"].append({
            "content": reminder,
            "time": time_str,
            "active": True,
            "created": time.time()
        })
        self.save()
    
    def search_memories(self, query: str) -> List[Dict]:
        """Search through all memories"""
        results = []
        query = query.lower()
        
        # Search notes
        for note in self.memories["notes"]:
            if query in note["content"].lower():
                results.append({
                    "type": "note",
                    "content": note["content"],
                    "date": note["date"]
                })
        
        # Search conversations
        for conv in self.memories["conversations"]:
            if query in conv["user"].lower() or query in conv["clever"].lower():
                results.append({
                    "type": "conversation",
                    "user": conv["user"],
                    "clever": conv["clever"]
                })
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get memory statistics"""
        return {
            "total_notes": len(self.memories["notes"]),
            "total_conversations": self.memories["system"]["total_conversations"],
            "total_reminders": len(self.memories["reminders"]),
            "first_run": datetime.fromtimestamp(
                self.memories["system"]["first_run"]
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "last_run": datetime.fromtimestamp(
                self.memories["system"]["last_run"]
            ).strftime("%Y-%m-%d %H:%M:%S")
        }

# Example usage
if __name__ == "__main__":
    memory = CleverMemory()
    
    # Add a note
    memory.add_note("User likes to wake up at 7 AM", "preferences")
    
    # Add conversation
    memory.add_conversation("What's the weather?", "I'll check that for you")
    
    # Get statistics
    stats = memory.get_statistics()
    print("Memory Statistics:", stats)