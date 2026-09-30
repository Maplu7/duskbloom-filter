import Cocoa
import PDFKit

final class ReaderDelegate:NSObject,NSApplicationDelegate,NSWindowDelegate {
    var window:NSWindow!;var pdf=PDFView();var scroll=NSScrollView();var text=NSTextView();var fontSize:CGFloat=17
    func applicationDidFinishLaunching(_ n:Notification){
        NSApp.setActivationPolicy(.accessory)
        window=NSWindow(contentRect:NSRect(x:0,y:0,width:1000,height:760),styleMask:[.titled,.closable,.resizable,.miniaturizable],backing:.buffered,defer:false);window.title="DuskBloom Reader";window.center();window.delegate=self
        let root=NSView();root.wantsLayer=true;root.layer?.backgroundColor=NSColor(calibratedRed:0.09,green:0.07,blue:0.10,alpha:1).cgColor;window.contentView=root
        let open=NSButton(title:"Open Document",target:self,action:#selector(openFile));open.frame=NSRect(x:22,y:710,width:130,height:32);open.bezelStyle=.rounded;root.addSubview(open)
        let minus=NSButton(title:"A−",target:self,action:#selector(smaller));minus.frame=NSRect(x:165,y:710,width:48,height:32);root.addSubview(minus)
        let plus=NSButton(title:"A+",target:self,action:#selector(larger));plus.frame=NSRect(x:218,y:710,width:48,height:32);root.addSubview(plus)
        let comfort=NSButton(title:"Comfort View",target:self,action:#selector(toggleComfort));comfort.frame=NSRect(x:280,y:710,width:120,height:32);comfort.bezelStyle=.rounded;root.addSubview(comfort)
        pdf.frame=NSRect(x:20,y:20,width:960,height:675);pdf.autoresizingMask=[.width,.height];pdf.autoScales=true;pdf.backgroundColor=NSColor(calibratedRed:0.12,green:0.10,blue:0.12,alpha:1);root.addSubview(pdf)
        scroll.frame=pdf.frame;scroll.autoresizingMask=[.width,.height];scroll.hasVerticalScroller=true;scroll.drawsBackground=true;scroll.backgroundColor=NSColor(calibratedRed:0.13,green:0.11,blue:0.13,alpha:1)
        text.isEditable=false;text.isSelectable=true;text.textColor=NSColor(calibratedWhite:0.94,alpha:1);text.backgroundColor=scroll.backgroundColor;text.textContainerInset=NSSize(width:55,height:38);text.font=.systemFont(ofSize:fontSize);scroll.documentView=text;root.addSubview(scroll);scroll.isHidden=true
        window.makeKeyAndOrderFront(nil);NSApp.activate(ignoringOtherApps:true)
    }
    @objc func openFile(){let p=NSOpenPanel();p.allowedContentTypes=[.pdf,.plainText,.rtf,.html,.init(filenameExtension:"docx")!];p.allowsMultipleSelection=false;if p.runModal()==.OK,let u=p.url{load(u)}}
    func load(_ u:URL){window.title="DuskBloom Reader — \(u.lastPathComponent)";if u.pathExtension.lowercased()=="pdf",let d=PDFDocument(url:u){pdf.document=d;pdf.isHidden=false;scroll.isHidden=true;return};var out="";if u.pathExtension.lowercased()=="docx"{out=docxText(u)}else{out=(try? String(contentsOf:u,encoding:.utf8)) ?? ((try? NSAttributedString(url:u,options:[:],documentAttributes:nil).string) ?? "Could not read this document.")};text.string=out;scroll.isHidden=false;pdf.isHidden=true}
    func docxText(_ u:URL)->String{let p=Process();let pipe=Pipe();p.executableURL=URL(fileURLWithPath:"/usr/bin/unzip");p.arguments=["-p",u.path,"word/document.xml"];p.standardOutput=pipe;try? p.run();p.waitUntilExit();let data=pipe.fileHandleForReading.readDataToEndOfFile();guard var s=String(data:data,encoding:.utf8) else{return "Could not read this DOCX."};s=s.replacingOccurrences(of:"</w:p>",with:"\n\n").replacingOccurrences(of:"</w:tab>",with:"\t");s=s.replacingOccurrences(of:"<[^>]+>",with:"",options:.regularExpression);return s.replacingOccurrences(of:"&amp;",with:"&").replacingOccurrences(of:"&lt;",with:"<").replacingOccurrences(of:"&gt;",with:">")}
    @objc func larger(){fontSize=min(32,fontSize+2);text.font=.systemFont(ofSize:fontSize)}
    @objc func smaller(){fontSize=max(12,fontSize-2);text.font=.systemFont(ofSize:fontSize)}
    @objc func toggleComfort(){if !pdf.isHidden,let d=pdf.document{var s="";for i in 0..<d.pageCount{s += (d.page(at:i)?.string ?? "")+"\n\n"};text.string=s;scroll.isHidden=false;pdf.isHidden=true}else if pdf.document != nil{scroll.isHidden=true;pdf.isHidden=false}}
    func windowWillClose(_ n:Notification){NSApp.terminate(nil)}
}
let app=NSApplication.shared;let d=ReaderDelegate();app.delegate=d;app.run()
