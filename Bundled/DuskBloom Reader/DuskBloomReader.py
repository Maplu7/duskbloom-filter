import os,sys,json,threading,tkinter as tk
from tkinter import filedialog,messagebox,ttk
from pathlib import Path

APP=Path(os.getenv("LOCALAPPDATA",Path.home()))/"DuskBloom"/"Reader"; APP.mkdir(parents=True,exist_ok=True)
STATE=APP/"state.json"

THEMES={
 "Cozy Pink":("#171218","#241C25","#302431","#E58AB3","#FFF7FB","#BFAAB6"),
 "Sky Blue":("#101820","#192733","#223746","#76BCE4","#F5FBFF","#A6C1D0"),
 "Obsidian":("#0E0E10","#1B1B1F","#25252A","#A7A7B2","#FAFAFC","#A5A5AF")
}
FILTERS={
 "Pink Blackout":"#D67E9C","Pink":"#EB9AB8","Dark Pink":"#9B4B6C","Rose Dim":"#BE7087",
 "Dusty Rose":"#A66C7E","Peach":"#DE9D7E","Sepia":"#967956","Sage":"#748B70",
 "Soft Cyan":"#709799","Mauve":"#82607D","Smoke":"#5C6067","Cocoa":"#4C3732",
 "Navy":"#23304B","Burgundy":"#522230","Lavender":"#8F74A6","Amber":"#D69949",
 "Forest Green":"#46694C","Warm White":"#FFE0B4","Deep Red":"#691C24","Blue Light":"#4E6F94",
 "Dark Dimmer":"#141414","Midnight":"#0E0C16","Obsidian":"#08080C"
}

class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title("DuskBloom Reader"); self.geometry("1320x820"); self.minsize(980,650)
  self.file=None; self.pages=[]; self.page=0; self.speech=None
  try:self.state=json.loads(STATE.read_text())
  except:self.state={}
  self.theme=tk.StringVar(value=self.state.get("theme","Cozy Pink"))
  self.filter=tk.StringVar(value=self.state.get("filter","Obsidian"))
  self.size=tk.IntVar(value=self.state.get("size",18))
  self.spacing=tk.IntVar(value=self.state.get("spacing",8))
  self.margin=tk.IntVar(value=self.state.get("margin",72))
  self.status=tk.StringVar(value="Open a PDF, DOCX, or TXT to begin.")
  self.build(); self.apply_theme(); self.protocol("WM_DELETE_WINDOW",self.close)
  if len(sys.argv)>1 and Path(sys.argv[-1]).exists(): self.open_path(Path(sys.argv[-1]))

 def button(self,parent,text,cmd):
  b=tk.Button(parent,text=text,command=cmd,relief="flat",bd=0,padx=14,pady=9,cursor="hand2")
  b.pack(side="left",padx=(0,8)); return b

 def build(self):
  self.header=tk.Frame(self); self.header.pack(fill="x",padx=24,pady=(20,10))
  self.brand=tk.Label(self.header,text="DuskBloom Reader  🌷",font=("Segoe UI",22,"bold")); self.brand.pack(side="left")
  self.subtitle=tk.Label(self.header,text="  reading shouldn't hurt",font=("Segoe UI",10)); self.subtitle.pack(side="left",pady=(9,0))
  self.themebox=ttk.Combobox(self.header,textvariable=self.theme,values=list(THEMES),state="readonly",width=13); self.themebox.pack(side="right")
  self.theme.trace_add("write",lambda *_:self.apply_theme())

  self.actions=tk.Frame(self); self.actions.pack(fill="x",padx=24,pady=(0,10))
  for t,c in [("Open",self.open),("◀ Previous",self.prev),("Next ▶",self.next),("Read aloud",self.read),("Stop",self.stop)]:
   self.button(self.actions,t,c)
  tk.Label(self.actions,text="Filter").pack(side="left",padx=(12,6))
  self.filterbox=ttk.Combobox(self.actions,textvariable=self.filter,values=list(FILTERS),state="readonly",width=15); self.filterbox.pack(side="left")
  self.filter.trace_add("write",lambda *_:self.apply_theme())

  self.body=tk.Frame(self); self.body.pack(fill="both",expand=True,padx=24,pady=(0,12))
  self.sidebar=tk.Frame(self.body,width=230); self.sidebar.pack(side="left",fill="y",padx=(0,12)); self.sidebar.pack_propagate(False)
  tk.Label(self.sidebar,text="READING COMFORT",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=16,pady=(18,8))
  self.make_scale("Text size",self.size,12,36)
  self.make_scale("Line spacing",self.spacing,0,20)
  self.make_scale("Page margins",self.margin,24,160)
  tk.Label(self.sidebar,text="QUICK MODES",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=16,pady=(18,8))
  for name,flt,sz,sp,mg in [("Study","Warm White",18,8,76),("Night","Midnight",19,10,88),("Soft Pink","Dusty Rose",18,9,82),("Migraine","Obsidian",20,11,96)]:
   b=tk.Button(self.sidebar,text=name,command=lambda a=flt,b=sz,c=sp,d=mg:self.quick(a,b,c,d),relief="flat",bd=0,pady=8); b.pack(fill="x",padx=14,pady=3)

  self.reader=tk.Frame(self.body); self.reader.pack(side="left",fill="both",expand=True)
  self.text=tk.Text(self.reader,wrap="word",undo=True,borderwidth=0,highlightthickness=0)
  self.scroll=tk.Scrollbar(self.reader,command=self.text.yview); self.text.configure(yscrollcommand=self.scroll.set)
  self.scroll.pack(side="right",fill="y"); self.text.pack(side="left",fill="both",expand=True)
  self.text.bind("<Control-o>",lambda e:self.open())
  self.footer=tk.Label(self,textvariable=self.status,anchor="w"); self.footer.pack(fill="x",padx=28,pady=(0,14))

 def make_scale(self,label,var,a,b):
  tk.Label(self.sidebar,text=label).pack(anchor="w",padx=16,pady=(8,0))
  s=tk.Scale(self.sidebar,from_=a,to=b,orient="horizontal",variable=var,showvalue=True,highlightthickness=0,bd=0,command=lambda _=None:self.format_text())
  s.pack(fill="x",padx=12)

 def quick(self,flt,sz,sp,mg):
  self.filter.set(flt); self.size.set(sz); self.spacing.set(sp); self.margin.set(mg); self.apply_theme()

 def apply_theme(self):
  bg,panel,raised,accent,fg,muted=THEMES[self.theme.get()]
  tint=FILTERS.get(self.filter.get(),"#08080C")
  self.configure(bg=bg)
  for w in (self.header,self.actions,self.body):w.configure(bg=bg)
  self.sidebar.configure(bg=panel); self.reader.configure(bg=bg)
  for parent in (self.header,self.actions,self.sidebar):
   for w in parent.winfo_children():
    try:
     if isinstance(w,tk.Label):w.configure(bg=parent.cget("bg"),fg=fg)
     elif isinstance(w,tk.Button):w.configure(bg=raised,fg=fg,activebackground=accent,activeforeground=fg)
     elif isinstance(w,tk.Scale):w.configure(bg=panel,fg=fg,troughcolor=raised,activebackground=accent)
    except:pass
  self.brand.configure(fg=fg); self.subtitle.configure(fg=muted); self.footer.configure(bg=bg,fg=muted)
  # Text remains high-contrast; selected DuskBloom color becomes the reading surface.
  self.text.configure(bg=tint,fg="#FFF8FC",insertbackground="#FFF8FC",selectbackground=accent)
  self.format_text()

 def format_text(self):
  try:
   m=self.margin.get()
   self.text.configure(font=("Segoe UI",self.size.get()),spacing1=self.spacing.get(),spacing2=max(0,self.spacing.get()//2),spacing3=self.spacing.get(),padx=m,pady=42)
  except:pass

 def open(self):
  p=filedialog.askopenfilename(filetypes=[("Documents","*.pdf *.docx *.txt"),("PDF","*.pdf"),("Word","*.docx"),("Text","*.txt")])
  if p:self.open_path(Path(p))

 def open_path(self,p):
  try:
   ext=p.suffix.lower()
   if ext==".txt":self.pages=[p.read_text(encoding="utf-8",errors="replace")]
   elif ext==".docx":
    from docx import Document; d=Document(str(p)); self.pages=["\n\n".join(x.text for x in d.paragraphs)]
   elif ext==".pdf":
    import fitz; d=fitz.open(str(p)); self.pages=[x.get_text("text") for x in d]
   else:raise ValueError("Unsupported file type")
   self.file=p; self.page=min(int(self.state.get("positions",{}).get(str(p),0)),max(0,len(self.pages)-1)); self.show()
  except Exception as e:messagebox.showerror("DuskBloom Reader","Could not open this document.\n\n"+str(e))

 def show(self):
  if not self.pages:return
  self.text.delete("1.0","end"); self.text.insert("1.0",self.pages[self.page]); self.text.mark_set("insert","1.0"); self.text.see("1.0"); self.format_text()
  self.status.set(f"{self.file.name}   •   page {self.page+1} of {len(self.pages)}"); self.title("DuskBloom Reader — "+self.file.name)
 def prev(self):
  if self.page>0:self.page-=1;self.show()
 def next(self):
  if self.page+1<len(self.pages):self.page+=1;self.show()
 def read(self):
  try:txt=self.text.get("sel.first","sel.last").strip()
  except:txt=self.text.get("insert","end").strip()
  if not txt:txt=self.text.get("1.0","end").strip()
  if not txt:return
  self.stop()
  def go():
   try:
    import pyttsx3; self.speech=pyttsx3.init(); self.speech.setProperty("rate",170); self.speech.say(txt); self.speech.runAndWait()
   except Exception:pass
  threading.Thread(target=go,daemon=True).start()
 def stop(self):
  try:
   if self.speech:self.speech.stop()
  except:pass
 def close(self):
  self.state.update(theme=self.theme.get(),filter=self.filter.get(),size=self.size.get(),spacing=self.spacing.get(),margin=self.margin.get())
  self.state.setdefault("positions",{})
  if self.file:self.state["positions"][str(self.file)]=self.page
  try:STATE.write_text(json.dumps(self.state,indent=2))
  except:pass
  self.destroy()

if __name__=="__main__":App().mainloop()
