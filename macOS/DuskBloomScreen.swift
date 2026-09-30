import Cocoa

struct Preset { let name:String; let color:NSColor; let alpha:CGFloat }
let presets:[Preset] = [
    .init(name:"Soft Pink",color:NSColor(calibratedRed:0.84,green:0.49,blue:0.61,alpha:1),alpha:0.16),
    .init(name:"Reading Comfort",color:NSColor(calibratedRed:0.89,green:0.78,blue:0.67,alpha:1),alpha:0.11),
    .init(name:"Study",color:NSColor(calibratedRed:1.0,green:0.94,blue:0.78,alpha:1),alpha:0.09),
    .init(name:"Night",color:NSColor(calibratedRed:0.055,green:0.047,blue:0.086,alpha:1),alpha:0.34),
    .init(name:"Migraine",color:NSColor(calibratedRed:0.03,green:0.03,blue:0.045,alpha:1),alpha:0.48)
]

final class OverlayWindow:NSWindow {
    init(screen:NSScreen) {
        super.init(contentRect:screen.frame,styleMask:.borderless,backing:.buffered,defer:false)
        isOpaque=false; backgroundColor=.clear; ignoresMouseEvents=true; hasShadow=false
        level=NSWindow.Level(rawValue:Int(CGWindowLevelForKey(.screenSaverWindow))+1)
        collectionBehavior=[.canJoinAllSpaces,.stationary,.ignoresCycle,.fullScreenAuxiliary]
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
        let im=NSMenu(); for v in [50,75,100,125,150] { let x=NSMenuItem(title:"\(v)%",action:#selector(setIntensity(_:)),keyEquivalent:"");x.target=self;x.tag=v;x.state=Int(intensity*100)==v ? .on:.off;im.addItem(x)}
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
