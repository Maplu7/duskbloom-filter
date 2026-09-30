import tkinter as tk
from tkinter import ttk
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class Center(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DuskBloom Center")
        self.geometry("560x430")
        self.configure(bg="#211923")
        self.resizable(False, False)
        tk.Label(self,text="DuskBloom",font=("Helvetica Neue",28,"bold"),fg="#f3b6cf",bg="#211923").pack(pady=(32,2))
        tk.Label(self,text="soft tools for a gentler screen",font=("Helvetica Neue",13),fg="#eadde5",bg="#211923").pack(pady=(0,24))
        box=tk.Frame(self,bg="#2d222e",padx=22,pady=18); box.pack(fill="x",padx=34)
        self.card(box,"Screen","Low-memory tint overlay — no screen recording","DuskBloomScreenMac")
        self.card(box,"Reader","Comfortable local document reader","DuskBloomReaderMac")
        tk.Label(self,text="DuskBloom Web for Zen/Firefox is included in the release folder.",wraplength=470,justify="left",fg="#cdbfc8",bg="#211923").pack(padx=38,pady=22,anchor="w")
    def card(self,parent,name,desc,exe):
        row=tk.Frame(parent,bg="#2d222e"); row.pack(fill="x",pady=8)
        text=tk.Frame(row,bg="#2d222e"); text.pack(side="left",fill="x",expand=True)
        tk.Label(text,text=name,font=("Helvetica Neue",16,"bold"),fg="white",bg="#2d222e").pack(anchor="w")
        tk.Label(text,text=desc,fg="#cdbfc8",bg="#2d222e").pack(anchor="w")
        tk.Button(row,text="Open",command=lambda:self.open_app(exe),bg="#e7a7c3",fg="#211923",relief="flat",padx=16,pady=7).pack(side="right")
    def open_app(self,name):
        app=ROOT.parent / f"{name}.app"
        if app.exists(): subprocess.Popen(["open",str(app)])
        else:
            py=ROOT / f"{name}.py"
            if py.exists(): subprocess.Popen([sys.executable,str(py)])
if __name__=="__main__": Center().mainloop()
