// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "GeneretiD1Helper", platforms: [.macOS(.v15)], targets: [
    .executableTarget(name: "genereticore-d1-helper", path: "Sources/GeneretiD1Helper", exclude: ["Upstream/LICENSE"])
])
