import Cocoa

struct Preset { let name:String; let color:NSColor; let alpha:CGFloat }
let presets: [Preset] = [
    .init(name: "Pink Blackout", color: NSColor(calibratedRed: 214/255, green: 126/255, blue: 156/255, alpha: 1), alpha: 0.16),
    .init(name: "Pink", color: NSColor(calibratedRed: 235/255, green: 154/255, blue: 184/255, alpha: 1), alpha: 0.15),
    .init(name: "Dark Pink", color: NSColor(calibratedRed: 155/255, green: 75/255, blue: 108/255, alpha: 1), alpha: 0.18),
    .init(name: "Rose Dim", color: NSColor(calibratedRed: 190/255, green: 112/255, blue: 135/255, alpha: 1), alpha: 0.17),
    .init(name: "Lavender", color: NSColor(calibratedRed: 143/255, green: 116/255, blue: 166/255, alpha: 1), alpha: 0.16),
    .init(name: "Amber", color: NSColor(calibratedRed: 214/255, green: 153/255, blue: 73/255, alpha: 1), alpha: 0.14),
    .init(name: "Forest Green", color: NSColor(calibratedRed: 70/255, green: 105/255, blue: 76/255, alpha: 1), alpha: 0.18),
    .init(name: "Warm White", color: NSColor(calibratedRed: 255/255, green: 224/255, blue: 180/255, alpha: 1), alpha: 0.10),
    .init(name: "Deep Red", color: NSColor(calibratedRed: 105/255, green: 28/255, blue: 36/255, alpha: 1), alpha: 0.22),
    .init(name: "Blue Light", color: NSColor(calibratedRed: 78/255, green: 111/255, blue: 148/255, alpha: 1), alpha: 0.17),
    .init(name: "Dark Dimmer", color: NSColor(calibratedRed: 20/255, green: 20/255, blue: 20/255, alpha: 1), alpha: 0.34),
    .init(name: "Midnight", color: NSColor(calibratedRed: 14/255, green: 12/255, blue: 22/255, alpha: 1), alpha: 0.40),
    .init(name: "Obsidian", color: NSColor(calibratedRed: 8/255, green: 8/255, blue: 12/255, alpha: 1), alpha: 0.46),
    .init(name: "Dusty Rose", color: NSColor(calibratedRed: 166/255, green: 108/255, blue: 126/255, alpha: 1), alpha: 0.17),
    .init(name: "Peach", color: NSColor(calibratedRed: 222/255, green: 157/255, blue: 126/255, alpha: 1), alpha: 0.14),
    .init(name: "Sepia", color: NSColor(calibratedRed: 150/255, green: 121/255, blue: 86/255, alpha: 1), alpha: 0.18),
    .init(name: "Sage", color: NSColor(calibratedRed: 116/255, green: 139/255, blue: 112/255, alpha: 1), alpha: 0.16),
    .init(name: "Soft Cyan", color: NSColor(calibratedRed: 112/255, green: 151/255, blue: 153/255, alpha: 1), alpha: 0.15),
    .init(name: "Mauve", color: NSColor(calibratedRed: 130/255, green: 96/255, blue: 125/255, alpha: 1), alpha: 0.18),
    .init(name: "Smoke", color: NSColor(calibratedRed: 92/255, green: 96/255, blue: 103/255, alpha: 1), alpha: 0.22),
    .init(name: "Cocoa", color: NSColor(calibratedRed: 76/255, green: 55/255, blue: 50/255, alpha: 1), alpha: 0.24),
    .init(name: "Navy", color: NSColor(calibratedRed: 35/255, green: 48/255, blue: 75/255, alpha: 1), alpha: 0.25),
    .init(name: "Burgundy", color: NSColor(calibratedRed: 82/255, green: 34/255, blue: 48/255, alpha: 1), alpha: 0.25)
]

final class OverlayWindow:NSWindow {
    init(screen:NSScreen) {
        super.init(contentRect:screen.frame,styleMask:.borderless,backing:.buffered,defer:false)
        isOpaque = false; backgroundColor = .clear; ignoresMouseEvents = true; hasShadow = false
        level = NSWindow.Level(rawValue:Int(CGWindowLevelForKey(.screenSaverWindow))+1)
        collectionBehavior = [.canJoinAllSpaces,.stationary,.ignoresCycle,.fullScreenAuxiliary]
        orderFrontRegardless()
    }
    func apply(_ color:NSColor,_ alpha:CGFloat,_ enabled:Bool) {
        backgroundColor = enabled ? color.withAlphaComponent(alpha) : .clear
        alphaValue = enabled ? 1 : 0
        orderFrontRegardless()
    }
}

final class AppDelegate:NSObject,NSApplicationDelegate {
    var status:NSStatusItem!; var overlays:[OverlayWindow]=[]
    var enabled=true; var presetIndex=0; var intensity:CGFloat=1
    let defaults=UserDefaults.standard
    func applicationDidFinishLaunching(_ n:Notification) {
        NSApp.setActivationPolicy(.accessory)
        enabled=defaults.object(forKey:"enabled") as? Bool ?? true
        presetIndex=min(max(defaults.integer(forKey:"preset"),0),presets.count-1)
        intensity=CGFloat(defaults.object(forKey:"intensity") as? Double ?? 1)
        buildStatus(); rebuildOverlays()
        NotificationCenter.default.addObserver(self,selector:#selector(displaysChanged),name:NSApplication.didChangeScreenParametersNotification,object:nil)
        NSWorkspace.shared.notificationCenter.addObserver(self,selector:#selector(woke),name:NSWorkspace.didWakeNotification,object:nil)
    }
    func buildStatus() {
        status=NSStatusBar.system.statusItem(withLength:NSStatusItem.variableLength)
        status.button?.title="🌸"; status.button?.toolTip="DuskBloom Screen"
        rebuildMenu()
    }
    func rebuildMenu() {
        let m=NSMenu()
        let title=NSMenuItem(title:"DuskBloom Screen",action:nil,keyEquivalent:""); title.isEnabled=false; m.addItem(title)
        let state=NSMenuItem(title:enabled ? "✓ Filter On" : "Filter Off",action:#selector(toggle),keyEquivalent:"t"); state.target=self; m.addItem(state)
        m.addItem(.separator())
        let pm=NSMenu(); for (i,p) in presets.enumerated(){ let x=NSMenuItem(title:p.name,action:#selector(setPreset(_:)),keyEquivalent:""); x.target=self;x.tag=i;x.state=i==presetIndex ? .on:.off;pm.addItem(x)}
        let pr=NSMenuItem(title:"Preset",action:nil,keyEquivalent:"");pr.submenu=pm;m.addItem(pr)
        let im=NSMenu(); for v in [10,20,30,40,50,60,70,80,90,100,110,125,150,175,200] { let x=NSMenuItem(title:"\(v)%",action:#selector(setIntensity(_:)),keyEquivalent:"");x.target=self;x.tag=v;x.state=Int(intensity*100)==v ? .on:.off;im.addItem(x)}
        let ir=NSMenuItem(title:"Intensity",action:nil,keyEquivalent:"");ir.submenu=im;m.addItem(ir)
        m.addItem(.separator())
        let login=NSMenuItem(title:"Open at Login…",action:#selector(openLoginItems),keyEquivalent:"");login.target=self;m.addItem(login)
        let q=NSMenuItem(title:"Quit DuskBloom Screen",action:#selector(quit),keyEquivalent:"q");q.target=self;m.addItem(q)
        status.menu=m
    }
    func rebuildOverlays(){ overlays.forEach{$0.close()};overlays=NSScreen.screens.map{OverlayWindow(screen:$0)};apply() }
    func apply(){let p=presets[presetIndex];overlays.forEach{$0.apply(p.color,min(p.alpha*intensity,0.82),enabled)};defaults.set(enabled,forKey:"enabled");defaults.set(presetIndex,forKey:"preset");defaults.set(Double(intensity),forKey:"intensity");rebuildMenu()}
    @objc func toggle(){enabled.toggle();apply()}
    @objc func setPreset(_ s:NSMenuItem){presetIndex=s.tag;enabled=true;apply()}
    @objc func setIntensity(_ s:NSMenuItem){intensity=CGFloat(s.tag)/100;apply()}
    @objc func displaysChanged(){rebuildOverlays()}
    @objc func woke(){rebuildOverlays()}
    @objc func openLoginItems(){NSWorkspace.shared.open(URL(string:"x-apple.systempreferences:com.apple.LoginItems-Settings.extension")!)}
    @objc func quit(){NSApp.terminate(nil)}
}
let app=NSApplication.shared;let delegate=AppDelegate();app.delegate=delegate;app.run()
