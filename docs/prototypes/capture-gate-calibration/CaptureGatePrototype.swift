#!/usr/bin/env swift

import Foundation

// PROTOTYPE — throw away the terminal shell after the calibration contract is accepted.

enum Mode: String { case supported, handheld }

struct Profile {
    let version: String
    let mode: Mode
    let windowMilliseconds: Int
    let minimumSamples: Int
    let requiredPassingRatio: Double
    let minimumRectangleConfidence: Double
    let minimumAreaRatio: Double
    let maximumCornerJitter: Double
    let maximumRotationRate: Double
    let maximumUserAcceleration: Double
    let minimumSharpnessRatio: Double
    let severeClipRatio: Double

    static func initial(_ mode: Mode) -> Profile {
        switch mode {
        case .supported:
            return Profile(version: "capture-gates-v1-unvalidated", mode: mode,
                windowMilliseconds: 400, minimumSamples: 8, requiredPassingRatio: 0.90,
                minimumRectangleConfidence: 0.85, minimumAreaRatio: 0.30,
                maximumCornerJitter: 0.003, maximumRotationRate: 0.04,
                maximumUserAcceleration: 0.02, minimumSharpnessRatio: 0.72,
                severeClipRatio: 0.01)
        case .handheld:
            return Profile(version: "capture-gates-v1-unvalidated", mode: mode,
                windowMilliseconds: 700, minimumSamples: 14, requiredPassingRatio: 0.80,
                minimumRectangleConfidence: 0.85, minimumAreaRatio: 0.30,
                maximumCornerJitter: 0.008, maximumRotationRate: 0.18,
                maximumUserAcceleration: 0.07, minimumSharpnessRatio: 0.82,
                severeClipRatio: 0.01)
        }
    }
}
struct Sample {
    let elapsedMilliseconds: Int
    let rectangleConfidence: Double
    let rectangleAreaRatio: Double
    let cornerJitter: Double
    let rotationRate: Double
    let userAcceleration: Double
    let sharpnessRatio: Double
    let shadowClipRatio: Double
    let highlightClipRatio: Double
    let focusAdjusting: Bool
    let exposureAdjusting: Bool
    let severeObstruction: Bool
}

struct Evaluation {
    let ready: Bool
    let structuralFailures: [String]
    let latestFailures: [String]
    let passingSamples: Int
    let requiredPassingSamples: Int
}

func failures(_ sample: Sample, profile: Profile) -> (structural: [String], quality: [String]) {
    var structural: [String] = []
    var quality: [String] = []
    if sample.rectangleConfidence < profile.minimumRectangleConfidence { structural.append("rectangleConfidence") }
    if sample.rectangleAreaRatio < profile.minimumAreaRatio { structural.append("rectangleArea") }
    if sample.shadowClipRatio > profile.severeClipRatio { structural.append("shadowClipping") }
    if sample.highlightClipRatio > profile.severeClipRatio { structural.append("highlightClipping") }
    if sample.severeObstruction { structural.append("severeObstruction") }
    if sample.cornerJitter > profile.maximumCornerJitter { quality.append("cornerJitter") }
    if sample.rotationRate > profile.maximumRotationRate { quality.append("rotationRate") }
    if sample.userAcceleration > profile.maximumUserAcceleration { quality.append("userAcceleration") }
    if sample.sharpnessRatio < profile.minimumSharpnessRatio { quality.append("sharpness") }
    if sample.focusAdjusting { quality.append("focusAdjusting") }
    if sample.exposureAdjusting { quality.append("exposureAdjusting") }
    return (structural, quality)
}

func evaluate(_ samples: [Sample], profile: Profile) -> Evaluation {
    guard let first = samples.first, let latest = samples.last else {
        return Evaluation(ready: false, structuralFailures: [], latestFailures: ["emptyWindow"], passingSamples: 0, requiredPassingSamples: profile.minimumSamples)
    }
    let duration = latest.elapsedMilliseconds - first.elapsedMilliseconds
    let results = samples.map { failures($0, profile: profile) }
    let structural = Array(Set(results.flatMap(\.structural))).sorted()
    let passing = results.filter { $0.structural.isEmpty && $0.quality.isEmpty }.count
    let required = max(profile.minimumSamples, Int(ceil(Double(samples.count) * profile.requiredPassingRatio)))
    let latestFailures = results.last!.structural + results.last!.quality
    let ready = duration >= profile.windowMilliseconds
        && samples.count >= profile.minimumSamples
        && structural.isEmpty
        && passing >= required
        && latestFailures.isEmpty
    return Evaluation(ready: ready, structuralFailures: structural,
        latestFailures: latestFailures, passingSamples: passing,
        requiredPassingSamples: required)
}

enum Scenario: String, CaseIterable { case clean, oneOutlier, moving, soft, clipped }

func samples(for scenario: Scenario, mode: Mode) -> [Sample] {
    let count = mode == .supported ? 9 : 15
    let step = mode == .supported ? 50 : 50
    return (0..<count).map { index in
        let outlier = scenario == .oneOutlier && index == count / 2
        return Sample(elapsedMilliseconds: index * step,
            rectangleConfidence: 0.94, rectangleAreaRatio: 0.55,
            cornerJitter: scenario == .moving ? 0.012 : (outlier ? 0.010 : 0.001),
            rotationRate: scenario == .moving ? 0.24 : 0.01,
            userAcceleration: scenario == .moving ? 0.09 : 0.005,
            sharpnessRatio: scenario == .soft ? 0.65 : 0.95,
            shadowClipRatio: 0.002,
            highlightClipRatio: scenario == .clipped ? 0.03 : 0.002,
            focusAdjusting: false, exposureAdjusting: false,
            severeObstruction: false)
    }
}

func render(mode: Mode, scenario: Scenario) {
    let profile = Profile.initial(mode)
    let window = samples(for: scenario, mode: mode)
    let result = evaluate(window, profile: profile)
    print("\u{001B}[2J\u{001B}[H", terminator: "")
    print("\u{001B}[1mCapture gate prototype\u{001B}[0m")
    print("\u{001B}[2mSynthetic inputs only; thresholds are unvalidated defaults.\u{001B}[0m\n")
    print("\u{001B}[1mprofile\u{001B}[0m             \(profile.version) / \(mode.rawValue)")
    print("\u{001B}[1mscenario\u{001B}[0m            \(scenario.rawValue)")
    print("\u{001B}[1mwindow\u{001B}[0m              \(window.last!.elapsedMilliseconds - window.first!.elapsedMilliseconds) ms, \(window.count) samples")
    print("\u{001B}[1mpassing samples\u{001B}[0m     \(result.passingSamples) / \(result.requiredPassingSamples) required")
    print("\u{001B}[1mstructural failures\u{001B}[0m \(result.structuralFailures.isEmpty ? "none" : result.structuralFailures.joined(separator: ", "))")
    print("\u{001B}[1mlatest failures\u{001B}[0m     \(result.latestFailures.isEmpty ? "none" : result.latestFailures.joined(separator: ", "))")
    print("\u{001B}[1mautomaticReady\u{001B}[0m      \(result.ready)\n")
    print("[m] mode  [1] clean  [2] one outlier  [3] moving  [4] soft  [5] clipped  [q] quit")
}

var mode = Mode.supported
var scenario = Scenario.clean
while true {
    render(mode: mode, scenario: scenario)
    guard let input = readLine()?.lowercased() else { break }
    switch input {
    case "m": mode = mode == .supported ? .handheld : .supported
    case "1": scenario = .clean
    case "2": scenario = .oneOutlier
    case "3": scenario = .moving
    case "4": scenario = .soft
    case "5": scenario = .clipped
    case "q": exit(0)
    default: break
    }
}
