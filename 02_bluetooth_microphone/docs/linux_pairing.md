# Linux Pairing Notes

Pair with the headset or glasses through your desktop Bluetooth settings.

For microphone input, Linux often needs the Bluetooth profile set to HFP/HSP. With PipeWire or PulseAudio tools, confirm that the device has an input source.

Then run:

```bash
python scripts/list_audio_devices.py
python scripts/live_bluetooth_mic.py --device-index <INDEX> --model base
```

If the microphone does not appear, test with a known-working Bluetooth headset before debugging glasses-specific behavior.
