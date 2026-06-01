# Stage 3: Meta Wearables Mobile Bridge

Capture or route audio through a mobile app, stream audio to a local laptop translator, and send captions back to mobile.

The Meta Wearables DAT iOS sample is copied under:

`mobile/ios/vendor/meta-wearables-dat-ios/`

## Local Server

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python scripts/local_ws_translator_server.py --host 0.0.0.0 --port 8765 --model base
```

## iOS Bridge

The starter SwiftUI source is under:

`mobile/ios/translator_bridge_app/TranslatorBridgeApp/`

Create an iOS app target in Xcode, add those files, then set the server URL to your laptop's LAN IP.
