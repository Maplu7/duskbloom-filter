import Cocoa

final class CenterDelegate:NSObject,NSApplicationDelegate {
    var window:NSWindow!
    func applicationDidFinishLaunching(_ n:Notification){
        NSApp.setActivationPolicy(.accessory)
        let w=NSWindow(contentRect:NSRect(x:0,y:0,width:620,height:500),styleMask:[.titled,.closable,.miniaturizable],backing:.buffered,defer:false)
        w.title="DuskBloom Center";w.isReleasedWhenClosed=false;w.center()
        let root=NSView();root.wantsLayer=true;root.layer?.backgroundColor=NSColor(calibratedRed:0.10,green:0.075,blue:0.11,alpha:1).cgColor;w.contentView=root
        label("DuskBloom",30,.boldSystemFont(ofSize:30),NSColor(calibratedRed:0.96,green:0.69,blue:0.80,alpha:1),NSRect(x:38,y:420,width:500,height:42),root)
        label("soft tools for a gentler Mac",14,.systemFont(ofSize:14),.secondaryLabelColor,NSRect(x:40,y:392,width:500,height:24),root)
        card("🌸  Screen","Low-memory menu bar filter • no screen recording","DuskBloom Screen.app",y:285,root)
        card("📖  Reader","Comfortable PDF, DOCX and text reading","DuskBloom Reader.app",y:175,root)
        let web=NSButton(title:"Open DuskBloom Web Folder",target:self,action:#selector(openWeb));web.frame=NSRect(x:38,y:92,width:220,height:34);web.bezelStyle=.rounded;root.addSubview(web)
        label("Center closes completely when you close this window.",12,.systemFont(ofSize:12),.tertiaryLabelColor,NSRect(x:40,y:45,width:500,height:20),root)
        w.delegate=self;window=w;w.makeKeyAndOrderFront(nil);NSApp.activate(ignoringOtherApps:true)
    }
    func label(_ t:String,_ s:CGFloat,_ f:NSFont,_ c:NSColor,_ r:NSRect,_ v:NSView){let x=NSTextField(labelWithString:t);x.frame=r;x.font=f;x.textColor=c;v.addSubview(x)}
    func card(_ title:String,_ sub:String,_ app:String,y:CGFloat,_ v:NSView){let box=NSBox(frame:NSRect(x:38,y:y,width:544,height:92));box.boxType=.custom;box.cornerRadius=16;box.fillColor=NSColor(calibratedWhite:0.16,alpha:1);box.borderColor=NSColor(calibratedWhite:1,alpha:0.08);v.addSubview(box);label(title,18,.boldSystemFont(ofSize:18),.labelColor,NSRect(x:18,y:48,width:360,height:26),box);label(sub,12,.systemFont(ofSize:12),.secondaryLabelColor,NSRect(x:18,y:23,width:390,height:20),box);let b=NSButton(title:"Open",target:self,action:#selector(openApp(_:)));b.representedObject=app;b.frame=NSRect(x:448,y:29,width:76,height:34);b.bezelStyle=.rounded;box.addSubview(b)}
    @objc func openApp(_ s:NSButton){guard let name=s.representedObject as? String else{return};let base=Bundle.main.bundleURL.deletingLastPathComponent();let url=base.appendingPathComponent(name);NSWorkspace.shared.openApplication(at:url,configuration:NSWorkspace.OpenConfiguration())}
    @objc func openWeb(){let u=Bundle.main.bundleURL.deletingLastPathComponent().appendingPathComponent("DuskBloom Web for Zen");NSWorkspace.shared.open(u)}
}
extension CenterDelegate:NSWindowDelegate{func windowWillClose(_ n:Notification){NSApp.terminate(nil)}}
let app=NSApplication.shared;let d=CenterDelegate();app.delegate=d;app.run()
