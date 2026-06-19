/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 *
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 */

//
// MicTestViewModel.swift
//
// Streams the active iOS microphone route to the local Whisper WebSocket server.
// When Ray-Ban/Meta glasses are selected as the Bluetooth HFP route, this is
// the closest available path for testing glasses microphone captions.
//

import AVFoundation
import Foundation
import Observation

@Observable
@MainActor
final class MicTestViewModel {
  var serverURLString: String {
    didSet {
      UserDefaults.standard.set(serverURLString, forKey: Self.serverURLDefaultsKey)
    }
  }

  var isSocketConnected = false
  var isStreaming = false
  var autoSendToGlasses = true
  var statusText = "Mic test stopped"
  var routeText = "No active route"
  var audioLevel: Double = 0
  var captionCount = 0
  var lastCaption: TranslatorCaption?
  var lastErrorMessage: String?

  @ObservationIgnored private let engine = AVAudioEngine()
  @ObservationIgnored private var converter: AVAudioConverter?
  @ObservationIgnored private var outputFormat: AVAudioFormat?
  @ObservationIgnored private var socket: URLSessionWebSocketTask?
  @ObservationIgnored private let decoder = JSONDecoder()
  @ObservationIgnored private var lastMeterUpdate = Date.distantPast

  private static let serverURLDefaultsKey = "translator.mic.websocket.url"
  private static let defaultServerURL = "ws://192.168.1.201:8765"

  init() {
    self.serverURLString =
      UserDefaults.standard.string(forKey: Self.serverURLDefaultsKey) ?? Self.defaultServerURL
    refreshRoute()
  }

  func connect(displayViewModel: DisplayViewModel) {
    disconnect()

    guard let url = URL(string: serverURLString) else {
      statusText = "Invalid mic server URL"
      lastErrorMessage = "Use a ws:// or wss:// URL."
      return
    }

    statusText = "Checking local network"
    lastErrorMessage = nil
    LocalNetworkPermissionProbe.shared.requestIfNeeded { [weak self, weak displayViewModel] in
      Task { @MainActor in
        guard let self else { return }
        self.openSocket(url, displayViewModel: displayViewModel)
      }
    }
  }

  private func openSocket(_ url: URL, displayViewModel: DisplayViewModel?) {
    let socket = URLSession.shared.webSocketTask(with: url)
    self.socket = socket
    isSocketConnected = true
    statusText = "Mic server connecting"
    lastErrorMessage = nil
    socket.resume()
    receiveLoop(displayViewModel: displayViewModel)
  }

  func disconnect() {
    stopMic()
    socket?.cancel(with: .goingAway, reason: nil)
    socket = nil
    isSocketConnected = false
    if statusText != "Mic permission denied" {
      statusText = "Mic server disconnected"
    }
  }

  func startMic() {
    guard isSocketConnected else {
      lastErrorMessage = "Connect to the mic server first."
      return
    }

    AVAudioApplication.requestRecordPermission { [weak self] granted in
      Task { @MainActor in
        guard let self else { return }
        if granted {
          self.startMicAfterPermission()
        } else {
          self.statusText = "Mic permission denied"
          self.lastErrorMessage = "Enable microphone permission for this app in iOS Settings."
        }
      }
    }
  }

  func stopMic() {
    guard isStreaming else {
      refreshRoute()
      return
    }

    engine.inputNode.removeTap(onBus: 0)
    engine.stop()
    isStreaming = false
    audioLevel = 0
    statusText = isSocketConnected ? "Mic stopped" : "Mic test stopped"
    refreshRoute()
  }

  func clear(displayViewModel: DisplayViewModel) {
    lastCaption = nil
    Task {
      await displayViewModel.clearTranslatorCaption(
        onDemo: { [weak self, weak displayViewModel] in
          Task { @MainActor in
            guard let self, let displayViewModel else { return }
            await self.sendSyntheticRouteCaption(displayViewModel: displayViewModel)
          }
        }
      )
    }
  }

  func sendSyntheticRouteCaption(displayViewModel: DisplayViewModel) async {
    let caption = TranslatorCaption(
      mode: .zhToEn,
      sourceText: routeText,
      translatedText: "Mic route: \(routeText)",
      isFinal: true,
      latencyMs: nil,
      createdAt: Date()
    )
    lastCaption = caption
    await sendCaptionToGlasses(caption, displayViewModel: displayViewModel)
  }

  func refreshRoute() {
    let session = AVAudioSession.sharedInstance()
    let inputs = session.currentRoute.inputs.map { "\($0.portName) (\($0.portType.rawValue))" }
    let outputs = session.currentRoute.outputs.map { "\($0.portName) (\($0.portType.rawValue))" }

    if inputs.isEmpty && outputs.isEmpty {
      routeText = "No active route"
    } else if outputs.isEmpty {
      routeText = inputs.joined(separator: ", ")
    } else {
      routeText = "\(inputs.joined(separator: ", ")) -> \(outputs.joined(separator: ", "))"
    }
  }

  private func startMicAfterPermission() {
    if isStreaming { return }

    do {
      let session = AVAudioSession.sharedInstance()
      try session.setCategory(
        .playAndRecord,
        mode: .voiceChat,
        options: [.allowBluetoothHFP, .defaultToSpeaker]
      )
      try session.setPreferredSampleRate(16_000)
      try session.setActive(true)
      preferBluetoothHFPInput(session)
      refreshRoute()

      let input = engine.inputNode
      let inputFormat = input.outputFormat(forBus: 0)
      guard let outputFormat = AVAudioFormat(
        commonFormat: .pcmFormatInt16,
        sampleRate: 16_000,
        channels: 1,
        interleaved: true
      ) else {
        throw MicTestError.cannotCreateOutputFormat
      }

      self.outputFormat = outputFormat
      self.converter = AVAudioConverter(from: inputFormat, to: outputFormat)

      input.removeTap(onBus: 0)
      input.installTap(onBus: 0, bufferSize: 2048, format: inputFormat) { [weak self] buffer, _ in
        self?.convertAndSend(buffer, inputFormat: inputFormat)
      }

      engine.prepare()
      try engine.start()
      isStreaming = true
      statusText = "Mic streaming"
    } catch {
      stopMic()
      statusText = "Mic start failed"
      lastErrorMessage = error.localizedDescription
    }
  }

  private func preferBluetoothHFPInput(_ session: AVAudioSession) {
    guard let inputs = session.availableInputs else { return }

    let preferredInput = inputs.first { input in
      input.portType == .bluetoothHFP
        || input.portName.localizedCaseInsensitiveContains("ray-ban")
        || input.portName.localizedCaseInsensitiveContains("meta")
    }

    if let preferredInput {
      try? session.setPreferredInput(preferredInput)
    }
  }

  private nonisolated func convertAndSend(_ buffer: AVAudioPCMBuffer, inputFormat: AVAudioFormat) {
    Task { @MainActor [weak self] in
      self?.convertAndSendOnMain(buffer, inputFormat: inputFormat)
    }
  }

  private func convertAndSendOnMain(_ buffer: AVAudioPCMBuffer, inputFormat: AVAudioFormat) {
    guard let converter, let outputFormat else { return }

    let ratio = outputFormat.sampleRate / inputFormat.sampleRate
    let outputCapacity = AVAudioFrameCount(Double(buffer.frameLength) * ratio) + 1
    guard let outputBuffer = AVAudioPCMBuffer(pcmFormat: outputFormat, frameCapacity: outputCapacity) else {
      return
    }

    let inputProvider = AudioConverterInputProvider(buffer: buffer)
    var conversionError: NSError?
    let inputBlock: AVAudioConverterInputBlock = { _, status in
      inputProvider.nextBuffer(status: status)
    }

    converter.convert(to: outputBuffer, error: &conversionError, withInputFrom: inputBlock)
    guard conversionError == nil, outputBuffer.frameLength > 0 else { return }

    let audioBuffer = outputBuffer.audioBufferList.pointee.mBuffers
    guard let bytes = audioBuffer.mData else { return }
    let data = Data(bytes: bytes, count: Int(audioBuffer.mDataByteSize))
    updateAudioLevel(data)
    socket?.send(.data(data)) { [weak self] error in
      if let error {
        Task { @MainActor in
          self?.lastErrorMessage = "Audio send failed: \(error.localizedDescription)"
        }
      }
    }
  }

  private func updateAudioLevel(_ data: Data) {
    let now = Date()
    guard now.timeIntervalSince(lastMeterUpdate) > 0.08 else { return }
    lastMeterUpdate = now

    let sampleCount = data.count / MemoryLayout<Int16>.size
    guard sampleCount > 0 else {
      audioLevel = 0
      return
    }

    let sumSquares = data.withUnsafeBytes { rawBuffer -> Double in
      let samples = rawBuffer.bindMemory(to: Int16.self)
      return samples.reduce(0.0) { partial, sample in
        let normalized = Double(sample) / Double(Int16.max)
        return partial + normalized * normalized
      }
    }

    let rms = sqrt(sumSquares / Double(sampleCount))
    audioLevel = min(max(rms * 8.0, 0), 1)
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
          self.stopMic()
          self.socket = nil
          self.isSocketConnected = false
          self.statusText = "Mic socket closed"
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
    guard let message = try? decoder.decode(MicServerMessage.self, from: data) else {
      return
    }

    switch message.type {
    case "ready":
      statusText = "Mic server ready"
      isSocketConnected = true
    case "caption":
      guard let text = message.text, !text.isEmpty else { return }
      let caption = TranslatorCaption(
        mode: .zhToEn,
        sourceText: "",
        translatedText: text,
        isFinal: true,
        latencyMs: message.inferenceSeconds.map { Int($0 * 1000) },
        createdAt: Date()
      )
      lastCaption = caption
      captionCount += 1
      statusText = isStreaming ? "Mic streaming" : "Caption received"

      guard autoSendToGlasses, let displayViewModel else { return }
      Task { await sendCaptionToGlasses(caption, displayViewModel: displayViewModel) }
    case "error":
      lastErrorMessage = message.message ?? "Mic server error"
    default:
      break
    }
  }

  private func sendCaptionToGlasses(
    _ caption: TranslatorCaption,
    displayViewModel: DisplayViewModel
  ) async {
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

private struct MicServerMessage: Decodable {
  let type: String
  let text: String?
  let message: String?
  let inferenceSeconds: Double?

  enum CodingKeys: String, CodingKey {
    case type
    case text
    case message
    case inferenceSeconds = "inference_seconds"
  }
}

private final class AudioConverterInputProvider {
  private let buffer: AVAudioPCMBuffer
  private var didProvideInput = false

  init(buffer: AVAudioPCMBuffer) {
    self.buffer = buffer
  }

  func nextBuffer(status: UnsafeMutablePointer<AVAudioConverterInputStatus>) -> AVAudioBuffer? {
    if didProvideInput {
      status.pointee = .noDataNow
      return nil
    }

    didProvideInput = true
    status.pointee = .haveData
    return buffer
  }
}

private enum MicTestError: LocalizedError {
  case cannotCreateOutputFormat

  var errorDescription: String? {
    switch self {
    case .cannotCreateOutputFormat:
      "Unable to create 16 kHz mono PCM output format."
    }
  }
}
