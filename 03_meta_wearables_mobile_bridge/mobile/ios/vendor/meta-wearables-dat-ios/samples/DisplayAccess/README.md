# Display Translator App

An iOS prototype for sending live translation captions to Meta Ray-Ban Display glasses using the Meta Wearables Device Access Toolkit display module.

## Features

- Connect to Meta Ray-Ban Display glasses
- Send a simple translator status screen to the glasses
- Receive caption payloads from the local FastAPI backend over WebSocket
- Stream the active iOS microphone route to a local Whisper WebSocket server for glasses mic testing
- Push incoming Chinese-to-English captions to the glasses display
- Send a demo caption to verify the glasses display path
- Manage device registration and connection states
- Open firmware and glasses app update flows when required

## Prerequisites

- iOS 17.0+
- Xcode 14.0+
- Swift 5.0+
- Meta Wearables Device Access Toolkit (included as a dependency)
- A Meta Ray-Ban Display glasses device for testing

## Building the app

### Using Xcode

1. Clone this repository
1. Open the project in Xcode
1. Select your target device
1. Click the "Build" button or press `Cmd+B` to build the project
1. To run the app, click the "Run" button (▶️) or press `Cmd+R`

## Running the app

1. Turn 'Developer Mode' on in the Meta AI app.
1. Launch the app.
1. Press the "Register" button to complete app registration.
1. Start the caption backend on the Mac:
   ```bash
   cd /Users/owenhu/Documents/chinese/04_display_english_to_chinese
   source .venv/bin/activate
   uvicorn backend.server:app --host 0.0.0.0 --port 8000
   ```
1. In the iPhone app, set the live captions URL to your Mac's Wi-Fi IP, for example `ws://192.168.1.201:8000/ws/captions`.
1. Tap "Show" to send the translator screen to the glasses.
1. Tap "Demo" to verify a sample translation renders on the glasses.
1. Tap "Connect" to receive live captions from the backend.
1. Run the laptop mic translator with `--display-url http://127.0.0.1:8000/caption`.
1. To test whether iOS can use the glasses as the microphone, start the Stage 3 audio server:
   ```bash
   cd /Users/owenhu/Documents/chinese/03_meta_wearables_mobile_bridge/server
   python scripts/local_ws_translator_server.py --host 0.0.0.0 --port 8765 --model base
   ```
1. In the "Mic caption test" card, set the URL to your Mac's Wi-Fi IP, for example `ws://192.168.1.201:8765`, tap "Connect", then tap "Start Mic". The route line should show whether iOS selected a Bluetooth HFP input from the glasses.
1. If a firmware update is required, tap "Update firmware" in Settings.
1. If session start reports that the app on the glasses is outdated, the app opens Settings so you can tap "Update app on glasses".

## Troubleshooting

For issues related to the Meta Wearables Device Access Toolkit, please refer to the [developer documentation](https://wearables.developer.meta.com/docs/develop/) or visit our [discussions forum](https://github.com/facebook/meta-wearables-dat-ios/discussions)

## License

This source code is licensed under the license found in the LICENSE file in the root directory of this source tree.
