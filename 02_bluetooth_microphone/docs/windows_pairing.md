# Windows Pairing Notes

1. Open Settings -> Bluetooth & devices.
2. Pair the headset or glasses.
3. Open Settings -> System -> Sound -> Input.
4. Select the Bluetooth microphone.
5. Run:

```powershell
python scripts\list_audio_devices.py
python scripts\live_bluetooth_mic.py --device-index <INDEX> --model base
```

If the device only appears as headphones and not as a microphone, the OS is not exposing a usable input device for Stage 2.
