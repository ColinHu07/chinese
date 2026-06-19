/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 *
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 */

//
// TranslatorCaptionViewModel.swift
//
// Receives caption payloads from the local FastAPI backend and pushes them to
// the wearable display through DisplayViewModel.
//

import Foundation
import Observation

@Observable
@MainActor
final class TranslatorCaptionViewModel {
  var serverURLString: String {
    didSet {
      UserDefaults.standard.set(serverURLString, forKey: Self.serverURLDefaultsKey)
    }
  }

  var isSocketConnected: Bool = false
  var autoSendToGlasses: Bool = true
  var isPaused: Bool = false
  var statusText: String = "Not connected"
  var lastCaption: TranslatorCaption?
  var captionCount: Int = 0
  var lastErrorMessage: String?

  @ObservationIgnored private var socket: URLSessionWebSocketTask?
  @ObservationIgnored private let decoder = JSONDecoder()

  private static let serverURLDefaultsKey = "translator.caption.websocket.url"
  private static let defaultServerURL = "ws://192.168.1.201:8000/ws/captions"

  init() {
    self.serverURLString =
      UserDefaults.standard.string(forKey: Self.serverURLDefaultsKey) ?? Self.defaultServerURL
  }

  func showReady(displayViewModel: DisplayViewModel) {
    Task {
      await displayViewModel.sendTranslatorReady(
        serverURL: serverURLString,
        onDemo: { [weak self, weak displayViewModel] in
          Task { @MainActor in
            guard let self, let displayViewModel else { return }
            await self.sendDemo(displayViewModel: displayViewModel)
          }
        }
      )
    }
  }

  func connect(displayViewModel: DisplayViewModel) {
    disconnect()

    guard let url = URL(string: serverURLString) else {
      statusText = "Invalid WebSocket URL"
      lastErrorMessage = "Use a ws:// or wss:// URL."
      return
    }

    let socket = URLSession.shared.webSocketTask(with: url)
    self.socket = socket
    isSocketConnected = true
    statusText = "Connecting"
    lastErrorMessage = nil

    socket.resume()
    Task {
      await displayViewModel.sendTranslatorWaiting(
        serverURL: serverURLString,
        onDemo: { [weak self, weak displayViewModel] in
          Task { @MainActor in
            guard let self, let displayViewModel else { return }
            await self.sendDemo(displayViewModel: displayViewModel)
          }
        }
      )
    }
    receiveLoop(displayViewModel: displayViewModel)
  }

  func disconnect() {
    socket?.cancel(with: .goingAway, reason: nil)
    socket = nil
    isSocketConnected = false
    statusText = "Disconnected"
  }

  func togglePause() {
    isPaused.toggle()
    statusText = isPaused ? "Paused" : (isSocketConnected ? "Listening" : "Not connected")
  }

  func clear(displayViewModel: DisplayViewModel) {
    lastCaption = nil
    Task {
      await displayViewModel.clearTranslatorCaption(
        onDemo: { [weak self, weak displayViewModel] in
          Task { @MainActor in
            guard let self, let displayViewModel else { return }
            await self.sendDemo(displayViewModel: displayViewModel)
          }
        }
      )
    }
  }

  func sendDemo(displayViewModel: DisplayViewModel) async {
    let caption = TranslatorCaption.demo
    lastCaption = caption
    captionCount += 1
    await displayViewModel.sendTranslatorCaption(
      caption,
      onClear: { [weak self, weak displayViewModel] in
        Task { @MainActor in
          guard let self, let displayViewModel else { return }
          self.clear(displayViewModel: displayViewModel)
        }
      }
    )
  }

  private func receiveLoop(displayViewModel: DisplayViewModel?) {
    socket?.receive { [weak self, weak displayViewModel] result in
      Task { @MainActor in
        guard let self else { return }

        switch result {
        case .success(let message):
          self.handle(message, displayViewModel: displayViewModel)
          if self.socket != nil {
            self.receiveLoop(displayViewModel: displayViewModel)
          }
        case .failure(let error):
          self.socket = nil
          self.isSocketConnected = false
          self.statusText = "Socket closed"
          self.lastErrorMessage = error.localizedDescription
        }
      }
    }
  }

  private func handle(
    _ message: URLSessionWebSocketTask.Message,
    displayViewModel: DisplayViewModel?
  ) {
    switch message {
    case .string(let text):
      guard let data = text.data(using: .utf8) else { return }
      handleJSON(data, displayViewModel: displayViewModel)
    case .data(let data):
      handleJSON(data, displayViewModel: displayViewModel)
    @unknown default:
      break
    }
  }

  private func handleJSON(_ data: Data, displayViewModel: DisplayViewModel?) {
    guard let message = try? decoder.decode(CaptionSocketMessage.self, from: data) else {
      return
    }

    if message.type == "status" {
      statusText = message.status ?? "Connected"
      isSocketConnected = true
      return
    }

    guard message.type == "caption" else { return }
    guard let translatedText = message.targetText, !translatedText.isEmpty else { return }

    let mode = TranslationMode(rawValue: message.mode ?? "") ?? .zhToEn
    let caption = TranslatorCaption(
      mode: mode,
      sourceText: message.sourceText ?? "",
      translatedText: translatedText,
      isFinal: message.isFinal ?? true,
      latencyMs: message.latencyMs,
      createdAt: Date()
    )

    lastCaption = caption
    captionCount += 1
    statusText = isPaused ? "Paused" : "Listening"

    guard autoSendToGlasses, !isPaused, let displayViewModel else { return }
    Task {
      await displayViewModel.sendTranslatorCaption(
        caption,
        onClear: { [weak self, weak displayViewModel] in
          Task { @MainActor in
            guard let self, let displayViewModel else { return }
            self.clear(displayViewModel: displayViewModel)
          }
        }
      )
    }
  }
}

private struct CaptionSocketMessage: Decodable {
  let type: String
  let status: String?
  let mode: String?
  let sourceText: String?
  let targetText: String?
  let isFinal: Bool?
  let latencyMs: Int?

  enum CodingKeys: String, CodingKey {
    case type
    case status
    case mode
    case sourceText = "source_text"
    case targetText = "target_text"
    case isFinal = "is_final"
    case latencyMs = "latency_ms"
  }
}
