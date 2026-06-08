# English-to-Chinese Display Caption Prototype

Display-only prototype for English-to-Simplified-Chinese captions on a 600x600 browser or Meta Ray-Ban Display Web App surface.

This stage does not capture microphone audio and does not run Whisper. It proves the display path first.

## Run Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Send a test caption:

```bash
curl -X POST http://localhost:8000/test-caption \
  -H "Content-Type: application/json" \
  -d '{"source_text":"Where is the train station?","target_text":"火车站在哪里？"}'
```

## Open Display App

Open `display-webapp/index.html` in a desktop browser. It works with static samples if the backend is not running.

If the backend is running, the app connects to `window.CAPTION_WS_URL` from `display-webapp/config.js`.

## Ray-Ban Display Notes

For glasses testing, host the web app at a public HTTPS URL and use a public `wss://` caption endpoint. A deployed HTTPS web app should not depend on `ws://localhost`.

Web App microphone capture is intentionally out of scope. The Web App is only a caption renderer.

## Optional Argos Backend

The default `requirements.txt` intentionally uses the mock backend only. Argos is scaffolded but optional because its install can be Python-version sensitive.

To experiment with Argos later:

```bash
pip install -r requirements-argos.txt
TRANSLATOR_BACKEND=argos uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

If Argos has no English-to-Chinese package installed, the backend raises a setup message and you can switch back to `TRANSLATOR_BACKEND=mock`.
