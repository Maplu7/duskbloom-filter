import Cocoa
import PDFKit
import UniformTypeIdentifiers

final class TintView: NSView {
    override func hitTest(_ point: NSPoint) -> NSView? { nil }
}

final class ReaderDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate, NSSpeechSynthesizerDelegate {
    private var window: NSWindow!
    private let pdfView = PDFView()
    private let tintView = TintView()
    private let scrollView = NSScrollView()
    private let textView = NSTextView()
    private let presetMenu = NSPopUpButton()
    private let intensityMenu = NSPopUpButton()
    private let rateSlider = NSSlider(value: 0.45, minValue: 0.15, maxValue: 0.75, target: nil, action: nil)
    private let readButton = NSButton()
    private let speaker = NSSpeechSynthesizer()
    private var fontSize: CGFloat = 18
    private var isSpeaking = false
    private var comfortMode = false

    private let presetRGB: [String: (CGFloat, CGFloat, CGFloat)] = [
        "Pink Blackout": (214,126,156), "Pink": (235,154,184), "Dark Pink": (155,75,108),
        "Rose Dim": (190,112,135), "Lavender": (143,116,166), "Amber": (214,153,73),
        "Forest Green": (70,105,76), "Warm White": (255,224,180), "Deep Red": (105,28,36),
        "Blue Light": (78,111,148), "Dark Dimmer": (20,20,20), "Midnight": (14,12,22),
        "Obsidian": (8,8,12), "Dusty Rose": (166,108,126), "Peach": (222,157,126),
        "Sepia": (150,121,86), "Sage": (116,139,112), "Soft Cyan": (112,151,153),
        "Mauve": (130,96,125), "Smoke": (92,96,103), "Cocoa": (76,55,50),
        "Navy": (35,48,75), "Burgundy": (82,34,48)
    ]

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        speaker.delegate = self
        fontSize = CGFloat(UserDefaults.standard.double(forKey: "readerFontSize"))
        if fontSize < 12 { fontSize = 18 }

        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1120, height: 800),
                          styleMask: [.titled, .closable, .resizable, .miniaturizable],
                          backing: .buffered, defer: false)
        window.title = "DuskBloom Reader"
        window.center()
        window.delegate = self

        let root = NSView(frame: NSRect(x: 0, y: 0, width: 1120, height: 800))
        root.autoresizingMask = [.width, .height]
        root.wantsLayer = true
        root.layer?.backgroundColor = NSColor(calibratedRed: 0.09, green: 0.07, blue: 0.10, alpha: 1).cgColor
        window.contentView = root

        addButton("Open", x: 20, width: 70, action: #selector(openFile), to: root)
        addButton("A−", x: 100, width: 48, action: #selector(smaller), to: root)
        addButton("A+", x: 154, width: 48, action: #selector(larger), to: root)
        addButton("Comfort View", x: 212, width: 115, action: #selector(toggleComfort), to: root)

        presetMenu.frame = NSRect(x: 338, y: 752, width: 150, height: 30)
        presetMenu.addItems(withTitles: Array(presetRGB.keys).sorted())
        presetMenu.selectItem(withTitle: UserDefaults.standard.string(forKey: "readerPreset") ?? "Obsidian")
        presetMenu.target = self
        presetMenu.action = #selector(changePreset)
        root.addSubview(presetMenu)

        intensityMenu.frame = NSRect(x: 496, y: 752, width: 100, height: 30)
        intensityMenu.addItems(withTitles: ["10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"])
        intensityMenu.selectItem(withTitle: UserDefaults.standard.string(forKey: "readerIntensity") ?? "40%")
        intensityMenu.target = self
        intensityMenu.action = #selector(changePreset)
        root.addSubview(intensityMenu)

        readButton.title = "Read Aloud"
        readButton.target = self
        readButton.action = #selector(toggleReadAloud)
        readButton.frame = NSRect(x: 608, y: 752, width: 100, height: 30)
        readButton.bezelStyle = .rounded
        root.addSubview(readButton)

        addButton("Pause", x: 716, width: 70, action: #selector(pauseSpeech), to: root)
        addButton("Stop", x: 792, width: 62, action: #selector(stopSpeech), to: root)

        let rateLabel = NSTextField(labelWithString: "Voice speed")
        rateLabel.frame = NSRect(x: 866, y: 758, width: 72, height: 18)
        rateLabel.textColor = .secondaryLabelColor
        rateLabel.font = .systemFont(ofSize: 11)
        root.addSubview(rateLabel)
        rateSlider.frame = NSRect(x: 940, y: 752, width: 150, height: 26)
        rateSlider.target = self
        rateSlider.action = #selector(rateChanged)
        root.addSubview(rateSlider)

        let documentFrame = NSRect(x: 18, y: 18, width: 1084, height: 720)
        pdfView.frame = documentFrame
        pdfView.autoresizingMask = [.width, .height]
        pdfView.autoScales = true
        pdfView.displayMode = .singlePageContinuous
        pdfView.displaysPageBreaks = true
        root.addSubview(pdfView)

        tintView.frame = documentFrame
        tintView.autoresizingMask = [.width, .height]
        tintView.wantsLayer = true
        root.addSubview(tintView)

        scrollView.frame = documentFrame
        scrollView.autoresizingMask = [.width, .height]
        scrollView.hasVerticalScroller = true
        scrollView.drawsBackground = true

        textView.frame = NSRect(x: 0, y: 0, width: documentFrame.width, height: documentFrame.height)
        textView.minSize = NSSize(width: 0, height: documentFrame.height)
        textView.maxSize = NSSize(width: CGFloat.greatestFiniteMagnitude, height: CGFloat.greatestFiniteMagnitude)
        textView.isEditable = false
        textView.isSelectable = true
        textView.isRichText = true
        textView.isVerticallyResizable = true
        textView.isHorizontallyResizable = false
        textView.autoresizingMask = [.width]
        textView.textContainer?.containerSize = NSSize(width: documentFrame.width, height: CGFloat.greatestFiniteMagnitude)
        textView.textContainer?.widthTracksTextView = true
        textView.textContainerInset = NSSize(width: 72, height: 48)
        scrollView.documentView = textView
        root.addSubview(scrollView)
        scrollView.isHidden = true

        applyTypography()
        applyPreset()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    private func addButton(_ title: String, x: CGFloat, width: CGFloat, action: Selector, to root: NSView) {
        let button = NSButton(title: title, target: self, action: action)
        button.frame = NSRect(x: x, y: 752, width: width, height: 30)
        button.bezelStyle = .rounded
        root.addSubview(button)
    }

    @objc private func openFile() {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.pdf, .plainText, .rtf, .html, UTType(filenameExtension: "docx") ?? .data]
        if panel.runModal() == .OK, let url = panel.url { load(url) }
    }

    private func load(_ url: URL) {
        stopSpeech()
        window.title = "DuskBloom Reader — \(url.lastPathComponent)"
        let ext = url.pathExtension.lowercased()
        if ext == "pdf", let document = PDFDocument(url: url) {
            pdfView.document = document
            comfortMode = false
            showPDF()
            return
        }
        let output: String
        if ext == "docx" { output = docxText(url) }
        else if ext == "rtf" || ext == "html" { output = attributedText(url) }
        else { output = (try? String(contentsOf: url, encoding: .utf8)) ?? "Could not read this document." }
        textView.string = output
        comfortMode = true
        showComfort()
    }

    private func showPDF() {
        scrollView.isHidden = true
        pdfView.isHidden = false
        tintView.isHidden = false
        applyPreset()
    }

    private func showComfort() {
        applyTypography()
        pdfView.isHidden = true
        tintView.isHidden = true
        scrollView.isHidden = false
        applyPreset()
    }

    @objc private func toggleComfort() {
        guard let document = pdfView.document else { return }
        if comfortMode {
            comfortMode = false
            showPDF()
            return
        }
        var output = ""
        let currentIndex = pdfView.currentPage.flatMap { document.index(for: $0) } ?? 0
        for index in currentIndex..<document.pageCount {
            if let pageText = document.page(at: index)?.string, !pageText.isEmpty {
                output += pageText + "\n\n"
            }
        }
        guard !output.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            let alert = NSAlert()
            alert.messageText = "Comfort View needs selectable PDF text"
            alert.informativeText = "This PDF looks image-based or scanned, so there is no embedded text to reflow."
            alert.runModal()
            return
        }
        textView.string = output
        comfortMode = true
        showComfort()
    }

    private func applyTypography() {
        let style = NSMutableParagraphStyle()
        style.lineSpacing = max(5, fontSize * 0.38)
        style.paragraphSpacing = max(9, fontSize * 0.55)
        let range = NSRange(location: 0, length: textView.string.utf16.count)
        textView.font = .systemFont(ofSize: fontSize)
        if range.length > 0 {
            textView.textStorage?.addAttributes([
                .font: NSFont.systemFont(ofSize: fontSize),
                .paragraphStyle: style
            ], range: range)
        }
        textView.sizeToFit()
        if let container = textView.textContainer, let manager = textView.layoutManager {
            manager.ensureLayout(for: container)
            let used = manager.usedRect(for: container)
            textView.frame.size.height = max(scrollView.contentSize.height, used.height + textView.textContainerInset.height * 2)
        }
        UserDefaults.standard.set(Double(fontSize), forKey: "readerFontSize")
    }

    @objc private func larger() { fontSize = min(40, fontSize + 2); applyTypography() }
    @objc private func smaller() { fontSize = max(12, fontSize - 2); applyTypography() }

    @objc private func changePreset() { applyPreset() }

    private func applyPreset() {
        let name = presetMenu.titleOfSelectedItem ?? "Obsidian"
        let rgb = presetRGB[name] ?? presetRGB["Obsidian"]!
        let tint = NSColor(calibratedRed: rgb.0/255, green: rgb.1/255, blue: rgb.2/255, alpha: 1)
        let pct = CGFloat(Int((intensityMenu.titleOfSelectedItem ?? "40%").replacingOccurrences(of: "%", with: "")) ?? 40) / 100
        tintView.layer?.backgroundColor = tint.withAlphaComponent(min(0.65, pct * 0.55)).cgColor

        let base = NSColor(calibratedRed: 0.055, green: 0.05, blue: 0.06, alpha: 1)
        let comfortBackground = base.blended(withFraction: min(0.55, pct * 0.55), of: tint) ?? base
        scrollView.backgroundColor = comfortBackground
        textView.backgroundColor = comfortBackground
        textView.textColor = NSColor(calibratedWhite: 0.96, alpha: 1)
        pdfView.backgroundColor = comfortBackground
        UserDefaults.standard.set(name, forKey: "readerPreset")
        UserDefaults.standard.set(intensityMenu.titleOfSelectedItem ?? "40%", forKey: "readerIntensity")
    }

    private func speechText() -> String {
        let selected = textView.selectedRange()
        if !scrollView.isHidden, selected.length > 0 {
            return (textView.string as NSString).substring(with: selected)
        }
        if !scrollView.isHidden { return textView.string }
        guard let document = pdfView.document else { return "" }
        let start = pdfView.currentPage.flatMap { document.index(for: $0) } ?? 0
        var output = ""
        for index in start..<document.pageCount {
            output += document.page(at: index)?.string ?? ""
            output += "\n"
        }
        return output
    }

    @objc private func toggleReadAloud() {
        if isSpeaking { pauseSpeech(); return }
        let words = speechText()
        guard !words.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { NSSound.beep(); return }
        speaker.rate = Float(130 + rateSlider.doubleValue * 170)
        speaker.startSpeaking(words)
        isSpeaking = true
        readButton.title = "Reading…"
    }

    @objc private func pauseSpeech() {
        guard isSpeaking else { return }
        speaker.pauseSpeaking(at: .wordBoundary)
        readButton.title = "Resume"
        readButton.action = #selector(resumeSpeech)
    }

    @objc private func resumeSpeech() {
        speaker.continueSpeaking()
        readButton.title = "Reading…"
        readButton.action = #selector(toggleReadAloud)
    }

    @objc private func stopSpeech() {
        speaker.stopSpeaking()
        isSpeaking = false
        readButton.title = "Read Aloud"
        readButton.action = #selector(toggleReadAloud)
    }

    @objc private func rateChanged() {
        if isSpeaking { speaker.rate = Float(130 + rateSlider.doubleValue * 170) }
    }

    func speechSynthesizer(_ sender: NSSpeechSynthesizer, didFinishSpeaking finishedSpeaking: Bool) {
        isSpeaking = false
        readButton.title = "Read Aloud"
        readButton.action = #selector(toggleReadAloud)
    }

    private func attributedText(_ url: URL) -> String {
        (try? NSAttributedString(url: url, options: [:], documentAttributes: nil).string) ?? "Could not read this document."
    }

    private func docxText(_ url: URL) -> String {
        let process = Process()
        let pipe = Pipe()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/unzip")
        process.arguments = ["-p", url.path, "word/document.xml"]
        process.standardOutput = pipe
        process.standardError = Pipe()
        do { try process.run(); process.waitUntilExit() } catch { return "Could not read this DOCX." }
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        guard var xml = String(data: data, encoding: .utf8) else { return "Could not read this DOCX." }
        xml = xml.replacingOccurrences(of: "</w:p>", with: "\n\n")
        xml = xml.replacingOccurrences(of: "</w:tab>", with: "\t")
        xml = xml.replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
        return xml.replacingOccurrences(of: "&amp;", with: "&")
            .replacingOccurrences(of: "&lt;", with: "<")
            .replacingOccurrences(of: "&gt;", with: ">")
            .replacingOccurrences(of: "&quot;", with: "\"")
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
