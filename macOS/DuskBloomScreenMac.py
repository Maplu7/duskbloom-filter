import tkinter as tk
import json
from pathlib import Path

CFG=Path.home()/".duskbloom_screen_mac.json"
PRESETS={"Cozy Pink":"#b56f8d","Warm":"#b08a62","Night":"#3b3655","Soft Gray":"#77727a"}

class Overlay:
    def __init__(self,root,screen,alpha,color):
        x,y,w,h=screen
        win=tk.Toplevel(root); win.overrideredirect(True); win.geometry(f"{w}x{h}+{x}+{y}")
        win.configure(bg=color); win.attributes("-alpha",alpha); win.attributes("-topmost",True)
        try: win.attributes("-transparent",False)
        except: pass
        win.bind("<Button-1>",lambda e:None)
        self.win=win
    def set(self,color,alpha):
        self.win.configure(bg=color); self.win.attributes("-alpha",alpha)

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("DuskBloom Screen"); self.geometry("430x390"); self.configure(bg="#211923")
        self.overlays=[]; self.enabled=tk.BooleanVar(value=True); self.intensity=tk.DoubleVar(value=18); self.preset=tk.StringVar(value="Cozy Pink")
        self.load()
        tk.Label(self,text="DuskBloom Screen",font=("Helvetica Neue",23,"bold"),fg="#f3b6cf",bg="#211923").pack(pady=(25,4))
        tk.Label(self,text="low-memory overlay • no screen recording",fg="#cdbfc8",bg="#211923").pack()
        tk.Checkbutton(self,text="Filter enabled",variable=self.enabled,command=self.apply,bg="#211923",fg="white",selectcolor="#2d222e",activebackground="#211923").pack(pady=18)
        tk.Label(self,text="Preset",fg="white",bg="#211923").pack()
        tk.OptionMenu(self,self.preset,*PRESETS.keys(),command=lambda _:self.apply()).pack(pady=5)
        tk.Label(self,text="Intensity",fg="white",bg="#211923").pack(pady=(16,0))
        tk.Scale(self,from_=3,to=45,orient="horizontal",variable=self.intensity,command=lambda _:self.apply(),length=300,bg="#211923",fg="white",highlightthickness=0).pack()
        tk.Button(self,text="Quit DuskBloom Screen",command=self.quit_all,bg="#e7a7c3",fg="#211923",relief="flat",padx=18,pady=8).pack(pady=24)
        self.after(200,self.make_overlays); self.protocol("WM_DELETE_WINDOW",self.iconify)
    def screens(self):
        # Tk reports the combined desktop bounds without reading pixels.
        return [(0,0,self.winfo_screenwidth(),self.winfo_screenheight())]
    def make_overlays(self):
        color=PRESETS[self.preset.get()]; a=self.intensity.get()/100 if self.enabled.get() else 0
        for s in self.screens(): self.overlays.append(Overlay(self,s,a,color))
        self.lift()
    def apply(self):
        color=PRESETS[self.preset.get()]; a=self.intensity.get()/100 if self.enabled.get() else 0
        for o in self.overlays:o.set(color,a)
        self.save()
    def save(self):
        try: CFG.write_text(json.dumps({"enabled":self.enabled.get(),"intensity":self.intensity.get(),"preset":self.preset.get()}))
        except: pass
    def load(self):
        try:
            d=json.loads(CFG.read_text()); self.enabled.set(d.get("enabled",True)); self.intensity.set(d.get("intensity",18)); self.preset.set(d.get("preset","Cozy Pink"))
        except: pass
    def quit_all(self):
        for o in self.overlays:o.win.destroy()
        self.destroy()
if __name__=="__main__": App().mainloop()
