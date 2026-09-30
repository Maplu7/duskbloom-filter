import os,sys,json,threading,tkinter as tk
from tkinter import filedialog,messagebox,ttk
from pathlib import Path
APP=Path(os.getenv('LOCALAPPDATA',Path.home()))/'DuskBloom'/'Reader'; APP.mkdir(parents=True,exist_ok=True)
STATE=APP/'state.json'
THEMES={'Cozy Pink':('#241a20','#35252e','#f4d6e4','#fff5fa'),'Sky Blue':('#17232d','#223746','#b9dff5','#f4fbff'),'Obsidian':('#111214','#1c1e22','#d5d7dc','#f5f5f5')}
PRESETS={'Soft':('#241a20','#fff5fa'),'Warm':('#2a211c','#fff1df'),'Night':('#101216','#e3e5e8'),'Paper':('#ddd2bc','#211c17')}
class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title('DuskBloom Reader'); self.geometry('1080x720'); self.minsize(760,520); self.file=None; self.pages=[]; self.page=0; self.speech=None
  try:self.state=json.loads(STATE.read_text())
  except:self.state={}
  self.theme=tk.StringVar(value=self.state.get('theme','Cozy Pink')); self.size=tk.IntVar(value=self.state.get('size',16)); self.spacing=tk.IntVar(value=self.state.get('spacing',6)); self.status=tk.StringVar(value='Ready — drop a PDF, DOCX or TXT here')
  self.build(); self.apply_theme(); self.protocol('WM_DELETE_WINDOW',self.close)
  if len(sys.argv)>1 and Path(sys.argv[-1]).exists(): self.open_path(Path(sys.argv[-1]))
 def build(self):
  self.top=tk.Frame(self); self.top.pack(fill='x',padx=14,pady=(12,6)); tk.Label(self.top,text='DuskBloom Reader  🌷',font=('Segoe UI',18,'bold')).pack(side='left')
  for t,c in [('Open',self.open),('◀',self.prev),('▶',self.next),('Read aloud',self.read),('Stop',self.stop)]: tk.Button(self.top,text=t,command=c,relief='flat',padx=12,pady=7).pack(side='left',padx=4)
  ttk.Combobox(self.top,textvariable=self.theme,values=list(THEMES),state='readonly',width=11).pack(side='right'); self.theme.trace_add('write',lambda *_:self.apply_theme())
  bar=tk.Frame(self); bar.pack(fill='x',padx=14,pady=4); tk.Label(bar,text='Text size').pack(side='left'); tk.Scale(bar,from_=11,to=30,orient='horizontal',variable=self.size,command=lambda _:self.format_text(),showvalue=True,length=150).pack(side='left'); tk.Label(bar,text='Spacing').pack(side='left',padx=(16,0)); tk.Scale(bar,from_=0,to=18,orient='horizontal',variable=self.spacing,command=lambda _:self.format_text(),showvalue=True,length=130).pack(side='left')
  for p in PRESETS: tk.Button(bar,text=p,command=lambda x=p:self.preset(x),relief='flat').pack(side='right',padx=3)
  self.text=tk.Text(self,wrap='word',undo=True,borderwidth=0,padx=42,pady=30); self.text.pack(fill='both',expand=True,padx=14,pady=8); self.text.bind('<Control-o>',lambda e:self.open()); self.text.bind('<Control-plus>',lambda e:self.size.set(min(30,self.size.get()+1))); self.text.bind('<Control-minus>',lambda e:self.size.set(max(11,self.size.get()-1)))
  tk.Label(self,textvariable=self.status,anchor='w').pack(fill='x',padx=16,pady=(0,10)); self.drop_target_register_safe()
 def drop_target_register_safe(self): pass
 def apply_theme(self):
  bg,panel,accent,fg=THEMES[self.theme.get()]; self.configure(bg=bg)
  for w in (self.top,): w.configure(bg=bg)
  for w in self.top.winfo_children():
   try:w.configure(bg=panel,fg=fg,activebackground=accent)
   except:pass
  self.text.configure(bg=panel,fg=fg,insertbackground=fg,selectbackground=accent); self.format_text()
 def preset(self,n):
  bg,fg=PRESETS[n]; self.text.configure(bg=bg,fg=fg,insertbackground=fg); self.status.set(n+' reading preset')
 def format_text(self):
  try:self.text.configure(font=('Segoe UI',self.size.get()),spacing1=self.spacing.get(),spacing2=self.spacing.get()//2,spacing3=self.spacing.get())
  except:pass
 def open(self):
  p=filedialog.askopenfilename(filetypes=[('Documents','*.pdf *.docx *.txt'),('PDF','*.pdf'),('Word','*.docx'),('Text','*.txt')]);
  if p:self.open_path(Path(p))
 def open_path(self,p):
  try:
   ext=p.suffix.lower(); self.pages=[]
   if ext=='.txt': self.pages=[p.read_text(encoding='utf-8',errors='replace')]
   elif ext=='.docx':
    from docx import Document; d=Document(str(p)); self.pages=['\n\n'.join(x.text for x in d.paragraphs)]
   elif ext=='.pdf':
    import fitz; d=fitz.open(str(p)); self.pages=[x.get_text('text') for x in d]
   else: raise ValueError('Unsupported file type')
   self.file=p; self.page=min(int(self.state.get('positions',{}).get(str(p),0)),max(0,len(self.pages)-1)); self.show(); self.state.setdefault('recent',[]); self.state['recent']=[str(p)]+[x for x in self.state['recent'] if x!=str(p)][:7]
  except Exception as e: messagebox.showerror('DuskBloom Reader','Could not open this document.\n\n'+str(e))
 def show(self):
  if not self.pages:return
  self.text.delete('1.0','end'); self.text.insert('1.0',self.pages[self.page]); self.text.edit_modified(False); self.status.set(f'{self.file.name}   •   page {self.page+1} of {len(self.pages)}'); self.title('DuskBloom Reader — '+self.file.name)
 def prev(self):
  if self.page>0:self.page-=1;self.show()
 def next(self):
  if self.page+1<len(self.pages):self.page+=1;self.show()
 def read(self):
  txt=self.text.get('insert','end').strip() or self.text.get('1.0','end').strip()
  if not txt:return
  self.stop()
  def go():
   try:
    import pyttsx3; self.speech=pyttsx3.init(); self.speech.setProperty('rate',175); self.speech.say(txt); self.speech.runAndWait()
   except Exception:pass
  threading.Thread(target=go,daemon=True).start()
 def stop(self):
  try:
   if self.speech:self.speech.stop()
  except:pass
 def close(self):
  self.state['theme']=self.theme.get(); self.state['size']=self.size.get(); self.state['spacing']=self.spacing.get(); self.state.setdefault('positions',{})
  if self.file:self.state['positions'][str(self.file)]=self.page
  try:STATE.write_text(json.dumps(self.state,indent=2))
  except:pass
  self.destroy()
if __name__=='__main__': App().mainloop()
