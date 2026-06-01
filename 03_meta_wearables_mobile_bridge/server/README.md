# Local Translator Server

Runs local Whisper translation for audio streamed from a phone.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python scripts/local_ws_translator_server.py --host 0.0.0.0 --port 8765 --model base
```

The server accepts binary PCM frames from one or more clients and returns JSON caption messages.
