import CoreAIKit
import Foundation
import FoundationModels
import ImageIO

struct Command: Decodable, Sendable {
    let id: String
    let task: String
    let model: String
    let inputs: Inputs
    let options: Options
    struct Inputs: Decodable, Sendable {
        var prompt: String?
        var image_base64: String?
        var choices: [String]?
    }
    struct Options: Decodable, Sendable {
        var max_tokens: Int?
        var temperature: Double?
    }
}

// One serialized writer: progress callbacks can arrive on SDK worker threads.
final class Writer: @unchecked Sendable {
    private let lock = NSLock()
    func emit(_ id: String, _ type: String, _ payload: [String: Any] = [:]) {
        lock.lock(); defer { lock.unlock() }
        guard let bytes = try? JSONSerialization.data(withJSONObject: ["id": id, "type": type, "payload": payload], options: [.sortedKeys]) else { return }
        FileHandle.standardOutput.write(bytes)
        FileHandle.standardOutput.write(Data([10]))
    }
}
let writer = Writer()

@available(macOS 27, *)
actor Runner {
    let store: ModelStore
    var chat: ChatSession?
    var chatKey = ""
    var vision: KitVisionModel?
    var decider: TypedDecisions?
    init(directory: URL) { store = ModelStore(directory: directory) }

    func parts(_ id: String) throws -> [ModelID] {
        // Use the built-in release catalog ONLY; never the SDK's live catalog.
        guard let entry = ModelCatalog.builtin.entry(id: id), let revision = entry.revision else {
            throw NSError(domain: "GeneretiCore", code: 1, userInfo: [NSLocalizedDescriptionKey: "Model has no pinned release entry"])
        }
        if id == "qwen3-0.6b", let model = entry.modelID { return [model] }
        if id == "qwen3-vl-2b" {
            let vl = VLModelID.qwen3VL2B.pinned(revision)
            return [vl.decoder, vl.vision]
        }
        throw NSError(domain: "GeneretiCore", code: 2, userInfo: [NSLocalizedDescriptionKey: "Unsupported model"])
    }

    func requireLocal(_ parts: [ModelID]) throws -> [URL] {
        try parts.map { part in
            guard let url = store.localURL(for: part) else {
                throw NSError(domain: "GeneretiCore", code: 3, userInfo: [NSLocalizedDescriptionKey: "Model missing. Use the explicit Download action first."])
            }
            return url
        }
    }

    func run(_ c: Command) async {
        let start = Date()
        do {
            let models = try parts(c.model)
            if c.task == "model.download" {
                var bytes: Int64 = 0
                for part in models where !store.isCached(part) { bytes += try await store.remoteSize(of: part) }
                try FileManager.default.createDirectory(at: store.directory, withIntermediateDirectories: true)
                guard let free = store.availableBytes, free > bytes + 1_000_000_000 else {
                    throw NSError(domain: "GeneretiCore", code: 4, userInfo: [NSLocalizedDescriptionKey: "Not enough disk space (including 1 GB reserve)"])
                }
                for (index, part) in models.enumerated() {
                    let url = try await store.download(part, progress: { p in
                        writer.emit(c.id, "download_progress", ["fraction": (Double(index) + p.fraction) / Double(models.count), "completed_bytes": p.completedBytes, "total_bytes": p.totalBytes, "component": index, "file": p.currentFile])
                    })
                    // SDK offers sibling-revision fallback; this adapter explicitly rejects it.
                    guard url == store.localURL(for: part) else {
                        throw NSError(domain: "GeneretiCore", code: 5, userInfo: [NSLocalizedDescriptionKey: "Pinned revision unavailable; refusing stale cache fallback"])
                    }
                }
                writer.emit(c.id, "completed", ["content": ["model": c.model, "installed": true], "total_ms": Date().timeIntervalSince(start) * 1000])
                return
            }
            let urls = try requireLocal(models)
            let maxTokens = c.options.max_tokens ?? 256
            guard (1...2048).contains(maxTokens), let prompt = c.inputs.prompt else {
                throw NSError(domain: "GeneretiCore", code: 6, userInfo: [NSLocalizedDescriptionKey: "Invalid prompt or token limit"])
            }
            writer.emit(c.id, "load_progress", ["fraction": 0])
            let loadStart = Date()
            var warm = false
            var text = ""
            var firstTokenMS: Double? = nil
            var stats: [String: Any] = [:]
            if c.task == "decision.evaluate" {
                guard let choices = c.inputs.choices, (2...26).contains(choices.count) else {
                    throw NSError(domain: "GeneretiCore", code: 9, userInfo: [NSLocalizedDescriptionKey: "Qwen supports 2–26 decision choices"])
                }
                warm = decider != nil
                if decider == nil {
                    chat = nil; chatKey = ""; vision = nil
                    var config = TypedDecisions.Configuration()
                    config.temperature = 1 // Raw answer-slot distribution; no calibration claim.
                    decider = try await TypedDecisions(bundleAt: urls[0], configuration: config)
                }
                guard let decider else { return }
                let loadMS = Date().timeIntervalSince(loadStart) * 1000
                writer.emit(c.id, "started", ["warm": warm, "load_ms": loadMS])
                let answer = try await decider.decide(prompt, .choice("Which option best fits the state and its instructions?", choices))
                guard case .choice(let choice) = answer.value else { return }
                writer.emit(c.id, "completed", ["content": ["choice": choice.id, "scores": choice.probabilities],
                    "timings": ["load_ms": loadMS, "total_ms": Date().timeIntervalSince(start) * 1000, "warm": warm],
                    "probability_kind": "answer_slot_softmax_uncalibrated"])
                return
            } else if c.task == "text.generate" {
                let temperature = c.options.temperature ?? 0
                let key = "\(c.model):\(c.task):\(maxTokens):\(temperature)"
                warm = chat != nil && chatKey == key
                if !warm {
                    chat = nil; vision = nil; decider = nil
                    var config = ChatSession.Configuration()
                    config.maxResponseTokens = maxTokens
                    config.temperature = temperature == 0 ? nil : temperature
                    chat = try await ChatSession(bundleAt: urls[0], configuration: config)
                    chatKey = key
                }
                guard let chat else { return }
                await chat.reset() // Warm model, independent observations; no leaked chat history.
                let loadMS = Date().timeIntervalSince(loadStart) * 1000
                writer.emit(c.id, "started", ["warm": warm, "load_ms": loadMS])
                let stream = await chat.streamResponse(to: prompt)
                for try await event in stream {
                    if case .response(let delta) = event {
                        if firstTokenMS == nil { firstTokenMS = Date().timeIntervalSince(start) * 1000 }
                        text += delta
                        writer.emit(c.id, "partial_text", ["delta": delta])
                    }
                }
                let s = await chat.stats
                stats = ["generated_tokens": s.generatedTokens, "footprint_bytes": s.footprintBytes, "load_ms": loadMS]
            } else if c.task == "vision.analyze" {
                warm = vision != nil
                if vision == nil {
                    chat = nil; chatKey = ""; decider = nil
                    vision = try await KitVisionModel(decoderBundleAt: urls[0], visionModelAt: urls[1], arch: .qwen3VL2B)
                }
                guard let vision, let encoded = c.inputs.image_base64,
                      let data = Data(base64Encoded: encoded), data.count <= 6_000_000,
                      let source = CGImageSourceCreateWithData(data as CFData, nil),
                      let image = CGImageSourceCreateThumbnailAtIndex(source, 0, [kCGImageSourceCreateThumbnailFromImageAlways: true, kCGImageSourceCreateThumbnailWithTransform: true, kCGImageSourceThumbnailMaxPixelSize: 1024] as CFDictionary) else {
                    throw NSError(domain: "GeneretiCore", code: 7, userInfo: [NSLocalizedDescriptionKey: "Supply a valid image, at most 6 MB"])
                }
                let loadMS = Date().timeIntervalSince(loadStart) * 1000
                writer.emit(c.id, "started", ["warm": warm, "load_ms": loadMS])
                let session = LanguageModelSession(model: vision)
                for try await snapshot in session.streamResponse(to: Prompt { prompt; Attachment(image) }, options: GenerationOptions(maximumResponseTokens: maxTokens)) {
                    let next = snapshot.content
                    if firstTokenMS == nil && !next.isEmpty { firstTokenMS = Date().timeIntervalSince(start) * 1000 }
                    writer.emit(c.id, "partial_text", ["text": next])
                    text = next
                }
                stats = ["load_ms": loadMS]
            } else {
                throw NSError(domain: "GeneretiCore", code: 8, userInfo: [NSLocalizedDescriptionKey: "Unsupported task"])
            }
            stats["total_ms"] = Date().timeIntervalSince(start) * 1000
            stats["first_response_ms"] = firstTokenMS
            stats["warm"] = warm
            writer.emit(c.id, "completed", ["content": ["text": text], "timings": stats])
        } catch {
            chat = nil; chatKey = ""; vision = nil; decider = nil
            writer.emit(c.id, "failed", ["message": error.localizedDescription])
        }
    }
}

@main struct Main {
    static func main() async {
        guard #available(macOS 27, *), CommandLine.arguments.count == 2 else {
            writer.emit("", "failed", ["message": "Requires macOS 27 and a model-cache directory argument"])
            return
        }
        let runner = Runner(directory: URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true))
        // Read stdin on a background thread; model execution never runs in the browser.
        let lines = AsyncStream<String> { continuation in
            DispatchQueue.global().async {
                while let line = readLine() { continuation.yield(line) }
                continuation.finish()
            }
        }
        for await line in lines {
            do {
                let command = try JSONDecoder().decode(Command.self, from: Data(line.utf8))
                await runner.run(command)
            } catch { writer.emit("", "failed", ["message": "Invalid command JSON"]) }
        }
    }
}
