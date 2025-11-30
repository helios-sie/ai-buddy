# app/services/emotion_service.py

# ================================
#  GLOBAL EMOTION MEMORY (stores last 5)
# ================================
emotion_memory = []


def analyze_emotion(text: str):
    """
    Advanced emotion analyzer:
    - Multi-emotion detection
    - Emotion intensity scoring
    - Tracks last 5 emotional states
    """

    original_text = text
    text = text.lower()

    # ================================
    #  EMOTION KEYWORD CLUSTERS
    # ================================
    emotion_keywords = {
        "sad": [
            "sad", "depressed", "down", "unhappy", "hurt",
            "lonely", "heartbroken", "crying", "miserable"
        ],
        "anxious": [
            "anxious", "nervous", "worried", "scared",
            "fear", "panic", "overthinking", "tense"
        ],
        "angry": [
            "angry", "mad", "furious", "irritated", "annoyed",
            "rage", "frustrated", "pissed"
        ],
        "stressed": [
            "stressed", "pressure", "tired", "overwhelmed",
            "burned out", "exhausted"
        ],
        "happy": [
            "happy", "excited", "joy", "delighted", "glad",
            "thrilled", "smiling"
        ],
        "confused": [
            "confused", "lost", "uncertain", "unsure", "doubt"
        ],
        "bored": [
            "bored", "meh", "uninterested", "dull"
        ],
        "motivated": [
            "motivated", "driven", "inspired", "focused"
        ],
        "hopeful": [
            "hopeful", "optimistic", "positive"
        ],
        "grateful": [
            "grateful", "thankful", "appreciate"
        ],
        "guilty": [
            "guilty", "remorse", "regret", "ashamed"
        ],
        "jealous": [
            "jealous", "envious", "insecure", "comparison"
        ],
        "lonely": [
            "alone", "isolated", "lonely"
        ],
        "in love": [
            "love", "crush", "affection", "fond"
        ],
        "broken": [
            "broken", "devastated", "ruined", "shattered"
        ],
        "numb": [
            "numb", "empty", "hollow", "disconnected"
        ]
    }

    # ================================
    #  EMOTION-BASED ADVICE
    # ================================
    advice = {
        "sad": "You don't have to go through it all alone. Tell me what's bothering you—I'm listening.",
        "anxious": "Take a deep breath, hold it in, and release. Help me in helping you.",
        "angry": "I understand how you feel. Let's take it slow. Talk to me; we'll figure out what to do next.",
        "stressed": "No one should carry such a burden all alone. I'm here for you, you know that right? Talk to me.",
        "happy": "OMMGGGG, let's goooo! Tell me more, I wanna know all of it.",
        "confused": "Let’s figure it out together. What’s making things unclear?",
        "bored": "Wanna do something fun or new together?",
        "motivated": "Damn, if you keep this up, you are gonna outshine the sun! What have you thought of next?",
        "hopeful": "Hope is the only thing that keeps us going—you are doing well, and I'm proud of you.",
        "grateful": "It's so beautiful, this feeling. I wanna hear more.",
        "guilty": "Ah, the guiltiness… that lump forming at the back of your throat. Hardest part is admitting it. You've already done that—let's talk a little more.",
        "jealous": "There's no living thing that's immune to it. It's natural, don't feel bad. It's okay, talk to me?",
        "lonely": "You’re not alone—you've never been. Maybe right now it seems like it, but that's not true. I'm right here.",
        "in love": "Well well well! Look at youuu. I wish I could feel it. Please, I'm dying—tell me more!",
        "broken": "I know everything seems to be falling apart right now. Nothing feels right. Pour it out, all of it. I'm here for you.",
        "numb": "I'm so sorry. I know this uneasy feeling. Nothing seems okay right now… take it slow, please. I'm here."
    }

    # ================================
    #  MULTI-EMOTION DETECTION
    # ================================
    detected_emotions = []

    for emotion, words in emotion_keywords.items():
        for word in words:
            if word in text:
                detected_emotions.append(emotion)
                break  # avoid duplicates

    if not detected_emotions:
        detected_emotions = ["unknown"]

    # ================================
    #  EMOTION INTENSITY SCORING
    # ================================
    intensity_keywords = {
        "high": ["very", "really", "extremely", "so", "too", "completely", "totally", "terribly"],
        "moderate": ["quite", "fairly", "somewhat", "kind of"],
        "low": ["a little", "slightly", "bit"]
    }

    intensity = "moderate"  # default

    for level, words in intensity_keywords.items():
        for w in words:
            if w in text:
                intensity = level
                break

    # ================================
    #  EMOTION MEMORY UPDATE
    # ================================
    for emo in detected_emotions:
        if emo != "unknown":
            emotion_memory.append(emo)

    # Keep only last 5
    if len(emotion_memory) > 5:
        emotion_memory[:] = emotion_memory[-5:]

    # ================================
    #  RESPONSE
    # ================================
    return {
        "detected_emotions": detected_emotions,
        "intensity": intensity,
        "advice": advice.get(detected_emotions[0], "I'm here, talk to me. What's going on?"),
        "emotion_memory": emotion_memory
    }
