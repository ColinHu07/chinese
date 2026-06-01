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
