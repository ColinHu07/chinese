import Combine
import Foundation

@MainActor
final class CaptionSocketClient: ObservableObject {
    @Published var isConnected = false
    @Published var statusText = "Disconnected"
    @Published var captions: [CaptionLine] = []

    private var socket: URLSessionWebSocketTask?
    private let decoder = JSONDecoder()

    func connect(urlString: String) {
        disconnect()
        guard let url = URL(string: urlString) else {
            statusText = "Invalid server URL"
            return
        }

        let socket = URLSession.shared.webSocketTask(with: url)
        self.socket = socket
        socket.resume()
        isConnected = true
        statusText = "Connected"
        receiveLoop()
    }

    func disconnect() {
        socket?.cancel(with: .goingAway, reason: nil)
        socket = nil
        isConnected = false
        statusText = "Disconnected"
    }

    func sendAudio(_ data: Data) {
        guard let socket else { return }
        socket.send(.data(data)) { [weak self] error in
            if let error {
                Task { @MainActor in
                    self?.statusText = "Send failed: \(error.localizedDescription)"
                }
            }
        }
    }

    private func receiveLoop() {
        socket?.receive { [weak self] result in
            Task { @MainActor in
                guard let self else { return }
                switch result {
                case .success(let message):
                    self.handle(message)
                    self.receiveLoop()
                case .failure(let error):
                    self.statusText = "Socket closed: \(error.localizedDescription)"
                    self.isConnected = false
                }
            }
        }
    }

    private func handle(_ message: URLSessionWebSocketTask.Message) {
        switch message {
        case .string(let text):
            guard let data = text.data(using: .utf8) else { return }
            handleJSON(data)
        case .data(let data):
            handleJSON(data)
        @unknown default:
            break
        }
    }

    private func handleJSON(_ data: Data) {
        guard let message = try? decoder.decode(ServerMessage.self, from: data) else {
            return
        }

        if message.type == "ready" {
            statusText = "Server ready"
            return
        }

        if message.type == "caption", let text = message.text, !text.isEmpty {
            captions.append(CaptionLine(text: text, receivedAt: Date()))
            if captions.count > 100 {
                captions.removeFirst(captions.count - 100)
            }
        }
    }
}
