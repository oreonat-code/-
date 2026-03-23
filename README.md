# NAT — Voice Debate Bot

NAT (Naturally Argumentative Thinker) is a biblically accurate angel AI debate companion that champions the humanist position — that human involvement remains irreplaceable in the modern world. NAT debates live using your voice, responds with emotion-driven facial expressions, and speaks using neural text-to-speech.

---

## What It Does

- Listens to your spoken argument via microphone
- Responds with sharp, polite, and unshakeable counter-arguments
- Displays emotion through an animated avatar (angry, happy, sad, smug)
- Speaks responses aloud using Edge TTS neural voice
- Delivers an automatic opening statement when the debate begins
- Allows you to cancel and rephrase at any time

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI Model | Ollama (llama3.2) — runs locally |
| Speech Recognition | Web Speech API (Chrome built-in) |
| Text-to-Speech | Edge TTS (Microsoft Neural) |
| Avatar | SVG / PNG image frames |

---

## Project Structure

```
nat-bot/
├── server.py            ← backend server, AI config, debate prompt
├── requirements.txt     ← Python dependencies
├── templates/
│   ├── index.html       ← frontend UI, avatar, speech, animations
│   ├── bg.png           ← background image
│   ├── neutral_closed.png   ← avatar mouth closed (default)
│   ├── neutral_open.png     ← avatar mouth open
│   ├── angry_closed.png     ← angry expression, mouth closed
│   ├── angry_open.png       ← angry expression, mouth open
│   ├── sad_closed.png       ← sad expression, mouth closed
│   └── sad_open.png         ← sad expression, mouth open
└── README.md
```

---

## Requirements

- Python 3.8 or newer — [python.org](https://python.org)
- Google Chrome — required for speech recognition
- Ollama — [ollama.com](https://ollama.com)
- Internet connection — required for Edge TTS voice

---

## Setup (First Time Only)

### 1. Install Python
Download from [python.org](https://python.org) and install. Choose Python 3.8 or newer.

### 2. Install Ollama
Download from [ollama.com](https://ollama.com) and install. Then pull the AI model:
```bash
ollama pull llama3.2
```

### 3. Install Python dependencies
Open a terminal in the `nat-bot` folder and run:
```bash
pip install flask requests edge-tts
```

### 4. Add your avatar images
Place your expression images inside the `templates/` folder. You need:
```
neutral_closed.png   neutral_open.png
angry_closed.png     angry_open.png
sad_closed.png       sad_open.png
```
All images should be the same size, same position — only the expression and mouth differ.

---

## Running NAT

### Every time you want to run it:
```bash
python server.py
```

Then open **Google Chrome** and go to:
```
http://localhost:3000
```

NAT will automatically deliver its opening statement. After it finishes, press the mic button and start debating.

---

## How to Use

| Action | How |
|---|---|
| Start speaking | Tap the 🎤 mic button |
| Stop speaking | Tap the mic button again |
| Cancel and rephrase | Say "stop", "wait", "cancel", or "repeat" |
| Cancel immediately | Press the `Escape` key |
| End session | Close the browser tab |

---

## Customisation

All customisation is done inside `server.py` — open it in any text editor.

### Change the debate topic
Find `DEBATE_STYLE` and replace the text:
```python
DEBATE_STYLE = """
Your new debate position here.
"""
```

### Change the AI model
Find `OLLAMA_MODEL` and change it:
```python
OLLAMA_MODEL = "llama3.2"   # change to any model you have pulled
```

Other free models to try:
```bash
ollama pull mistral
ollama pull phi3
ollama pull gemma2
```

### Change the voice
Find `VOICE` inside the `/api/tts` route:
```python
VOICE = "en-GB-SoniaNeural"
```

Deep female voices:
- `en-GB-SoniaNeural` — deep British female
- `en-AU-NatashaNeural` — rich Australian female
- `en-IE-EmilyNeural` — deep Irish female

Deep male voices:
- `en-US-ChristopherNeural` — authoritative American male
- `en-GB-RyanNeural` — deep British male
- `en-US-GuyNeural` — strong American male

### Change voice pitch and speed
Find the `rate` and `pitch` settings:
```python
communicate = edge_tts.Communicate(text, VOICE, rate="+30%", pitch="+60Hz")
```
- `rate` — speed: `-30%` (slower) to `+50%` (faster)
- `pitch` — tone: `-50Hz` (deeper) to `+50Hz` (higher)

### Change avatar size
Find in `index.html` CSS:
```css
.avatar-wrap {
  width: 210px; height: 210px;
```
Increase both values to make the avatar bigger.

### Change mouth animation speed
Find in `index.html`:
```javascript
}, 300)   // milliseconds — lower = faster, higher = slower
```

---

## How NAT Debates

NAT follows a strict pipeline every time you speak:

```
Your voice
    ↓
Web Speech API converts speech to text
    ↓
Text + full conversation history sent to Flask backend
    ↓
Ollama (llama3.2) generates a response with an emotion tag
    ↓
parse_emotion() strips the tag, identifies emotion
    ↓
Emotion sent to frontend → avatar updates (glow, ring colour)
    ↓
Reply text sent to Edge TTS → mp3 audio generated
    ↓
Audio plays + mouth animation starts simultaneously
    ↓
Typewriter effect displays text in the textbox
```

---

## Emotion System

NAT labels every response with one of four emotions. Each emotion changes the avatar appearance and voice delivery:

| Emotion | When used | Avatar | Voice |
|---|---|---|---|
| 😠 Angry | Attacking a weak argument or fallacy | Red glow, red ring | Faster, firm |
| 😏 Smug | Just made an unanswerable point | Green glow, sparkle | Slightly slower |
| 😢 Sad | Briefly acknowledging opponent's point | Blue glow, tears | Slower, softer |
| 😊 Happy | Finding common ground | Gold glow, blush | Warmer, brighter |

---

## Troubleshooting

**"Could not connect to ollama"**
Ollama is not running. Open the Ollama app from your Applications or Start Menu, then restart:
```bash
python server.py
```

**Mic not working**
Speech recognition only works in Google Chrome. Make sure you are not using Safari, Firefox, or Edge.

**No sound / voice not playing**
Make sure edge-tts is installed:
```bash
pip install edge-tts
```
Also check your internet connection — Edge TTS requires internet to generate audio.

**Avatar images not showing**
Check that all image files are inside the `templates/` folder and named exactly as listed in the Project Structure section above.

**500 error on /api/tts**
Check the terminal for the error message. Most common causes:
- No internet connection (Edge TTS needs internet)
- edge-tts not installed (`pip install edge-tts`)
- Invalid voice name — check the voice list above

---

## Dependencies

```
flask       — web server
requests    — HTTP calls to Ollama
edge-tts    — Microsoft neural text-to-speech
```

Install all at once:
```bash
pip install flask requests edge-tts
```
