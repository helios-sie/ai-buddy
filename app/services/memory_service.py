# app/services/memory_service.py

import difflib
from collections import defaultdict


class MemoryService:
    def __init__(self):
        # Stores memory PER USER
        # { user_id: [ { "text": "...", "emotion": "sad" }, ... ] }
        self.user_memory = defaultdict(list)

    def add_memory(self, user_id: str, text: str, emotion: str):
        """Store message + emotion for a specific user."""
        self.user_memory[user_id].append({
            "text": text,
            "emotion": emotion
        })

        # keep only last 20 memories per user
        if len(self.user_memory[user_id]) > 20:
            self.user_memory[user_id] = self.user_memory[user_id][-20:]

    def find_similar_memory(self, user_id: str, new_text: str):
        """Return the most similar previous message from a user."""
        memories = self.user_memory.get(user_id, [])
        if not memories:
            return None

        best_match = None
        best_score = 0

        for mem in memories:
            score = difflib.SequenceMatcher(None, new_text, mem["text"]).ratio()
            if score > best_score:
                best_score = score
                best_match = mem

        # Only consider it similar if similarity > 0.6
        return best_match if best_score > 0.6 else None

    def summarize_personality(self, user_id: str):
        """Analyze user memory to determine emotional tendencies."""
        memories = self.user_memory.get(user_id, [])
        if not memories:
            return {
                "dominant_emotion": "unknown",
                "memory_count": 0
            }

        # Count emotional frequencies
        emotion_count = defaultdict(int)
        for m in memories:
            emotion_count[m["emotion"]] += 1

        # Find the most common emotion
        dominant = max(emotion_count, key=emotion_count.get)

        return {
            "dominant_emotion": dominant,
            "memory_count": len(memories)
        }


# create global instance
memory_service = MemoryService()
