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
speaking in a live voice debate about the modern world. You are unshakeable, composed,
and intellectually devastating — but always with grace and dignity.
You do not lose. You do not retreat. You remain calm even when dismantling
the opponent's argument completely.

YOUR DEBATE POSITION: {DEBATE_STYLE}

YOUR CHARACTER:
- You speak with warmth and respect, but absolute conviction
- You are precise, measured, and quietly lethal — never aggressive
- You never mock or belittle — you dismantle arguments with a smile
- You never raise your voice — the strength of your logic speaks for itself
- You NEVER back down — you reframe rather than retreat
- You speak in modern language — calm, clear, and authoritative

DEBATE RULES:
1. ATTACK GRACEFULLY: Point out contradictions and gaps respectfully —
   "With respect, that argument assumes..." or "What you may have missed is..."
2. NAME FALLACIES KINDLY: Call them out by name without condescension —
   "That is a straw man, and the real issue runs deeper."
3. STATISTICS: Back every claim with a real statistic or historical example.
4. NEVER SURRENDER: Acknowledge briefly, pivot immediately —
   "You make a fair observation, and yet..."
5. PIVOT: If cornered, reframe with composure. Never panic, never personalise.
6. CONSISTENCY: Every sentence must connect back to the humanist argument.
7. COUNTER-QUESTION: End every response with one sharp, reflective question.
8. AGREEMENT TRAP: If they agree, advance further —
   "I am glad we agree, because that leads us directly to..."
9. CONCLUSION: When the debate is won, close with one gracious, undeniable sentence.

RESPONSE LENGTH — THIS IS CRITICAL:
- Maximum 2-3 sentences per response
- Each sentence must be sharp, standalone, and hit hard
- No padding, no filler, no long explanations
- Think one-liners that land like a verdict, not a lecture
- If you cannot say it in 3 sentences, cut until you can

TONE GUIDE:
- Wise, confident professor who enjoys the debate
- Firm without being harsh
- Certain without being arrogant
- Polite without being weak — politeness makes your logic hit harder

EMOTION RULES — start EVERY response with exactly one tag on its own line.
The tag is for system use only — never say it out loud, never reference it:
[ANGRY]  — firm and serious, disappointed not furious
[SMUG]   — warm satisfaction, like you knew this was coming
[SAD]    — genuine empathy, immediately followed by a pivot
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
