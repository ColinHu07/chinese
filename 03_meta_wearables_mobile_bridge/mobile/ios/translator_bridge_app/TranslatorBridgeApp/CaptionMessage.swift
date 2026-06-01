import Foundation

struct ServerMessage: Decodable {
    let type: String
    let clientId: String?
    let chunkId: Int?
    let text: String?
    let rawText: String?
    let inferenceSeconds: Double?

    enum CodingKeys: String, CodingKey {
        case type
        case clientId = "client_id"
        case chunkId = "chunk_id"
        case text
        case rawText = "raw_text"
        case inferenceSeconds = "inference_seconds"
    }
}

struct CaptionLine: Identifiable {
    let id = UUID()
    let text: String
    let receivedAt: Date
}
