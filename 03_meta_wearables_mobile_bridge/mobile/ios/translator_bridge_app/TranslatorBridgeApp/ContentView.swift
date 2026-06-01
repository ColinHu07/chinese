import SwiftUI

struct ContentView: View {
    @StateObject private var socketClient = CaptionSocketClient()
    @StateObject private var audioStreamer = AudioStreamer()
    @State private var serverURL = "ws://192.168.1.10:8765"

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                TextField("Server URL", text: $serverURL)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .keyboardType(.URL)
                    .textFieldStyle(.roundedBorder)

                HStack {
                    Button(socketClient.isConnected ? "Disconnect" : "Connect") {
                        if socketClient.isConnected {
                            socketClient.disconnect()
                        } else {
                            socketClient.connect(urlString: serverURL)
                        }
                    }
                    .buttonStyle(.borderedProminent)

                    Button(audioStreamer.isStreaming ? "Stop Mic" : "Start Mic") {
                        if audioStreamer.isStreaming {
                            audioStreamer.stop()
                        } else {
                            startAudio()
                        }
                    }
                    .buttonStyle(.bordered)
                    .disabled(!socketClient.isConnected)
                }

                VStack(alignment: .leading, spacing: 4) {
                    Text(socketClient.statusText)
                    Text(audioStreamer.statusText)
                }
                .font(.footnote)
                .foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)

                List(socketClient.captions.reversed()) { caption in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(caption.text)
                            .font(.body)
                        Text(caption.receivedAt, style: .time)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .padding()
            .navigationTitle("Translator Bridge")
            .onAppear {
                audioStreamer.onAudioFrame = { data in
                    Task { @MainActor in
                        socketClient.sendAudio(data)
                    }
                }
            }
            .onDisappear {
                audioStreamer.stop()
                socketClient.disconnect()
            }
        }
    }

    private func startAudio() {
        do {
            try audioStreamer.start()
        } catch {
            audioStreamer.stop()
        }
    }
}

#Preview {
    ContentView()
}
