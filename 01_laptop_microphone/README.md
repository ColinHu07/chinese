# Stage 1: Laptop Microphone

Capture audio from the laptop microphone, translate Mandarin speech locally, and print English captions.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Install OS audio dependencies first:

- macOS: `brew install ffmpeg portaudio`
- Ubuntu/Debian: `sudo apt install ffmpeg portaudio19-dev`
- Windows: install ffmpeg and add it to `PATH`

## Translate a File

```bash
python scripts/translate_file.py --file samples/mandarin_test.wav --model base
```

## Live Laptop Mic

```bash
python scripts/list_audio_devices.py
python scripts/live_laptop_mic.py --model base --device-index auto
```

Use a specific input device:

```bash
python scripts/live_laptop_mic.py --model base --device-index 2 --chunk-seconds 5 --overlap-seconds 1
```

Logs are written to `logs/session_YYYYMMDD_HHMMSS.jsonl`.

## Optional Baidu Chinese -> English Mode

The default mode asks Whisper to translate Chinese audio directly into English. To compare that with Baidu, use Baidu mode:

```text
Chinese audio -> Whisper Chinese transcript -> Baidu Chinese-to-English text translation
```

Set credentials first:

```bash
export BAIDU_TRANSLATE_APP_ID="your_app_id"
export BAIDU_TRANSLATE_SECRET_KEY="your_secret_key"
```

Then run:

```bash
python scripts/live_laptop_mic.py \
  --mode baidu \
  --model base \
  --device-index auto \
  --chunk-seconds 3 \
  --overlap-seconds 0.5 \
  --show-source
```

For a file:

```bash
python scripts/translate_file.py --file samples/mandarin_test.wav --mode baidu --show-source
```

Baidu mode is a cloud API path. It sends Chinese transcript text to Baidu and requires network access plus API credentials.
