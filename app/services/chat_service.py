# app/services/chat_service.py

from app.services.emotion_service import analyze_emotion
from app.services.personality_engine import (
    load_personality,
    update_personality,
    apply_personality,
)
from app.services.memory_service import (
    save_message,
    get_recent_memory
)

def generate_reply(user_id: str, message: str):
    """
    Main chat logic:
    - analyze emotions
    - update personality
    - fetch recent memory
    - generate personalized response
    """

    # 1. Save user message into memory
    save_message(user_id, "user", message)

    # 2. Load existing personality profile
    personality = load_personality(user_id)

    # 3. Emotion detection
    emotion_result = analyze_emotion(message)

    # 4. Update personality based on emotion + message style
    personality = update_personality(user_id, message, emotion_result)

    # 5. Get recent memory (last 5 messages)
    memory_snippet = get_recent_memory(user_id, limit=5)

    # 6. Generate base response
    base_response = build_base_response(message, emotion_result, memory_snippet)

    # 7. Apply personality (tone, slang, quirks, etc.)
    final_response = apply_personality(base_response, personality)

    # 8. Save bot response into memory
    save_message(user_id, "bot", final_response)

    return {
        "emotion": emotion_result["emotion"],
        "response": final_response,
        "personality": personality,
    }


# ---------------------------------------------------------
# Helper: Base emotional response generator
# ---------------------------------------------------------

def build_base_response(message: str, emotion_data: dict, memory):
    """
    Creates a raw emotional response before personality is applied.
    """

    emotion = emotion_data.get("emotion")
    advice = emotion_data.get("advice")

    # If emotion is unknown → neutral supportive response
    if emotion == "unknown":
        return f"I hear you. {advice}"

    # If emotion is known
    return f"I can sense you're feeling {emotion}. {advice}"
