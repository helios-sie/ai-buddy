from app.services.memory_service import memory_service
from app.services.emotion_service import analyze_emotion


def generate_reply(user_id: str, message: str):
    """
    Main conversational logic.
    Uses:
      - emotion engine
      - memory similarity
      - personality profile
      - style adaptation
    """

    # 1. Analyze emotion of current message
    emotion_result = analyze_emotion(message)
    emotion = emotion_result["detected_emotions"][0]

    # 2. Add this message to memory (now linked to user_id)
    memory_service.add_memory(user_id, message, emotion)

    # 3. Check if similar memory exists
    similar = memory_service.find_similar_memory(user_id, message)

    # 4. Get personality summary for this user
    personality = memory_service.summarize_personality(user_id)

    # ---------- REPLY GENERATION LOGIC ---------- #

    # If a similar message exists → respond contextually
    if similar:
        prev_text = similar["text"]
        prev_emotion = similar["emotion"]

        return (
            f"I remember you mentioned something similar earlier. "
            f"Last time you felt **{prev_emotion}**, and you said:\n"
            f"\"{prev_text}\".\n\n"
            f"Does this feel like the same situation, or is it different this time?"
        )

    # If no similar memory, generate fresh reply
    if emotion != "unknown":
        base_reply = emotion_result["advice"]
    else:
        base_reply = "I'm here with you. Tell me what's on your mind."

    # Style adaptation based on user personality
    style_tail = ""

    # If user expresses mostly positive emotions → energetic tone
    if personality["dominant_emotion"] in ["happy", "hopeful", "motivated"]:
        style_tail = " 😄"

    # If user expresses heavy emotions → calmer tone
    elif personality["dominant_emotion"] in ["sad", "broken", "anxious", "lonely"]:
        style_tail = " I'm right here with you."

    # If user tends to write long messages → more detailed replies
    if personality["memory_count"] > 5 and similar is None:
        base_reply += " And I want to understand you even better, keep talking to me."

    return base_reply + style_tai
