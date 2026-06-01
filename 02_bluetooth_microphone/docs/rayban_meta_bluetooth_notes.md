# Ray-Ban Meta Bluetooth Notes

Stage 2 only works if the operating system exposes the glasses as a normal audio input device.

Expected flow:

```text
Ray-Ban Meta microphone
-> OS Bluetooth audio input
-> sounddevice device index
-> local Whisper translator
```

If the glasses appear for playback but not recording, use Stage 3. That path routes audio through a mobile app and streams it to the laptop translator.
