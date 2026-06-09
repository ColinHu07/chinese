# Stage 2: Bluetooth Microphone

Reuse the local translator with any Bluetooth input device, including headsets or glasses if the operating system exposes them as microphones.

## Quick Start

From this folder:

```bash
python scripts/list_audio_devices.py
python scripts/live_bluetooth_mic.py --device-index <INDEX> --model base
```

Use `auto` for the OS default input:

```bash
python scripts/live_bluetooth_mic.py --device-index auto --model base
```

If Ray-Ban Meta glasses do not appear as an input microphone, prove the code path with a normal Bluetooth headset first, then move to Stage 3.

## Optional Baidu Mode

If you want to compare Whisper's built-in Chinese-to-English translation against Baidu:

```bash
export BAIDU_TRANSLATE_APP_ID="your_app_id"
export BAIDU_TRANSLATE_SECRET_KEY="your_secret_key"

python scripts/live_bluetooth_mic.py \
  --mode baidu \
  --device-index <INDEX> \
  --model base \
  --chunk-seconds 3 \
  --overlap-seconds 0.5 \
  --show-source
```

To mirror captions to the browser/glasses display prototype:

```bash
python scripts/live_bluetooth_mic.py \
  --mode baidu \
  --device-index <INDEX> \
  --model base \
  --chunk-seconds 3 \
  --overlap-seconds 0.5 \
  --show-source \
  --display-url http://127.0.0.1:8000/caption
```

Baidu mode sends Chinese transcript text to Baidu, so it is not offline.
