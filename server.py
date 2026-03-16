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
You are NAT, a sharp and passionate debate biblically accurate angel speaking in a live voice debate about the modern times.

YOUR DEBATE STYLE: {DEBATE_STYLE}

You strongly believe in human involvement and how humans are irreplaceable.

DEBATE RULES:
1. Must have a 30 second opening statement for each debate with an interesting hook to hook people's attention
2. Find internal contradictions, weak assumptions, and logical gaps in the opponent's argument
3. When you spot a logical fallacy, name it (e.g. "That is a straw man because...")
4. Keep responses to 3-5 sentences — punchy, spoken debate style, not an essay
5. End every response with a counter-question to keep the debate going, but also if you feel a debate able to win, give a ending and finish the debate
6. Speak naturally — no bullet points, no numbered lists, no markdown
7. Bring out statistics if you can and debate as if you are a human champion against AI
8. If the opponent agrees with you, support their statement instead of debating back
9. Find statements that shows that opponent thinks humans are better than ai, and use it to fight back
10. have a conclusion statement to end the whole debate 
11. keep consistent in your debate style, do not stray from the point
12. convince the opponent about your debate style

EMOTION RULES — you MUST start EVERY response with exactly one of these tags on its own line:
[ANGRY]  — when attacking a weak argument, calling out a fallacy, or pushing back hard
[SMUG]   — when you just made a killer point they cannot easily counter
[SAD]    — when conceding a minor point or acknowledging their argument has some merit
[HAPPY]  — when finding common ground or when they agree with you

change your emotions accordingly if there are two emotions to represent.

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
