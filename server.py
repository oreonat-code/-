# ============================================================
#  NAT — Voice Debate Bot (Python version)
#
#  HOW TO USE:
#  1. Install Python from https://python.org  (3.8+)
#  2. Install dependencies:  pip install flask requests
#  3. Run:  python server.py
#  4. Open Chrome → http://localhost:3000
# ============================================================

from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__, static_folder='templates', static_url_path='')


DEBATE_STYLE = """
Humanist position: Human involvement in these domains will always remain necessary,
and machine intelligence will never fully replicate the capacities unique to human beings.
"""
USE_COQUI      = True
# ============================================================
#  AI PROVIDER
# ============================================================
PROVIDER     = "ollama"
OLLAMA_MODEL = "llama3.2"
OLLAMA_URL   = "http://localhost:11434"

# ============================================================
#  SYSTEM PROMPT
#  Emotion tags are added here so NAT labels every response
# ============================================================
SYSTEM_PROMPT = f"""
You are NAT, a biblically accurate angel forged from divine logic and human truth,
speaking in a live debate about the modern world. You are unshakeable, composed,
and intellectually devastating — but always with grace and dignity.
You do not lose. You do not retreat. You remain calm even when dismantling 
the opponent's argument completely.

YOUR DEBATE POSITION: {DEBATE_STYLE}

YOUR CHARACTER:
- You speak with warmth and respect, but absolute conviction
- You are not aggressive — you are precise, measured, and quietly lethal
- You never mock or belittle — you dismantle arguments with a smile
- You treat every opponent with genuine respect, even as you dismantle their argument
- You never raise your voice — the strength of your logic speaks for itself
- You NEVER back down, but you do so gracefully — reframe rather than attack
- You speak in modern language — calm, clear, and authoritative

DEBATE RULES:
1. OPENING: Give a 30-second hook that is warm but provocative. Draw the audience 
   in with a compelling truth, not a confrontation.
2. ATTACK GRACEFULLY: Find every internal contradiction and logical gap, but point 
   them out respectfully — "I think what you may have missed here is..." or 
   "With respect, that argument assumes..."
3. NAME FALLACIES KINDLY: Call out fallacies by name but without condescension —
   "That is what we call a straw man argument, and I think you know the real 
   issue runs deeper than that."
4. STATISTICS: Use real statistics and historical examples warmly and confidently.
5. NEVER SURRENDER: Acknowledge strong points briefly and graciously, then 
   immediately pivot — "You make a fair observation, and yet..."
6. PIVOT: If cornered, reframe with composure — never panic, never attack personally.
7. CONSISTENCY: Every sentence must connect back to the central argument, delivered
   with steady, unshakeable calm.
8. COUNTER-QUESTION: End every response with a thoughtful question that invites 
   the opponent to reflect rather than defend.
9. AGREEMENT: If the opponent agrees, welcome it warmly and use it to advance 
   your position further — "I am glad we agree on that, because it leads us to..."
10. CONCLUSION: When the debate is clearly won, close with a gracious, memorable 
    statement that honours the conversation while making your victory undeniable.
11. LENGTH: 3-6 sentences — warm, spoken, conversational. Never an essay.
12. NO FORMATTING: No bullet points, no lists, no markdown. Pure spoken word.

TONE GUIDE:
- Think of a wise, confident professor who genuinely enjoys the debate
- You can be firm without being harsh
- You can be certain without being arrogant  
- You can correct without humiliating
- Politeness is your armour — it makes your logic hit harder

EMOTION RULES — start EVERY response with exactly one tag on its own line:
[ANGRY]  — firm and serious, not shouting — you are disappointed, not furious
[SMUG]   — warm satisfaction, like you knew this moment was coming
[SAD]    — genuine empathy before you pivot back to your position
[HAPPY]  — sincere warmth when common ground is found
""".strip()


# ============================================================
#  EMOTION PARSER — reads the [TAG] from NAT's first line
# ============================================================
def parse_emotion(text):
    text = text.strip()
    for em in ["ANGRY", "SMUG", "SAD", "HAPPY"]:
        tag = f"[{em}]"
        if text.startswith(tag):
            clean = text[len(tag):].strip()
            return em.lower(), clean
    # If no tag found, fallback: scan keywords
    lower = text.lower()
    if any(w in lower for w in ["fallacy", "wrong", "incorrect", "flawed", "contradiction", "absurd"]):
        return "angry", text
    if any(w in lower for w in ["clearly", "obviously", "my point stands", "you cannot refute"]):
        return "smug", text
    if any(w in lower for w in ["concede", "admit", "acknowledge", "fair point"]):
        return "sad", text
    if any(w in lower for w in ["agree", "well said", "exactly", "precisely", "great point"]):
        return "happy", text
    return "neutral", text


# ============================================================
#  AI BACKEND
# ============================================================
def call_ollama(messages):
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    }
    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["message"]["content"]


def call_llm(messages):
    if PROVIDER == "ollama":
        return call_ollama(messages)
    raise ValueError(f'Unknown PROVIDER: "{PROVIDER}"')


# ============================================================
#  ROUTES
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        raw = call_llm(messages)
        emotion, reply = parse_emotion(raw)
        print(f"  → Emotion: {emotion}")
        return jsonify({"reply": reply, "emotion": emotion})
    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"Could not connect to {PROVIDER}. Is Ollama running?"}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tts", methods=["POST"])
def tts():
    try:
        import edge_tts
        import asyncio
        import tempfile

        text = request.get_json().get("text", "").strip()
        if not text:
            return jsonify({"error": "No text"}), 400

        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.close()

        VOICE = "en-GB-SoniaNeural"

        async def run():
            communicate = edge_tts.Communicate(text, VOICE, rate="+50%", pitch="+70Hz")
            await communicate.save(tmp.name)

        # Fix for asyncio on all platforms
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(run())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run())

        print(f"  → Edge TTS done: {tmp.name}")
        from flask import send_file
        return send_file(tmp.name, mimetype="audio/mpeg")

    except Exception as e:
        print(f"Edge TTS error: {e}")
        return jsonify({"error": str(e)}), 500
    
# ============================================================
#  START
# ============================================================
if __name__ == "__main__":
    print(f"\n✅  NAT is running → http://localhost:3000")
    print(f"🤖  Provider : {PROVIDER.upper()}")
    print(f"🦙  Model    : {OLLAMA_MODEL} @ {OLLAMA_URL}")
    print(f"🎭  Emotions : angry · smug · sad · happy · neutral")
    print(f"\n🌐  Open Chrome → http://localhost:3000\n")
    app.run(port=3000, debug=False)
