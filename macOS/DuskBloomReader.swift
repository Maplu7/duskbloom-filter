import Cocoa
import PDFKit
import UniformTypeIdentifiers

final class ReaderDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate {
    private var window: NSWindow!
    private let pdfView = PDFView()
    private let scrollView = NSScrollView()
    private let textView = NSTextView()
    private var fontSize: CGFloat = 17
    private let presetMenu = NSPopUpButton()
    private let speaker = NSSpeechSynthesizer()
    private var isSpeaking = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)

        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1000, height: 760),
            styleMask: [.titled, .closable, .resizable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        window.title = "DuskBloom Reader"
        window.center()
        window.delegate = self

        let root = NSView(frame: window.contentView?.bounds ?? .zero)
        root.autoresizingMask = [.width, .height]
        root.wantsLayer = true
        root.layer?.backgroundColor = NSColor(
            calibratedRed: 0.09,
            green: 0.07,
            blue: 0.10,
            alpha: 1
        ).cgColor
        window.contentView = root

        let openButton = NSButton(
            title: "Open Document",
            target: self,
            action: #selector(openFile)
        )
        openButton.frame = NSRect(x: 22, y: 710, width: 130, height: 32)
        openButton.bezelStyle = .rounded
        root.addSubview(openButton)

        let smallerButton = NSButton(
            title: "A−",
            target: self,
            action: #selector(smaller)
        )
        smallerButton.frame = NSRect(x: 165, y: 710, width: 48, height: 32)
        root.addSubview(smallerButton)

        let largerButton = NSButton(
            title: "A+",
            target: self,
            action: #selector(larger)
        )
        largerButton.frame = NSRect(x: 218, y: 710, width: 48, height: 32)
        root.addSubview(largerButton)

        let comfortButton = NSButton(
            title: "Comfort View",
            target: self,
            action: #selector(toggleComfort)
        )
        comfortButton.frame = NSRect(x: 280, y: 710, width: 120, height: 32)
        comfortButton.bezelStyle = .rounded
        root.addSubview(comfortButton)

        presetMenu.frame = NSRect(x: 414, y: 710, width: 150, height: 32)
        presetMenu.addItems(withTitles: ["Obsidian", "Cozy Pink", "Sky Blue", "Warm Paper"])
        presetMenu.selectItem(withTitle: "Obsidian")
        presetMenu.target = self
        presetMenu.action = #selector(changePreset)
        root.addSubview(presetMenu)

        let readButton = NSButton(
            title: "Read Aloud",
            target: self,
            action: #selector(toggleReadAloud)
        )
        readButton.frame = NSRect(x: 578, y: 710, width: 110, height: 32)
        readButton.bezelStyle = .rounded
        root.addSubview(readButton)

        pdfView.frame = NSRect(x: 20, y: 20, width: 960, height: 675)
        pdfView.autoresizingMask = [.width, .height]
        pdfView.autoScales = true
        pdfView.displayMode = .singlePageContinuous
        pdfView.displaysPageBreaks = true
        pdfView.backgroundColor = NSColor(
            calibratedRed: 0.12,
            green: 0.10,
            blue: 0.12,
            alpha: 1
        )
        root.addSubview(pdfView)

        scrollView.frame = pdfView.frame
        scrollView.autoresizingMask = [.width, .height]
        scrollView.hasVerticalScroller = true
        scrollView.drawsBackground = true
        scrollView.backgroundColor = NSColor(
            calibratedRed: 0.13,
            green: 0.11,
            blue: 0.13,
            alpha: 1
        )

        textView.isEditable = false
        textView.isSelectable = true
        textView.isRichText = false
        textView.textColor = NSColor(calibratedWhite: 0.94, alpha: 1)
        textView.backgroundColor = scrollView.backgroundColor
        textView.textContainerInset = NSSize(width: 55, height: 38)
        textView.font = .systemFont(ofSize: fontSize)
        textView.isVerticallyResizable = true
        textView.isHorizontallyResizable = false
        textView.autoresizingMask = [.width]
        textView.textContainer?.widthTracksTextView = true

        scrollView.documentView = textView
        root.addSubview(scrollView)
        scrollView.isHidden = true

        applyPreset(named: "Obsidian")
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    @objc private func openFile() {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [
            .pdf,
            .plainText,
            .rtf,
            .html,
            UTType(filenameExtension: "docx") ?? .data
        ]
        panel.allowsMultipleSelection = false

        if panel.runModal() == .OK, let url = panel.url {
            load(url)
        }
    }

    private func load(_ url: URL) {
        window.title = "DuskBloom Reader — \(url.lastPathComponent)"
        let ext = url.pathExtension.lowercased()

        if ext == "pdf", let document = PDFDocument(url: url) {
            pdfView.document = document
            pdfView.isHidden = false
            scrollView.isHidden = true
            return
        }

        let output: String
        if ext == "docx" {
            output = docxText(url)
        } else if ext == "rtf" || ext == "html" {
            output = attributedText(url)
        } else {
            output = (try? String(contentsOf: url, encoding: .utf8))
                ?? "Could not read this document."
        }

        textView.string = output
        textView.font = .systemFont(ofSize: fontSize)
        scrollView.isHidden = false
        pdfView.isHidden = true
    }

    private func attributedText(_ url: URL) -> String {
        do {
            return try NSAttributedString(
                url: url,
                options: [:],
                documentAttributes: nil
            ).string
        } catch {
            return "Could not read this document."
        }
    }

    private func docxText(_ url: URL) -> String {
        let process = Process()
        let pipe = Pipe()

        process.executableURL = URL(fileURLWithPath: "/usr/bin/unzip")
        process.arguments = ["-p", url.path, "word/document.xml"]
        process.standardOutput = pipe
        process.standardError = Pipe()

        do {
            try process.run()
            process.waitUntilExit()
        } catch {
            return "Could not read this DOCX."
        }

        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        guard var xml = String(data: data, encoding: .utf8) else {
            return "Could not read this DOCX."
        }

        xml = xml.replacingOccurrences(of: "</w:p>", with: "\n\n")
        xml = xml.replacingOccurrences(of: "</w:tab>", with: "\t")
        xml = xml.replacingOccurrences(
            of: "<[^>]+>",
            with: "",
            options: .regularExpression
        )
        xml = xml.replacingOccurrences(of: "&amp;", with: "&")
        xml = xml.replacingOccurrences(of: "&lt;", with: "<")
        xml = xml.replacingOccurrences(of: "&gt;", with: ">")
        xml = xml.replacingOccurrences(of: "&quot;", with: "\"")
        return xml
    }

    @objc private func larger() {
        fontSize = min(32, fontSize + 2)
        textView.font = .systemFont(ofSize: fontSize)
    }

    @objc private func smaller() {
        fontSize = max(12, fontSize - 2)
        textView.font = .systemFont(ofSize: fontSize)
    }

    @objc private func toggleComfort() {
        if !pdfView.isHidden, let document = pdfView.document {
            var output = ""
            for index in 0..<document.pageCount {
                output += document.page(at: index)?.string ?? ""
                output += "\n\n"
            }
            textView.string = output
            textView.font = .systemFont(ofSize: fontSize)
            scrollView.isHidden = false
            pdfView.isHidden = true
        } else if pdfView.document != nil {
            scrollView.isHidden = true
            pdfView.isHidden = false
        }
    }

    @objc private func changePreset() {
        applyPreset(named: presetMenu.titleOfSelectedItem ?? "Obsidian")
    }

    private func applyPreset(named name: String) {
        let background: NSColor
        let textColor: NSColor
        switch name {
        case "Cozy Pink":
            background = NSColor(calibratedRed: 0.16, green: 0.09, blue: 0.13, alpha: 1)
            textColor = NSColor(calibratedRed: 1.0, green: 0.94, blue: 0.97, alpha: 1)
        case "Sky Blue":
            background = NSColor(calibratedRed: 0.07, green: 0.12, blue: 0.17, alpha: 1)
            textColor = NSColor(calibratedRed: 0.93, green: 0.97, blue: 1.0, alpha: 1)
        case "Warm Paper":
            background = NSColor(calibratedRed: 0.20, green: 0.17, blue: 0.13, alpha: 1)
            textColor = NSColor(calibratedRed: 1.0, green: 0.96, blue: 0.88, alpha: 1)
        default:
            background = NSColor(calibratedRed: 0.07, green: 0.07, blue: 0.09, alpha: 1)
            textColor = NSColor(calibratedWhite: 0.94, alpha: 1)
        }
        scrollView.backgroundColor = background
        textView.backgroundColor = background
        textView.textColor = textColor
        pdfView.backgroundColor = background
    }

    @objc private func toggleReadAloud(_ sender: NSButton) {
        if isSpeaking {
            speaker.stopSpeaking()
            isSpeaking = false
            sender.title = "Read Aloud"
            return
        }

        var words = textView.string
        if !pdfView.isHidden, let document = pdfView.document {
            words = ""
            for index in 0..<document.pageCount {
                words += document.page(at: index)?.string ?? ""
                words += "\n"
            }
        }
        guard !words.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            NSSound.beep()
            return
        }
        speaker.startSpeaking(words)
        isSpeaking = true
        sender.title = "Stop Reading"
    }

    func windowWillClose(_ notification: Notification) {
        speaker.stopSpeaking()
        NSApp.terminate(nil)
    }
}

let app = NSApplication.shared
let delegate = ReaderDelegate()
app.delegate = delegate
app.run()
