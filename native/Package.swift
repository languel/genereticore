// swift-tools-version: 6.0
import PackageDescription
let package = Package(
    name: "GeneretiCoreHelper",
    platforms: [.macOS("27.0")],
    dependencies: [.package(url: "https://github.com/john-rocky/coreai-kit", exact: "0.7.3")],
    targets: [.executableTarget(name: "genereticore-helper",
        dependencies: [.product(name: "CoreAIKit", package: "coreai-kit")],
        path: "Sources/GeneretiCoreHelper")]
)
