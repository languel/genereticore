import Foundation
import CoreML

struct Command: Decodable {
    let id: String
    let task: String
    let model: String
    let inputs: Inputs
    struct Inputs: Decodable { let prompt: String; let choices: [String]; let question: String? }
}
func emit(_ id: String, _ type: String, _ payload: [String: Any]) {
    if let bytes = try? JSONSerialization.data(withJSONObject: ["id":id,"type":type,"payload":payload], options: [.sortedKeys]) {
        FileHandle.standardOutput.write(bytes); FileHandle.standardOutput.write(Data([10]))
    }
}
@main struct Helper {
    static func main() async {
        guard CommandLine.arguments.count == 2 else { return }
        let directory = URL(fileURLWithPath: CommandLine.arguments[1])
        var manager: D1OmniManager?
        while let line = readLine() {
            guard let data = line.data(using:.utf8), let command = try? JSONDecoder().decode(Command.self,from:data) else { continue }
            let start = Date(); let cold = manager == nil
            do {
                guard command.task == "decision.evaluate", command.model == "d1-omni-600m", (2...8).contains(command.inputs.choices.count) else {
                    throw NSError(domain:"GeneretiD1",code:1,userInfo:[NSLocalizedDescriptionKey:"d1 supports text decisions with 2–8 choices"])
                }
                var loadMS = 0.0
                if manager == nil {
                    emit(command.id,"loading",[:]); let before=Date()
                    manager = try await D1OmniManager.load(from:directory,computeUnits:.cpuAndNeuralEngine,batch:1)
                    loadMS = Date().timeIntervalSince(before)*1000
                }
                let answer = try await manager!.answer(state:command.inputs.prompt,question:.choice(
                    command.inputs.question ?? "Which option best fits the state?",options:command.inputs.choices.map { (name:$0,description:"") }))
                let choices=command.inputs.choices
                let scores=Dictionary(uniqueKeysWithValues:zip(choices,answer.probabilities.map(Double.init)))
                emit(command.id,"completed",["backend":"coreml","content":["choice":choices[answer.selectedIndex],"scores":scores],
                    "probability_kind":"d1_temperature_scaled", "timings":["cold":cold,"load_ms":loadMS,"prediction_ms":answer.predictionMilliseconds,
                    "total_ms":Date().timeIntervalSince(start)*1000,"input_tokens":answer.tokenCount,"generated_tokens":0,"compute_units":"cpuAndNeuralEngine"]])
            } catch { emit(command.id,"failed",["message":error.localizedDescription]) }
        }
    }
}
