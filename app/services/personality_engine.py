# app/services/personality_engine.py
"""
Advanced Personality Engine (APE) - per-user adaptive personality model.

- Stores a personality profile per user_id (in-memory for now).
- Extracts textual style features from each message.
- Updates sliders and signature features.
- Exposes functions to get a user's current personality settings
  and to sample stylistic choices for reply generation.
"""

from collections import defaultdict, Counter
import re

# In-memory store: { user_id: profile_dict }
_user_profiles = defaultdict(lambda: {
    # Core sliders (0-10)
    "playful": 7,
    "supportive": 8,
    "sarcastic": 4,
    "energy": 7,
    "formality": 2,
    "emoji_usage": 6,
    # Derived stats
    "slang_level": 5,
    "avg_msg_len": 0.0,
    "msg_count": 0,
    "emoji_pref": Counter(),
    "signature_phrases": Counter(),
    # meta
    "last_updated": None
})

SLANG_TOKENS = {"bruh","idk","lol","lmao","ngl","omg","wtf","bro","vibe","lowkey","mood"}
EMOJI_RE = re.compile(r'[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\u2600-\u27BF]+', flags=re.UNICODE)

def _extract_emojis(text: str):
    return EMOJI_RE.findall(text)

def _extract_tokens(text: str):
    # simple tokens split, keep contractions
    tokens = re.findall(r"[a-zA-Z']+", text.lower())
    return tokens

def analyze_style_from_text(user_id: int, text: str):
    """
    Examine a message and produce style features:
    - slang score (0-10)
    - emoji list
    - length
    - signature phrase candidates
    """
    profile = _user_profiles[user_id]

    tokens = _extract_tokens(text)
    token_set = set(tokens)
    slang_hits = sum(1 for t in token_set if t in SLANG_TOKENS)
    slang_score = min(10, int((slang_hits / (len(token_set)+1)) * 20))  # scaled 0-10

    emojis = _extract_emojis(text)
    msg_len = len(text.strip())

    # find candidate signature phrases (2-3 word phrases with apostrophes/slang)
    phrases = re.findall(r"\b(?:[a-zA-Z']+\s){0,2}[a-zA-Z']+\b", text.lower())
    sig_candidates = [p for p in phrases if any(tok in SLANG_TOKENS for tok in p.split())][:3]

    return {
        "slang_score": slang_score,
        "emojis": emojis,
        "msg_len": msg_len,
        "sig_candidates": sig_candidates
    }

def update_profile_with_message(user_id: int, text: str):
    """
    Update the user's personality profile based on a single message.
    This updates averages, slang level, emoji prefs, and signature phrases.
    """
    profile = _user_profiles[user_id]
    stats = analyze_style_from_text(user_id, text)

    # update message count & avg length (running average)
    mc = profile["msg_count"]
    prev_avg = profile["avg_msg_len"]
    profile["msg_count"] = mc + 1
    profile["avg_msg_len"] = (prev_avg * mc + stats["msg_len"]) / (mc + 1)

    # update slang_level gradually (decay + add)
    # new_slang = weighted avg between old and detected
    profile["slang_level"] = int((profile["slang_level"] * mc + stats["slang_score"]) / (mc + 1))

    # update emoji usage slider (increase if user uses emojis often)
    if stats["emojis"]:
        profile["emoji_usage"] = min(10, profile["emoji_usage"] + 0.5)
        for e in stats["emojis"]:
            profile["emoji_pref"][e] += 1
    else:
        # small decay if user rarely uses emojis
        profile["emoji_usage"] = max(0, profile["emoji_usage"] - 0.02)

    # update signature phrases
    for sc in stats["sig_candidates"]:
        profile["signature_phrases"][sc] += 1

    # subtle adjustments to playful/supportive/sarcastic sliders based on cues
    # (these heuristics are simple; we can refine later)
    if stats["slang_score"] >= 4:
        profile["playful"] = min(10, profile["playful"] + 0.2)
    else:
        profile["playful"] = max(0, profile["playful"] - 0.02)

    # longer messages trend to more supportive / reflective replies
    if stats["msg_len"] > 120:
        profile["supportive"] = min(10, profile["supportive"] + 0.3)
        profile["formality"] = min(10, profile["formality"] + 0.1)
    else:
        profile["supportive"] = max(0, profile["supportive"] - 0.01)

    # update last_updated
    import datetime
    profile["last_updated"] = datetime.datetime.utcnow().isoformat()

    # write back
    _user_profiles[user_id] = profile
    return profile

def get_profile(user_id: int):
    """Return a copy of the user's profile (do not expose counters directly)."""
    p = _user_profiles[user_id].copy()
    p["emoji_pref"] = dict(p["emoji_pref"].most_common(3))
    p["signature_phrases"] = dict(p["signature_phrases"].most_common(5))
    return p

def sample_reply_style(user_id: int):
    """
    Produce sampled stylistic choices for the reply generator to use:
    - whether to use emojis
    - slang level to mimic
    - rough tone adjustments (playful/supportive/sarcastic)
    """
    p = _user_profiles[user_id]
    # decide emoji usage probabilistically based on slider
    use_emoji = p["emoji_usage"] >= 6
    preferred_emojis = [e for e, _ in p["emoji_pref"].most_common(2)]

    # determine slang mimic level (0-10)
    slang_level = p["slang_level"]

    # derive tone multipliers
    tone = {
        "playful": p["playful"],
        "supportive": p["supportive"],
        "sarcastic": p["sarcastic"],
        "energy": p["energy"],
        "formality": p["formality"]
    }

    return {
        "use_emoji": use_emoji,
        "preferred_emojis": preferred_emojis,
        "slang_level": slang_level,
        "tone": tone
    }

# Small helper to manually create or reset a profile (for testing)
def reset_profile(user_id: int):
    _user_profiles[user_id] = _user_profiles.default_factory()
    return get_profile(user_id)
