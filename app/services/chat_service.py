# app/services/chat_service.py

from app.services.memory_service import memory_service
from app.services.emotion_service import analyze_emotion
from app.services.style_service import style_service


def apply_style_to_reply(reply: str, style_profile: dict):
    """
    Modifies the AI reply based on user's texting style.
    """
    if not style_profile:
        return reply  # user has no style data yet

    emoji_freq = style_profile["emoji_freq"]
    exclaim_freq = style_profile["exclaim_freq"]
    slang_used = style_profile["slang_used"]
    avg_length = style_profile["avg_length"]

    # --------------------------
    # 1️⃣ Add emojis if user uses many emojis
    # --------------------------
    if emoji_freq > 0.5:     # user uses lots of emojis
        reply += " 🤍"
    elif emoji_freq > 0.2:
        reply += " 🙂"

    # --------------------------
    # 2️⃣ Add exclamation marks if user does that often
    # --------------------------
    if exclaim_freq > 0.4:
        reply += "!!"
    elif exclaim_freq > 0.2:
        reply += "!"

    # --------------------------
    # 3️⃣ If user uses slang, use similar slang
    # --------------------------
    slang_map = {
        "lmao": "lmao",
        "lol": "lol",
        "fr": "fr",
        "omg": "omg",
        "bruh": "bruh"
    }

    if slang_used:
        # pick the most used slang and add it
        common_slang = slang_used[0]
        if common_slang in slang_map:
            reply = f"{slang_map[common_slang]} {reply}"

    # --------------------------
    # 4️⃣ If user writes long & formal messages → give longer replies
    # --------------------------
    if avg_length > 120:
        reply += " If you want to talk more about this, I’m here for you in detail."

    return reply


def generate_reply(user_id: str, message: str):
    """
    Main conversational logic.
    Integrates:
      – emotion engine
      – memory similarity
      – personality profile
      – style learning (NEW)
    """

    # 1️⃣ Analyze emotion
    emotion_result = analyze_emotion(message)
    emotion = emotion_result["detected_emotions"][0]

    # 2️⃣ Store message in memory
    memory_service.add_memory(user_id, message, emotion)

    # 3️⃣ Update style engine based on this message (NEW)
    style_service.update_user_style(user_id, message)

    # 4️⃣ Get style profile (NEW)
    style_profile = style_service.get_user_style(user_id)

    # 5️⃣ Check similar memories
    similar = memory_service.find_similar_memory(user_id, message)

    # 6️⃣ Personality summary
    personality = memory_service.summarize_personality(user_id)

    # ------------------------------------------------
    # REPLY GENERATION LOGIC
    # ------------------------------------------------

    # If similar memory found → contextual reply
    if similar:
        prev_text = similar["text"]
        prev_emotion = similar["emotion"]

        base_reply = (
            f"I remember you mentioned something similar earlier. "
            f"Last time you felt **{prev_emotion}**, and you said:\n"
            f"\"{prev_text}\".\n\n"
            f"Does this feel like the same situation, or is it different this time?"
        )

        return apply_style_to_reply(base_reply, style_profile)

    # No similar memory → generate fresh reply
    if emotion != "unknown":
        base_reply = emotion_result["advice"]
    else:
        base_reply = "I'm here with you. Tell me what's on your mind."

    # Personality-based tone (your existing logic)
    if personality["dominant_emotion"] in ["happy", "hopeful", "motivated"]:
        base_reply += " 😊"
    elif personality["dominant_emotion"] in ["sad", "broken", "anxious", "lonely"]:
        base_reply += " I'm right here with you."

    # More detailed responses for users who write long or often
    if personality["memory_count"] > 5 and similar is None:
        base_reply += " And I want to understand you even better, keep talking to me."

    # FINAL STEP — Apply user texting style (NEW)
    final_reply = apply_style_to_reply(base_reply, style_profile)

    return final_reply
