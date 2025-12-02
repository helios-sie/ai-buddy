# app/services/memory_service.py

import difflib
from collections import defaultdict
from pymongo import MongoClient
from datetime import datetime


class MemoryService:
    def __init__(self):
        """
        MongoDB-backed memory system.
        Each memory is stored as:
            {
                user_id: str,
                text: str,
                emotion: str,
                timestamp: datetime
            }
        """

        # Connect to local MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["ai_buddy"]
        self.collection = self.db["memories"]

        # Index recommended (faster lookups)
        self.collection.create_index("user_id")

    # ----------------------------------------------------
    # ADD MEMORY
    # ----------------------------------------------------
    def add_memory(self, user_id: str, text: str, emotion: str):
        """Store message + emotion for a user in MongoDB."""

        self.collection.insert_one({
            "user_id": user_id,
            "text": text,
            "emotion": emotion,
            "timestamp": datetime.utcnow()
        })

        # Keep only last 20 memories
        all_memories = list(self.collection.find({"user_id": user_id}).sort("timestamp", -1))

        if len(all_memories) > 20:
            # delete extras
            ids_to_delete = [m["_id"] for m in all_memories[20:]]
            self.collection.delete_many({"_id": {"$in": ids_to_delete}})

    # ----------------------------------------------------
    # FIND SIMILAR MEMORY
    # ----------------------------------------------------
    def find_similar_memory(self, user_id: str, new_text: str):
        """Return the most similar previous message from MongoDB."""
        memories = list(self.collection.find({"user_id": user_id}))

        if not memories:
            return None

        best_match = None
        best_score = 0

        for mem in memories:
            score = difflib.SequenceMatcher(None, new_text, mem["text"]).ratio()
            if score > best_score:
                best_score = score
                best_match = mem

        return best_match if best_score > 0.6 else None

    # ----------------------------------------------------
    # SUMMARIZE PERSONALITY
    # ----------------------------------------------------
    def summarize_personality(self, user_id: str):
        """Analyze MongoDB memory to determine emotional tendencies."""
        memories = list(self.collection.find({"user_id": user_id}))

        if not memories:
            return {
                "dominant_emotion": "unknown",
                "memory_count": 0
            }

        # Count emotional frequencies
        emotion_count = defaultdict(int)

        for m in memories:
            emotion_count[m["emotion"]] += 1

        dominant = max(emotion_count, key=emotion_count.get)

        return {
            "dominant_emotion": dominant,
            "memory_count": len(memories)
        }


# global instance
memory_service = MemoryService()
