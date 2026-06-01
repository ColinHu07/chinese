# Translator Bridge App

Minimal SwiftUI source skeleton for an iOS microphone-to-WebSocket bridge.

This folder is intentionally separate from the vendored Meta DAT sample. Start here for the translator bridge, then pull DAT-specific registration/session pieces from:

`../vendor/meta-wearables-dat-ios/`

## Current Flow

```text
iPhone microphone or Bluetooth HFP input
-> AVAudioEngine
-> 16 kHz mono int16 PCM
-> WebSocket binary frames
-> laptop local translator server
-> JSON caption messages
-> SwiftUI captions
```

Create an iOS app target in Xcode and add the files under `TranslatorBridgeApp/`.
