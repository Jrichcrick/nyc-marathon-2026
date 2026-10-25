import Foundation
import HealthKit
import WorkoutKit

func clock(_ seconds: Int) -> String {
    String(format: "%d:%02d:%02d", seconds / 3600, seconds % 3600 / 60, seconds % 60)
}

let output = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let slow: [Int: Int] = [1:580, 14:550, 16:600, 20:550, 23:560, 24:550]
let guides: [Int: String] = [1:"9:30-9:40", 14:"9:00-9:10", 16:"EASY HR<=165", 20:"9:00-9:10", 23:"9:10-9:20", 24:"9:00-9:10"]
let cues: [Int: String] = [1:"UP", 2:"DOWN", 5:"GEL", 10:"GEL", 14:"PULASKI", 16:"BRIDGE", 17:"GEL", 20:"GEL", 23:"CLIMB", 24:"PARK", 25:"DOWN"]
var elapsed = 0
var intervals: [IntervalStep] = []
var manifest: [[String: Any]] = []
for mile in 1...26 {
    elapsed += slow[mile] ?? 540
    let prefix = String(format: "%02d", mile)
    let cue = cues[mile].map { " \($0)" } ?? ""
    let guide = guides[mile] ?? "8:50-9:00"
    let name = "\(prefix)\(cue) \(guide) | BY \(clock(elapsed))"
    let step = WorkoutStep(goal: .distance(1, .miles), alert: nil, displayName: name)
    intervals.append(IntervalStep(.work, step: step))
    manifest.append(["mile":mile, "name":name, "distance_mi":1, "elapsed_by_seconds":elapsed, "alert":"none"])
}
let finishName = "FINISH 8:50-9:00 | BY 3:58:28"
intervals.append(IntervalStep(.work, step: WorkoutStep(goal: .open, alert: nil, displayName: finishName)))
manifest.append(["mile":"finish", "name":finishName, "goal":"open", "alert":"none"])
let workout = CustomWorkout(activity: .running, location: .outdoor, displayName: "NYC 3:57", warmup: nil, blocks: [IntervalBlock(steps: intervals, iterations: 1)], cooldown: nil)
let id = UUID(uuidString: "920C33CA-E21B-441E-BE1F-2734B13F8570")!
let plan = WorkoutPlan(.custom(workout), id: id)
let data = try plan.dataRepresentation
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
let url = output.appendingPathComponent("NYC-3-57.workout")
try data.write(to: url)
let restored = try WorkoutPlan(from: Data(contentsOf: url))
precondition(restored == plan, "Apple WorkoutKit round trip failed")
guard case let .custom(decoded) = restored.workout else { fatalError("Not custom") }
precondition(decoded.warmup == nil && decoded.cooldown == nil)
precondition(decoded.blocks.count == 1 && decoded.blocks[0].iterations == 1)
precondition(decoded.blocks[0].steps.count == 27)
for (index, interval) in decoded.blocks[0].steps.enumerated() {
    precondition(interval.purpose == .work && interval.step.alert == nil)
    precondition(interval.step.displayName == intervals[index].step.displayName)
    if index < 26 {
        guard case let .distance(value, unit) = interval.step.goal else { fatalError("Distance missing") }
        precondition(value == 1 && unit == .miles)
    } else {
        precondition(interval.step.goal == .open)
    }
}
let json = try JSONSerialization.data(withJSONObject: ["name":"NYC 3:57", "id":id.uuidString, "warmup":"skip", "cooldown":"skip", "steps":manifest], options: [.prettyPrinted, .sortedKeys])
try json.write(to: output.appendingPathComponent("NYC-3-57-spec.json"))

let testNames = ["01 EASY | check mile cue", "02 EASY | check average pace", "03 EASY | END at 3 miles"]
let testSteps = testNames.map { IntervalStep(.work, step: WorkoutStep(goal: .distance(1, .miles), alert: nil, displayName: $0)) }
let test = CustomWorkout(activity: .running, location: .outdoor, displayName: "3 mi Watch Rehearsal", warmup: nil, blocks: [IntervalBlock(steps: testSteps)], cooldown: nil)
let testPlan = WorkoutPlan(.custom(test), id: UUID(uuidString: "F1221A5C-829E-45BC-9ECD-67D41F1F0003")!)
let testData = try testPlan.dataRepresentation
try testData.write(to: output.appendingPathComponent("3-mi-Watch-Rehearsal.workout"))
let restoredTest = try WorkoutPlan(from: testData)
precondition(restoredTest == testPlan)
print("PASS: Apple WorkoutKit export and import: 26 × 1 mi Work + Open finish, names preserved, no target alerts, no warmup/cooldown. \(data.count) bytes.")
print("PASS: 3 × 1 mi easy rehearsal, no target alerts. \(testData.count) bytes.")
