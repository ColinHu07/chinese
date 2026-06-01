# iOS Audio Routing

The starter iOS bridge uses:

- `AVAudioSession.Category.playAndRecord`
- `AVAudioSession.Mode.voiceChat`
- `.allowBluetooth`
- `AVAudioEngine` input tap
- `AVAudioConverter` to 16 kHz mono int16 PCM

When supported glasses are paired, iOS may route the microphone through the Bluetooth hands-free profile. If that does not happen, confirm routing with a normal Bluetooth headset first.
