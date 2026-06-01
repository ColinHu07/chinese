# macOS Pairing Notes

1. Open System Settings.
2. Pair the Bluetooth headset or glasses.
3. Go to Sound -> Input.
4. Select the Bluetooth device as the input microphone.
5. Run:

```bash
python scripts/list_audio_devices.py
```

If the device appears, run:

```bash
python scripts/live_bluetooth_mic.py --device-index <INDEX> --model base
```

Bluetooth microphone quality may be lower than the laptop microphone because many devices switch to a headset profile for mic input.
