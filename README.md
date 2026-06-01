# Chinese Translator Prototype

No-API Mandarin-to-English live caption translator prototype.

## Stages

1. `01_laptop_microphone/` - Local laptop microphone and audio-file translation using local Whisper.
2. `02_bluetooth_microphone/` - Bluetooth microphone and glasses-as-mic experiments using the same local translator core.
3. `03_meta_wearables_mobile_bridge/` - WebSocket server plus iOS bridge source for mobile audio capture.

The first run may download Whisper model weights. After that, inference runs locally.

## Quick Start

```bash
cd 01_laptop_microphone
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python scripts/list_audio_devices.py
python scripts/live_laptop_mic.py --model base --device-index auto
```

For Bluetooth input:

```bash
cd ../02_bluetooth_microphone
python scripts/list_audio_devices.py
python scripts/live_bluetooth_mic.py --device-index <INDEX> --model base
```

For the mobile bridge:

```bash
cd ../03_meta_wearables_mobile_bridge/server
pip install -r requirements.txt
python scripts/local_ws_translator_server.py --host 0.0.0.0 --port 8765 --model base
```
