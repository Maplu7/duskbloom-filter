import Cocoa

struct FilterDef { let name: String; let color: NSColor; let alphas: [CGFloat] }
struct PresetDef { let name: String; let filter: String; let intensity: Int; let whitePoint: Bool }

func levels(_ values: [Int]) -> [CGFloat] { values.map { CGFloat($0) / 255.0 } }
let filters: [String: FilterDef] = [
 "pink_blackout": .init(name:"Pink Blackout",color:NSColor(calibratedRed:214/255,green:126/255,blue:156/255,alpha:1),alphas:levels([10,14,18,24,31,39,49,60,72,86,101,117,134,152,171,190,207,221,232,240])),
 "pink": .init(name:"Pink",color:NSColor(calibratedRed:1,green:182/255,blue:193/255,alpha:1),alphas:levels([3,5,7,10,13,17,22,28,34,42,50,60,71,84,100,118,138,160,185,210])),
 "dark_pink": .init(name:"Dark Pink",color:NSColor(calibratedRed:180/255,green:80/255,blue:110/255,alpha:1),alphas:levels([6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,189,206,220,232])),
 "rose_dim": .init(name:"Rose Dim",color:NSColor(calibratedRed:210/255,green:100/255,blue:130/255,alpha:1),alphas:levels([7,11,16,22,30,39,49,60,72,85,99,114,130,147,165,183,200,216,228,238])),
 "dusty_rose": .init(name:"Dusty Rose",color:NSColor(calibratedRed:166/255,green:108/255,blue:126/255,alpha:1),alphas:levels([5,8,12,17,23,30,38,47,57,68,80,93,107,122,138,155,173,191,208,224])),
 "peach": .init(name:"Peach",color:NSColor(calibratedRed:222/255,green:157/255,blue:126/255,alpha:1),alphas:levels([4,7,11,15,20,26,33,41,50,60,71,83,96,110,125,140,156,172,188,205])),
 "sepia": .init(name:"Sepia",color:NSColor(calibratedRed:150/255,green:121/255,blue:86/255,alpha:1),alphas:levels([4,7,11,15,20,26,33,41,50,60,71,83,96,110,125,140,156,172,188,205])),
 "sage": .init(name:"Sage",color:NSColor(calibratedRed:116/255,green:139/255,blue:112/255,alpha:1),alphas:levels([4,7,11,15,20,26,33,41,50,60,71,83,96,110,125,140,156,172,188,205])),
 "soft_cyan": .init(name:"Soft Cyan",color:NSColor(calibratedRed:112/255,green:151/255,blue:153/255,alpha:1),alphas:levels([4,7,11,15,20,26,33,41,50,60,71,83,96,110,125,140,156,172,188,205])),
 "mauve": .init(name:"Mauve",color:NSColor(calibratedRed:130/255,green:96/255,blue:125/255,alpha:1),alphas:levels([5,8,12,17,23,30,38,47,57,68,80,93,107,122,138,155,173,191,208,224])),
 "smoke": .init(name:"Smoke",color:NSColor(calibratedRed:92/255,green:96/255,blue:103/255,alpha:1),alphas:levels([5,10,16,23,31,40,50,61,73,86,100,115,131,148,165,183,200,215,228,240])),
 "cocoa": .init(name:"Cocoa",color:NSColor(calibratedRed:76/255,green:55/255,blue:50/255,alpha:1),alphas:levels([5,10,16,23,31,40,50,61,73,86,100,115,131,148,165,183,200,215,228,240])),
 "navy": .init(name:"Navy",color:NSColor(calibratedRed:35/255,green:48/255,blue:75/255,alpha:1),alphas:levels([6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,189,206,220,232])),
 "burgundy": .init(name:"Burgundy",color:NSColor(calibratedRed:82/255,green:34/255,blue:48/255,alpha:1),alphas:levels([6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,189,206,220,232])),
 "reading": .init(name:"Reading Comfort",color:NSColor(calibratedRed:226/255,green:198/255,blue:170/255,alpha:1),alphas:levels([3,4,6,8,10,13,16,20,25,31,38,46,55,65,76,88,101,115,130,146])),
 "purple": .init(name:"Lavender",color:NSColor(calibratedRed:180/255,green:130/255,blue:220/255,alpha:1),alphas:levels([5,8,12,17,23,30,38,47,57,68,80,93,107,122,138,155,173,191,208,224])),
 "amber": .init(name:"Amber",color:NSColor(calibratedRed:1,green:160/255,blue:60/255,alpha:1),alphas:levels([5,8,12,16,21,27,34,42,51,61,72,84,97,111,126,142,159,176,193,208])),
 "green": .init(name:"Forest Green",color:NSColor(calibratedRed:100/255,green:180/255,blue:100/255,alpha:1),alphas:levels([5,8,12,16,21,27,34,42,51,61,72,84,97,111,126,142,159,176,193,208])),
 "warm_white": .init(name:"Warm White",color:NSColor(calibratedRed:1,green:240/255,blue:200/255,alpha:1),alphas:levels([3,5,8,11,15,19,24,30,37,44,53,62,73,85,98,112,127,143,160,178])),
 "deep_red": .init(name:"Deep Red",color:NSColor(calibratedRed:200/255,green:50/255,blue:50/255,alpha:1),alphas:levels([6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,189,206,220,232])),
 "bluelight": .init(name:"Blue Light",color:NSColor(calibratedRed:100/255,green:160/255,blue:1,alpha:1),alphas:levels([4,7,11,15,20,26,33,41,50,60,71,83,96,110,125,140,156,172,188,205])),
 "dark": .init(name:"Dark Dimmer",color:NSColor(calibratedRed:20/255,green:20/255,blue:20/255,alpha:1),alphas:levels([5,10,16,23,31,40,50,61,73,86,100,115,131,148,165,183,200,215,228,240])),
 "midnight": .init(name:"Midnight",color:NSColor(calibratedRed:14/255,green:12/255,blue:22/255,alpha:1),alphas:levels([8,13,20,28,37,47,58,70,83,97,112,128,145,163,181,198,214,227,238,246])),
 "obsidian": .init(name:"Obsidian",color:NSColor(calibratedRed:8/255,green:8/255,blue:12/255,alpha:1),alphas:levels([10,16,24,33,43,54,66,79,93,108,124,141,159,178,196,212,226,237,246,252]))
]
let filterOrder=["pink_blackout","pink","dark_pink","rose_dim","reading","purple","amber","green","warm_white","deep_red","bluelight","dark","midnight","obsidian"]
let presets=[
 PresetDef(name:"Migraine",filter:"obsidian",intensity:20,whitePoint:true),
 PresetDef(name:"Study",filter:"warm_white",intensity:7,whitePoint:false),
 PresetDef(name:"Night",filter:"midnight",intensity:12,whitePoint:true),
 PresetDef(name:"Soft Pink",filter:"pink_blackout",intensity:10,whitePoint:false),
 PresetDef(name:"Reading Comfort",filter:"reading",intensity:7,whitePoint:false),
 PresetDef(name:"Media",filter:"dark",intensity:5,whitePoint:false)
]

final class OverlayWindow: NSWindow {
 init(screen:NSScreen) {
  super.init(contentRect:screen.frame,styleMask:.borderless,backing:.buffered,defer:false)
  isOpaque = false; backgroundColor = .clear; ignoresMouseEvents = true; hasShadow = false
  level=NSWindow.Level(rawValue:Int(CGWindowLevelForKey(.screenSaverWindow)))
  collectionBehavior=[.canJoinAllSpaces,.stationary,.ignoresCycle,.fullScreenAuxiliary]
  orderFrontRegardless()
 }
 func apply(filter:String,intensity:Int,enabled:Bool,whitePoint:Bool) {
  guard let f=filters[filter] else { return }
  var a=f.alphas[max(0,min(19,intensity-1))]
  if whitePoint { a=min(0.988,a + ((["warm_white","reading","pink","pink_blackout","bluelight","amber"].contains(filter)) ? 18/255 : 9/255)) }
  backgroundColor=enabled ? f.color.withAlphaComponent(a) : .clear
  alphaValue=enabled ? 1 : 0
  if enabled { orderFrontRegardless() }
 }
}

struct Profile: Codable { var filter:String; var intensity:Int; var whitePoint:Bool }
struct MonitorSetting: Codable { var enabled:Bool; var filter:String; var intensity:Int }

private let dashboardDarwinName = "com.duskbloom.DuskBloomScreen.settingsChanged" as CFString
private func dashboardDarwinCallback(_ center: CFNotificationCenter?, _ observer: UnsafeMutableRawPointer?, _ name: CFNotificationName?, _ object: UnsafeRawPointer?, _ userInfo: CFDictionary?) {
 guard let observer else { return }
 let delegate = Unmanaged<AppDelegate>.fromOpaque(observer).takeUnretainedValue()
 DispatchQueue.main.async { delegate.externalCommand() }
}

final class AppDelegate:NSObject,NSApplicationDelegate {
 let d=UserDefaults.standard
 var status:NSStatusItem!
 var overlays:[OverlayWindow]=[]
 var enabled=true, whitePoint=false, perMonitor=false, restoreLast=true, startPaused=false
 var filter="pink_blackout", intensity=7
 var monitorSettings:[String:MonitorSetting]=[:]
 var profiles:[String:Profile]=[:]
 var startupProfile=""
 var pausedUntil:Date?
 var pauseTimer:Timer?, boostTimer:Timer?, emergencyTimer:Timer?
 var boostBackup:(Int,Bool)?, emergencyBackup:(Bool,String,Int,Bool,Bool,[String:MonitorSetting])?

 func applicationDidFinishLaunching(_ n:Notification) {
  NSApp.setActivationPolicy(.accessory); load()
  buildStatus(); rebuildOverlays()
  NotificationCenter.default.addObserver(self,selector:#selector(displaysChanged),name:NSApplication.didChangeScreenParametersNotification,object:nil)
  NSWorkspace.shared.notificationCenter.addObserver(self,selector:#selector(woke),name:NSWorkspace.didWakeNotification,object:nil)
  DistributedNotificationCenter.default().addObserver(self, selector:#selector(externalCommand), name:Notification.Name("com.duskbloom.DuskBloomScreen.settingsChanged"), object:nil)
  CFNotificationCenterAddObserver(
   CFNotificationCenterGetDarwinNotifyCenter(),
   Unmanaged.passUnretained(self).toOpaque(),
   dashboardDarwinCallback,
   dashboardDarwinName,
   nil,
   .deliverImmediately
  )
 }
 @objc func externalCommand(){ d.synchronize(); load(); apply() }
 func load() {
  enabled=d.object(forKey:"enabled") as? Bool ?? true
  filter=d.string(forKey:"filter") ?? "pink_blackout"; if filters[filter] == nil { filter="pink_blackout" }
  intensity=max(1,min(20,d.object(forKey:"level") as? Int ?? 7))
  whitePoint=d.object(forKey:"whitePoint") as? Bool ?? false
  perMonitor=d.object(forKey:"perMonitor") as? Bool ?? false
  restoreLast=d.object(forKey:"restoreLast") as? Bool ?? true
  startPaused=d.object(forKey:"startPaused") as? Bool ?? false
  startupProfile=d.string(forKey:"startupProfile") ?? ""
  if let data=d.data(forKey:"monitors"),let v=try? JSONDecoder().decode([String:MonitorSetting].self,from:data){monitorSettings=v}
  if let data=d.data(forKey:"profiles"),let v=try? JSONDecoder().decode([String:Profile].self,from:data){profiles=v}
  if profiles.isEmpty {
   profiles=["Migraine":Profile(filter:"obsidian",intensity:18,whitePoint:true),"Study":Profile(filter:"warm_white",intensity:7,whitePoint:false),"Night":Profile(filter:"midnight",intensity:12,whitePoint:true),"Reading Comfort":Profile(filter:"reading",intensity:7,whitePoint:false)]
  }
 }
 func applyLaunchOnlySettings() {
  // Startup profile and Start Paused are launch behaviors only.
  // External widget changes must never snap the filter back to a startup preset.
  if !startupProfile.isEmpty,let p=profiles[startupProfile]{
   filter=p.filter;intensity=p.intensity;whitePoint=p.whitePoint;enabled=true
  }
  if startPaused { pausedUntil=Date.distantFuture }
 }
 func save() {
  d.set(enabled,forKey:"enabled");d.set(filter,forKey:"filter");d.set(intensity,forKey:"level");d.set(whitePoint,forKey:"whitePoint");d.set(perMonitor,forKey:"perMonitor");d.set(restoreLast,forKey:"restoreLast");d.set(startPaused,forKey:"startPaused");d.set(startupProfile,forKey:"startupProfile")
  if let x=try? JSONEncoder().encode(monitorSettings){d.set(x,forKey:"monitors")}
  if let x=try? JSONEncoder().encode(profiles){d.set(x,forKey:"profiles")}
 }
 func buildStatus(){status=NSStatusBar.system.statusItem(withLength:NSStatusItem.variableLength);status.button?.title="🌸";status.button?.toolTip="DuskBloom Screen";rebuildMenu()}
 func item(_ title:String,_ action:Selector?=nil,_ tag:Int=0)->NSMenuItem{let x=NSMenuItem(title:title,action:action,keyEquivalent:"");x.target=self;x.tag=tag;return x}
 func root(_ title:String,_ submenu:NSMenu)->NSMenuItem{let x=item(title);x.submenu=submenu;return x}
 func rebuildMenu() {
  let m=NSMenu(), paused=(pausedUntil != nil && pausedUntil! > Date())
  let mode=perMonitor ? "Per-Monitor":"Global"
  let t=item("DuskBloom Screen • \(mode) • \(paused ? "Paused":(enabled ? "Active":"Off"))");t.isEnabled=false;m.addItem(t)
  let s=item("\(filters[filter]?.name ?? filter) • Lv \(intensity)");s.isEnabled=false;m.addItem(s);m.addItem(.separator())
  m.addItem(item("Toggle Filter",#selector(toggle)))
  m.addItem(item(paused ? "Resume":"Pause 5 min",#selector(togglePause)))
  m.addItem(item(emergencyBackup == nil ? "Emergency Mode":"Restore Emergency",#selector(toggleEmergency)));m.addItem(.separator())

  let bm=NSMenu(); for (i,v) in [(3,5),(5,10),(8,15)].enumerated(){bm.addItem(item("Boost +\(v.0) for \(v.1) min",#selector(startBoost(_:)),i))};bm.addItem(.separator());bm.addItem(item("Cancel Boost",#selector(cancelBoost)));m.addItem(root("Boost",bm))
  let pm=NSMenu();for (i,p) in presets.enumerated(){let x=item(p.name,#selector(applyPreset(_:)),i);pm.addItem(x)};m.addItem(root("Presets",pm))
  let fm=NSMenu();for (i,k) in filterOrder.enumerated(){guard let f=filters[k] else{continue};let x=item(f.name,#selector(setFilter(_:)),i);x.state=(!perMonitor && k==filter) ? .on:.off;fm.addItem(x)};m.addItem(root("Global Filter",fm))
  let im=NSMenu();for i in 1...20{let x=item("\(i)",#selector(setIntensity(_:)),i);x.state=(!perMonitor && i==intensity) ? .on:.off;im.addItem(x)};m.addItem(root("Global Intensity",im));m.addItem(.separator())

  let mm=NSMenu();let use=item("Use Per-Monitor",#selector(togglePerMonitor));use.state=perMonitor ? .on:.off;mm.addItem(use);mm.addItem(.separator())
  for i in 0..<NSScreen.screens.count {
   let sm=NSMenu(), ms=monitorSetting(i)
   let on=item("Enabled",#selector(toggleMonitor(_:)),i);on.state=ms.enabled ? .on:.off;sm.addItem(on);sm.addItem(.separator())
   let sf=NSMenu();for (j,k) in filterOrder.enumerated(){guard let f=filters[k] else{continue};let x=item(f.name,#selector(setMonitorFilter(_:)),i*100+j);x.state=k==ms.filter ? .on:.off;sf.addItem(x)};sm.addItem(root("Filter",sf))
   let si=NSMenu();for lv in 1...20{let x=item("\(lv)",#selector(setMonitorIntensity(_:)),i*100+lv);x.state=lv==ms.intensity ? .on:.off;si.addItem(x)};sm.addItem(root("Intensity",si))
   mm.addItem(root("Monitor \(i+1)",sm))
  }
  m.addItem(root("Monitors",mm))

  let prof=NSMenu();prof.addItem(item("Save Current as Profile…",#selector(saveProfile)));if !profiles.isEmpty{prof.addItem(.separator())
   let loadM=NSMenu(),delM=NSMenu(),startM=NSMenu();let none=item("(none)",#selector(setStartupProfile(_:)),-1);none.state=startupProfile.isEmpty ? .on:.off;startM.addItem(none)
   for (i,n) in profiles.keys.sorted().enumerated(){loadM.addItem(item(n,#selector(loadProfile(_:)),i));delM.addItem(item(n,#selector(deleteProfile(_:)),i));let x=item(n,#selector(setStartupProfile(_:)),i);x.state=n==startupProfile ? .on:.off;startM.addItem(x)}
   prof.addItem(root("Load",loadM));prof.addItem(root("Delete",delM));prof.addItem(root("Start With Profile",startM))
  };m.addItem(root("Profiles",prof))

  let km=NSMenu();["⌘⇧M — Toggle Filter","⌘⇧R — Reading Comfort","⌘⇧N — Night","⌘⇧↑ — Intensity Up","⌘⇧↓ — Intensity Down"].forEach{let x=item($0);x.isEnabled=false;km.addItem(x)};m.addItem(root("Keyboard Shortcuts",km))
  let om=NSMenu();let wp=item("White Point Killer",#selector(toggleWhitePoint));wp.state=whitePoint ? .on:.off;om.addItem(wp);let rs=item("Restore Last State",#selector(toggleRestore));rs.state=restoreLast ? .on:.off;om.addItem(rs);let sp=item("Start Paused",#selector(toggleStartPaused));sp.state=startPaused ? .on:.off;om.addItem(sp);om.addItem(.separator());om.addItem(item("Open at Login…",#selector(openLogin)));m.addItem(root("Options",om))
  m.addItem(.separator());m.addItem(item("Open Filter Folder",#selector(openFolder)));m.addItem(item("Safe Reset",#selector(safeReset)));m.addItem(item("Quit DuskBloom Screen",#selector(quit)));status.menu=m
 }
 func monitorSetting(_ i:Int)->MonitorSetting{monitorSettings["\(i)"] ?? MonitorSetting(enabled:true,filter:filter,intensity:intensity)}
 func effectiveEnabled()->Bool{enabled && !(pausedUntil != nil && pausedUntil! > Date())}
 func rebuildOverlays(){overlays.forEach{$0.close()};overlays=NSScreen.screens.map{OverlayWindow(screen:$0)};apply()}
 func apply(){for (i,o) in overlays.enumerated(){if perMonitor{let x=monitorSetting(i);o.apply(filter:x.filter,intensity:x.intensity,enabled:x.enabled && effectiveEnabled(),whitePoint:whitePoint)}else{o.apply(filter:filter,intensity:intensity,enabled:effectiveEnabled(),whitePoint:whitePoint)}};save();rebuildMenu()}
 @objc func toggle(){enabled.toggle();pausedUntil=nil;apply()}
 @objc func togglePause(){if pausedUntil != nil && pausedUntil! > Date(){pausedUntil=nil;pauseTimer?.invalidate()}else{pausedUntil=Date().addingTimeInterval(300);pauseTimer?.invalidate();pauseTimer=Timer.scheduledTimer(withTimeInterval:300,repeats:false){[weak self]_ in self?.pausedUntil=nil;self?.apply()}};apply()}
 @objc func toggleEmergency(){if let b=emergencyBackup{enabled=b.0;filter=b.1;intensity=b.2;whitePoint=b.3;perMonitor=b.4;monitorSettings=b.5;emergencyBackup=nil;emergencyTimer?.invalidate();apply();return};emergencyBackup=(enabled,filter,intensity,whitePoint,perMonitor,monitorSettings);enabled=true;filter="obsidian";intensity=20;whitePoint=true;perMonitor=false;emergencyTimer=Timer.scheduledTimer(withTimeInterval:600,repeats:false){[weak self]_ in self?.toggleEmergency()};apply()}
 @objc func startBoost(_ s:NSMenuItem){let opts=[(3,5.0),(5,10.0),(8,15.0)],v=opts[s.tag];boostBackup=(intensity,whitePoint);intensity=min(20,intensity+v.0);whitePoint=true;enabled=true;boostTimer?.invalidate();boostTimer=Timer.scheduledTimer(withTimeInterval:v.1*60,repeats:false){[weak self]_ in self?.restoreBoost()};apply()}
 @objc func cancelBoost(){restoreBoost()}
 func restoreBoost(){guard let b=boostBackup else{return};intensity=b.0;whitePoint=b.1;boostBackup=nil;boostTimer?.invalidate();apply()}
 @objc func applyPreset(_ s:NSMenuItem){let p=presets[s.tag];filter=p.filter;intensity=p.intensity;whitePoint=p.whitePoint;enabled=true;pausedUntil=nil;apply()}
 @objc func setFilter(_ s:NSMenuItem){filter=filterOrder[s.tag];perMonitor=false;enabled=true;apply()}
 @objc func setIntensity(_ s:NSMenuItem){intensity=s.tag;perMonitor=false;enabled=true;apply()}
 @objc func togglePerMonitor(){perMonitor.toggle();apply()}
 @objc func toggleMonitor(_ s:NSMenuItem){var x=monitorSetting(s.tag);x.enabled.toggle();monitorSettings["\(s.tag)"]=x;perMonitor=true;apply()}
 @objc func setMonitorFilter(_ s:NSMenuItem){let mon=s.tag/100,idx=s.tag%100;var x=monitorSetting(mon);x.filter=filterOrder[idx];monitorSettings["\(mon)"]=x;perMonitor=true;apply()}
 @objc func setMonitorIntensity(_ s:NSMenuItem){let mon=s.tag/100,lv=s.tag%100;var x=monitorSetting(mon);x.intensity=lv;monitorSettings["\(mon)"]=x;perMonitor=true;apply()}
 @objc func toggleWhitePoint(){whitePoint.toggle();apply()}
 @objc func toggleRestore(){restoreLast.toggle();save();rebuildMenu()}
 @objc func toggleStartPaused(){startPaused.toggle();save();rebuildMenu()}
 func profileName(_ tag:Int)->String?{let a=profiles.keys.sorted();return tag>=0 && tag<a.count ? a[tag]:nil}
 @objc func saveProfile(){let a=NSAlert();a.messageText="Save Current as Profile";a.informativeText="Enter a profile name:";let f=NSTextField(frame:NSRect(x:0,y:0,width:240,height:24));f.stringValue="My Profile";a.accessoryView=f;a.addButton(withTitle:"Save");a.addButton(withTitle:"Cancel");if a.runModal() == .alertFirstButtonReturn{let n=f.stringValue.trimmingCharacters(in:.whitespacesAndNewlines);if !n.isEmpty{profiles[n]=Profile(filter:filter,intensity:intensity,whitePoint:whitePoint);save();rebuildMenu()}}}
 @objc func loadProfile(_ s:NSMenuItem){guard let n=profileName(s.tag),let p=profiles[n] else{return};filter=p.filter;intensity=p.intensity;whitePoint=p.whitePoint;enabled=true;perMonitor=false;apply()}
 @objc func deleteProfile(_ s:NSMenuItem){guard let n=profileName(s.tag) else{return};profiles.removeValue(forKey:n);if startupProfile==n{startupProfile=""};save();rebuildMenu()}
 @objc func setStartupProfile(_ s:NSMenuItem){startupProfile=s.tag == -1 ? "" : (profileName(s.tag) ?? "");save();rebuildMenu()}
 @objc func openLogin(){if let u=URL(string:"x-apple.systempreferences:com.apple.LoginItems-Settings.extension"){NSWorkspace.shared.open(u)}}
 @objc func openFolder(){NSWorkspace.shared.activateFileViewerSelecting([Bundle.main.bundleURL])}
 @objc func safeReset(){pauseTimer?.invalidate();boostTimer?.invalidate();emergencyTimer?.invalidate();pausedUntil=nil;boostBackup=nil;emergencyBackup=nil;enabled=true;filter="pink_blackout";intensity=7;whitePoint=false;perMonitor=false;monitorSettings=[:];apply()}
 @objc func displaysChanged(){rebuildOverlays()}
 @objc func woke(){rebuildOverlays()}
 @objc func quit(){NSApp.terminate(nil)}
}

// Lightweight command bridge used by the Übersicht DuskBloom dashboard.
// It only edits DuskBloom Screen's preferences and wakes the already-running app.
// No screen capture, polling process, or background Python process is used.
func commandDefaults() -> UserDefaults {
 return UserDefaults(suiteName:"com.duskbloom.DuskBloomScreen") ?? .standard
}
func notifyRunningScreen() {
 DistributedNotificationCenter.default().post(name:Notification.Name("com.duskbloom.DuskBloomScreen.settingsChanged"),object:nil)
}
func filterDisplayName(_ key:String)->String { filters[key]?.name ?? key }
func jsonStatus(_ d:UserDefaults) {
 let key=d.string(forKey:"filter") ?? "pink_blackout"
 let level=max(1,min(20,d.object(forKey:"level") as? Int ?? 7))
 let on=d.object(forKey:"enabled") as? Bool ?? true
 let wp=d.object(forKey:"whitePoint") as? Bool ?? false
 let payload:[String:Any]=[
  "enabled":on,"paused":false,"running":true,"filter":key,"filter_name":filterDisplayName(key),
  "intensity":level,"white_point_killer":wp,"adaptive_brightness":false,"flash_protection":false,
  "brightness_compression":false,"auto_fade":false,"startup_safety":true,"launch_at_login":false,
  "temporary_reveal":false,"monitor_memory":true,"remembered_monitors":NSScreen.screens.count,"gaming_safe_mode":true,
  "flash_strength":"Native"
 ]
 if let data=try? JSONSerialization.data(withJSONObject:payload),let s=String(data:data,encoding:.utf8){print(s)}
}
func runDashboardCommand(_ args:[String])->Bool {
 guard let cmd=args.first else{return false}
 let d=commandDefaults()
 func setEnabled(_ v:Bool){d.set(v,forKey:"enabled")}
 switch cmd.lowercased() {
 case "status": jsonStatus(d); return true
 case "toggle": setEnabled(!(d.object(forKey:"enabled") as? Bool ?? true))
 case "on": setEnabled(true)
 case "off": setEnabled(false)
 case "intensity":
  if args.count>1,let n=Int(args[1]){d.set(max(1,min(20,n)),forKey:"level");setEnabled(true)}
 case "filter":
  if args.count>1,filters[args[1]] != nil{d.set(args[1],forKey:"filter");d.set(false,forKey:"perMonitor");setEnabled(true)}
 case "preset","mode":
  if args.count>1 {
   let wanted=args.dropFirst().joined(separator:" ").lowercased()
   let aliases=["reading":"reading comfort","media":"media","night":"night","study":"study","migraine":"migraine","soft pink":"soft pink"]
   let target=aliases[wanted] ?? wanted
   if let p=presets.first(where:{$0.name.lowercased()==target}) {
    d.set(p.filter,forKey:"filter");d.set(p.intensity,forKey:"level");d.set(p.whitePoint,forKey:"whitePoint");d.set(false,forKey:"perMonitor");setEnabled(true)
   }
  }
 case "whitepoint","white-point":
  if args.count>1{d.set(args[1].lowercased()=="on",forKey:"whitePoint")}
 case "folder":
  NSWorkspace.shared.activateFileViewerSelecting([Bundle.main.bundleURL]); return true
 // Compatibility with buttons from the older dashboard. These features are
 // intentionally passive in the native low-memory Screen build.
 case "adaptive","flash","compression","fade","startup-safety","reveal","monitor-memory","gaming","launch":
  break
 default: return false
 }
 d.synchronize();notifyRunningScreen();return true
}

let cli=Array(CommandLine.arguments.dropFirst())
if !cli.isEmpty && runDashboardCommand(cli) {
 exit(0)
}

let app=NSApplication.shared
let delegate=AppDelegate()
app.delegate=delegate
app.run()
