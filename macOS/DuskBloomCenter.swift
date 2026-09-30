import Cocoa

final class CenterDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate {
    private var window: NSWindow!

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)

        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 620, height: 500),
            styleMask: [.titled, .closable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        window.title = "DuskBloom Center"
        window.isReleasedWhenClosed = false
        window.center()
        window.delegate = self

        let root = NSView(frame: window.contentView?.bounds ?? .zero)
        root.autoresizingMask = [.width, .height]
        root.wantsLayer = true
        root.layer?.backgroundColor = NSColor(
            calibratedRed: 0.10, green: 0.075, blue: 0.11, alpha: 1
        ).cgColor
        window.contentView = root

        addLabel(
            "DuskBloom",
            font: .boldSystemFont(ofSize: 30),
            color: NSColor(calibratedRed: 0.96, green: 0.69, blue: 0.80, alpha: 1),
            frame: NSRect(x: 38, y: 420, width: 500, height: 42),
            to: root
        )
        addLabel(
            "soft tools for a gentler Mac",
            font: .systemFont(ofSize: 14),
            color: .secondaryLabelColor,
            frame: NSRect(x: 40, y: 392, width: 500, height: 24),
            to: root
        )

        addCard(
            title: "🌸  Screen",
            subtitle: "Low-memory menu bar filter • no screen recording",
            tag: 1,
            y: 285,
            to: root
        )
        addCard(
            title: "📖  Reader",
            subtitle: "Comfortable PDF, DOCX and text reading",
            tag: 2,
            y: 175,
            to: root
        )

        let webButton = NSButton(title: "Open DuskBloom Web Folder", target: self, action: #selector(openWeb))
        webButton.frame = NSRect(x: 38, y: 92, width: 220, height: 34)
        webButton.bezelStyle = .rounded
        root.addSubview(webButton)

        addLabel(
            "Center closes completely when you close this window.",
            font: .systemFont(ofSize: 12),
            color: .tertiaryLabelColor,
            frame: NSRect(x: 40, y: 45, width: 500, height: 20),
            to: root
        )

        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    private func addLabel(
        _ text: String,
        font: NSFont,
        color: NSColor,
        frame: NSRect,
        to parent: NSView
    ) {
        let label = NSTextField(labelWithString: text)
        label.frame = frame
        label.font = font
        label.textColor = color
        parent.addSubview(label)
    }

    private func addCard(
        title: String,
        subtitle: String,
        tag: Int,
        y: CGFloat,
        to parent: NSView
    ) {
        let box = NSBox(frame: NSRect(x: 38, y: y, width: 544, height: 92))
        box.boxType = .custom
        box.cornerRadius = 16
        box.fillColor = NSColor(calibratedWhite: 0.16, alpha: 1)
        box.borderColor = NSColor(calibratedWhite: 1, alpha: 0.08)
        parent.addSubview(box)

        addLabel(
            title,
            font: .boldSystemFont(ofSize: 18),
            color: .labelColor,
            frame: NSRect(x: 18, y: 48, width: 360, height: 26),
            to: box
        )
        addLabel(
            subtitle,
            font: .systemFont(ofSize: 12),
            color: .secondaryLabelColor,
            frame: NSRect(x: 18, y: 23, width: 390, height: 20),
            to: box
        )

        let button = NSButton(title: "Open", target: self, action: #selector(openApp(_:)))
        button.tag = tag
        button.frame = NSRect(x: 448, y: 29, width: 76, height: 34)
        button.bezelStyle = .rounded
        box.addSubview(button)
    }

    @objc private func openApp(_ sender: NSButton) {
        let appName: String
        switch sender.tag {
        case 1:
            appName = "DuskBloom Screen.app"
        case 2:
            appName = "DuskBloom Reader.app"
        default:
            return
        }

        let releaseFolder = Bundle.main.bundleURL.deletingLastPathComponent()
        let appURL = releaseFolder.appendingPathComponent(appName)
        let config = NSWorkspace.OpenConfiguration()

        NSWorkspace.shared.openApplication(at: appURL, configuration: config) { _, error in
            if let error = error {
                NSSound.beep()
                print("Could not open \(appName): \(error)")
            }
        }
    }

    @objc private func openWeb() {
        let releaseFolder = Bundle.main.bundleURL.deletingLastPathComponent()
        let webURL = releaseFolder.appendingPathComponent("DuskBloom Web for Zen")
        NSWorkspace.shared.open(webURL)
    }

    func windowWillClose(_ notification: Notification) {
        NSApp.terminate(nil)
    }
}

let app = NSApplication.shared
let delegate = CenterDelegate()
app.delegate = delegate
app.run()
