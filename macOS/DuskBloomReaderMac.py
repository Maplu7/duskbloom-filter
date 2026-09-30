import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import fitz
from docx import Document

class Reader(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("DuskBloom Reader"); self.geometry("900x700"); self.configure(bg="#211923")
        bar=tk.Frame(self,bg="#211923"); bar.pack(fill="x",padx=18,pady=12)
        tk.Label(bar,text="DuskBloom Reader",font=("Helvetica Neue",20,"bold"),fg="#f3b6cf",bg="#211923").pack(side="left")
        tk.Button(bar,text="Open",command=self.open_file,bg="#e7a7c3",fg="#211923",relief="flat",padx=16).pack(side="right")
        self.size=tk.IntVar(value=16)
        tk.Scale(bar,from_=12,to=28,orient="horizontal",variable=self.size,command=self.resize_text,length=150,bg="#211923",fg="white",highlightthickness=0).pack(side="right",padx=14)
        self.text=tk.Text(self,wrap="word",font=("Helvetica Neue",16),bg="#2b252c",fg="#f4edf1",insertbackground="white",relief="flat",padx=35,pady=30,spacing1=3,spacing3=7)
        self.text.pack(fill="both",expand=True,padx=18,pady=(0,18))
    def resize_text(self,_=None): self.text.configure(font=("Helvetica Neue",self.size.get()))
    def open_file(self):
        p=filedialog.askopenfilename(filetypes=[("Documents","*.pdf *.txt *.docx")])
        if not p:return
        path=Path(p); out=""
        try:
            if path.suffix.lower()==".pdf":
                doc=fitz.open(p); out="\n\n".join(page.get_text() for page in doc); doc.close()
            elif path.suffix.lower()==".docx":
                doc=Document(p); out="\n\n".join(x.text for x in doc.paragraphs)
            else: out=path.read_text(errors="replace")
            self.text.delete("1.0","end"); self.text.insert("1.0",out); self.title(f"DuskBloom Reader — {path.name}")
        except Exception as e:
            self.text.delete("1.0","end"); self.text.insert("1.0",f"Could not open this document.\n\n{e}")
if __name__=="__main__": Reader().mainloop()
