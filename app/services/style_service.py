# app/services/style_service.py

import re
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["ai_buddy"]
style_collection = db["user_style"]


class StyleService:

    def __init__(self):
        self.slang_words = [
            "lmao", "lol", "bro", "fr", "omg", "wtf", 
            "idk", "ikr", "bruh", "no cap", "cap", "ong"
        ]

    # ---------------------------
    # Extract style features
    # ---------------------------
    def analyze_style(self, text: str):
        text_lower = text.lower()

        # Emoji count
        emoji_count = len([c for c in text if c in self._emoji_range()])

        # Message length
        length = len(text)

        # Exclamations
        exclaims = text.count("!")

        # Slang detection
        slang_found = []
        for slang in self.slang_words:
            if slang in text_lower:
                slang_found.append(slang)

        return {
            "emoji_count": emoji_count,
            "length": length,
            "exclaims": exclaims,
            "slang": slang_found
        }

    # ---------------------------
    # Save/update style stats
    # ---------------------------
    def update_user_style(self, user_id: str, text: str):

        style = self.analyze_style(text)

        style_collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "total_messages": 1,
                    "total_emojis": style["emoji_count"],
                    "total_length": style["length"],
                    "total_exclaims": style["exclaims"]
                },
                "$addToSet": {
                    "slang_used": {"$each": style["slang"]}
                }
            },
            upsert=True
        )

    # ---------------------------
    # Fetch style profile
    # ---------------------------
    def get_user_style(self, user_id: str):
        profile = style_collection.find_one({"user_id": user_id})
        if not profile:
            return None

        total = profile.get("total_messages", 1)

        return {
            "avg_length": profile.get("total_length", 0) / total,
            "emoji_freq": profile.get("total_emojis", 0) / total,
            "exclaim_freq": profile.get("total_exclaims", 0) / total,
            "slang_used": profile.get("slang_used", [])
        }

    # ---------------------------
    # Helper: detect emojis
    # ---------------------------
    def _emoji_range(self):
        ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Misc symbols
            (0x1F680, 0x1F6FF),  # Transport
            (0x1F900, 0x1F9FF),  # Supplemental Symbols
        ]
        return {chr(i) for r in ranges for i in range(r[0], r[1])}


style_service = StyleService()
