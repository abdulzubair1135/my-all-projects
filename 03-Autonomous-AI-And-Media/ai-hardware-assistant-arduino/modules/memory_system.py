# modules/memory_system.py
"""
Memory System - Notes Storage
"""

import json
import os
import time
 
class MemorySystem:
    def __init__(self, memory_file):
        self.memory_file = memory_file
        self.data = self.load()
    
    def load(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return {"notes": []}
        return {"notes": []}
    
    def save(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_note(self, note):
        self.data["notes"].append({
            "content": note,
            "time": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M")
        })
        self.save()
    
    def get_notes(self, limit=10):
        return self.data["notes"][-limit:]