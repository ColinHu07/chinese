import AVFoundation
import Combine
import Foundation

final class AudioStreamer: ObservableObject {
    @Published private(set) var isStreaming = false
    @Published private(set) var statusText = "Mic stopped"

    var onAudioFrame: ((Data) -> Void)?

    private let engine = AVAudioEngine()
    private var converter: AVAudioConverter?
    private var outputFormat: AVAudioFormat?

    func start() throws {
        if isStreaming { return }

        let session = AVAudioSession.sharedInstance()
        try session.setCategory(
            .playAndRecord,
            mode: .voiceChat,
            options: [.allowBluetooth, .defaultToSpeaker]
        )
        try session.setPreferredSampleRate(16_000)
        try session.setActive(true)

        let input = engine.inputNode
        let inputFormat = input.outputFormat(forBus: 0)
        guard let outputFormat = AVAudioFormat(
            commonFormat: .pcmFormatInt16,
            sampleRate: 16_000,
            channels: 1,
            interleaved: true
        ) else {
            throw AudioStreamerError.cannotCreateOutputFormat
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
    }

    func stop() {
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
        isStreaming = false
        statusText = "Mic stopped"
    }

    private func convertAndSend(_ buffer: AVAudioPCMBuffer, inputFormat: AVAudioFormat) {
        guard let converter, let outputFormat else { return }

        let ratio = outputFormat.sampleRate / inputFormat.sampleRate
        let outputCapacity = AVAudioFrameCount(Double(buffer.frameLength) * ratio) + 1
        guard let outputBuffer = AVAudioPCMBuffer(pcmFormat: outputFormat, frameCapacity: outputCapacity) else {
            return
        }

        var didProvideInput = false
        var conversionError: NSError?
        let inputBlock: AVAudioConverterInputBlock = { _, status in
            if didProvideInput {
                status.pointee = .noDataNow
                return nil
            }
            didProvideInput = true
            status.pointee = .haveData
            return buffer
        }

        converter.convert(to: outputBuffer, error: &conversionError, withInputFrom: inputBlock)
        guard conversionError == nil, outputBuffer.frameLength > 0 else { return }

        let audioBuffer = outputBuffer.audioBufferList.pointee.mBuffers
        guard let bytes = audioBuffer.mData else { return }
        let data = Data(bytes: bytes, count: Int(audioBuffer.mDataByteSize))
        onAudioFrame?(data)
    }
}

enum AudioStreamerError: Error {
    case cannotCreateOutputFormat
}
