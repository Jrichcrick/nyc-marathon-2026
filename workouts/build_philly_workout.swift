import Foundation
import HealthKit
import WorkoutKit

// Philly 3:58 — Philadelphia Marathon, Sun Nov 22 2026.
// Same structure as NYC 3:57: 26 x 1 mi Work steps + Open finish, no alerts,
// guide range and slow-edge cumulative BY time in each step name.
// Slow edges sum to 3:58:28 over 26.21875 mi (JR's rule: stay inside every range = goal).
// Must match index.html (Philly Plan tab) and workouts/Philly-3-58-spec.json.

func clock(_ seconds: Int) -> String {
    String(format: "%d:%02d:%02d", seconds / 3600, seconds % 3600 / 60, seconds % 60)
}

let output = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let slow: [Int: Int] = [1:560, 8:560, 9:550, 10:570, 11:550, 12:550, 16:550, 17:550, 18:550, 19:550, 20:550]
let guides: [Int: String] = [1:"9:10-9:20", 8:"9:10-9:20", 9:"9:00-9:10", 10:"9:20-9:30", 11:"9:00-9:10", 12:"9:00-9:10",
                             16:"9:00-9:10", 17:"9:00-9:10", 18:"9:00-9:10", 19:"9:00-9:10", 20:"9:00-9:10",
                             24:"8:40-9:00", 25:"8:40-9:00", 26:"8:40-9:00"]
let cues: [Int: String] = [1:"START", 5:"GEL", 8:"CLIMB", 10:"HILL", 11:"GEL", 16:"GEL", 17:"MANAYUNK", 19:"CLIMB", 20:"TURN GEL"]
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
precondition(elapsed == 14190, "Slow edges through mile 26 must total 3:56:30")
let finishName = "FINISH 8:40-9:00 | BY 3:58:28"
intervals.append(IntervalStep(.work, step: WorkoutStep(goal: .open, alert: nil, displayName: finishName)))
manifest.append(["mile":"finish", "name":finishName, "goal":"open", "alert":"none"])
let workout = CustomWorkout(activity: .running, location: .outdoor, displayName: "Philly 3:58", warmup: nil, blocks: [IntervalBlock(steps: intervals, iterations: 1)], cooldown: nil)
let id = UUID(uuidString: "B7F546BB-E3B4-4DD2-A930-6222E43AB0E4")!
let plan = WorkoutPlan(.custom(workout), id: id)
let data = try plan.dataRepresentation
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
let url = output.appendingPathComponent("Philly-3-58.workout")
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
let json = try JSONSerialization.data(withJSONObject: ["name":"Philly 3:58", "id":id.uuidString, "warmup":"skip", "cooldown":"skip", "steps":manifest], options: [.prettyPrinted, .sortedKeys])
try json.write(to: output.appendingPathComponent("Philly-3-58-spec.json"))
print("PASS: Philly 3:58 — 26 × 1 mi Work + Open finish, names preserved, no target alerts, no warmup/cooldown. \(data.count) bytes.")
