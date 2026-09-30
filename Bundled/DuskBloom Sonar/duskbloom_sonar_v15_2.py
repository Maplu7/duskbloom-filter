import json, os, ssl, subprocess, threading, traceback, time, sys
import ssl
import http.client
from pathlib import Path
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "sonar_widget_log.txt"
PREFS = ROOT / "widget_settings.json"

CORE_PATHS = [
    Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "SteelSeries" / "SteelSeries Engine 3" / "coreProps.json",
    Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "SteelSeries" / "GG" / "coreProps.json",
]
CHANNELS = [("master","MASTER"),("game","GAME"),("chatRender","CHAT"),("media","MEDIA"),("aux","AUX"),("chatCapture","MIC")]

THEMES = {
 "cozy_pink":{"name":"Cozy Pink","bg":"#171217","panel":"#241b22","panel2":"#31232d","text":"#fff3f8","muted":"#bfa6b2","accent":"#f3a9c8","accent2":"#573849","border":"#49343f","bad":"#ff91aa","good":"#a9ddb9","track":"#49343f"},
 "sky_blue":{"name":"Sky Blue","bg":"#10171d","panel":"#17232c","panel2":"#20313d","text":"#f1f9ff","muted":"#a9c4d6","accent":"#8fd3ff","accent2":"#294b61","border":"#315164","bad":"#ff9fb0","good":"#9fe1c1","track":"#315164"},
 "lavender":{"name":"Lavender","bg":"#15131b","panel":"#211d2b","panel2":"#2d273a","text":"#faf6ff","muted":"#b9add0","accent":"#c6afff","accent2":"#493c69","border":"#403852","bad":"#ff9eb5","good":"#a7ddb9","track":"#403852"},
 "midnight":{"name":"Midnight","bg":"#0e1118","panel":"#151b27","panel2":"#1e2635","text":"#f4f7ff","muted":"#9ba8c1","accent":"#8eafff","accent2":"#293b68","border":"#2b3549","bad":"#ff94aa","good":"#99dcb6","track":"#2b3549"},
 "matcha":{"name":"Matcha","bg":"#111713","panel":"#1a251e","panel2":"#233129","text":"#f3fbf5","muted":"#a9c1ae","accent":"#a9d8ae","accent2":"#35523b","border":"#34473a","bad":"#f5a0aa","good":"#a9d8ae","track":"#34473a"},
 "steel":{"name":"Steel","bg":"#101214","panel":"#191d20","panel2":"#23282c","text":"#f6f7f8","muted":"#aeb6bd","accent":"#76d6ff","accent2":"#274b5b","border":"#343b40","bad":"#ff8fa6","good":"#8dd9b0","track":"#343b40"},
 "light":{"name":"Cloud Night","bg":"#15191d","panel":"#20262b","panel2":"#293138","text":"#f1f6f9","muted":"#aab9c3","accent":"#82c9ef","accent2":"#344955","border":"#3b4851","bad":"#e78294","good":"#82c59a","track":"#3b4851"} ,
 "strawberry_milk":{"name":"Strawberry Milk","bg":"#241b20","panel":"#32252c","panel2":"#3c2b34","text":"#fff2f7","muted":"#caaebc","accent":"#ff9fc6","accent2":"#633d50","border":"#503745","bad":"#ff8fa0","good":"#9ed8b5","track":"#503745"},
 "cotton_candy":{"name":"Cotton Candy","bg":"#171a24","panel":"#222636","panel2":"#2a3043","text":"#f8f4ff","muted":"#b7b8d0","accent":"#f3a7d7","accent2":"#385b78","border":"#3b4058","bad":"#ff92a2","good":"#9fe0c0","track":"#3b4058"},
 "blueberry":{"name":"Blueberry","bg":"#121728","panel":"#1b2340","panel2":"#222c50","text":"#f0f3ff","muted":"#aeb8df","accent":"#8da9ff","accent2":"#414d83","border":"#35426c","bad":"#ff93aa","good":"#9bd9bd","track":"#35426c"},
 "ocean":{"name":"Ocean","bg":"#101c21","panel":"#172a31","panel2":"#1d343d","text":"#effcff","muted":"#9ebdc5","accent":"#67c7d9","accent2":"#315b63","border":"#2d4b55","bad":"#ef8c9b","good":"#83d6ad","track":"#2d4b55"},
 "sage_rose":{"name":"Sage & Rose","bg":"#171d1a","panel":"#222b26","panel2":"#2a352f","text":"#f2f5ef","muted":"#aebcaf","accent":"#d99aaa","accent2":"#526356","border":"#3b4a40","bad":"#e98d99","good":"#a6d3b0","track":"#3b4a40"},
 "peach_cream":{"name":"Peach Cream","bg":"#251b19","panel":"#342521","panel2":"#402d28","text":"#fff4ee","muted":"#d2b6a9","accent":"#ffb49a","accent2":"#68493e","border":"#584038","bad":"#ff8f94","good":"#a9d5ad","track":"#584038"},
 "sunset":{"name":"Sunset","bg":"#21171f","panel":"#30202d","panel2":"#3b2736","text":"#fff1f6","muted":"#c3a9ba","accent":"#f092b0","accent2":"#6c4a43","border":"#503447","bad":"#f27f8d","good":"#a8d4af","track":"#503447"},
 "cherry_cola":{"name":"Cherry Cola","bg":"#1b1115","panel":"#29191f","panel2":"#342027","text":"#ffeef2","muted":"#bd9ba5","accent":"#e56b89","accent2":"#63303d","border":"#4b2934","bad":"#ff8797","good":"#9fd2ac","track":"#4b2934"},
 "mocha":{"name":"Mocha","bg":"#1d1817","panel":"#2a2321","panel2":"#342b28","text":"#f7eee8","muted":"#baa9a0","accent":"#d9a38f","accent2":"#59443b","border":"#493a35","bad":"#dc8585","good":"#a8c8a6","track":"#493a35"}
}

def log(msg):
    try:
        with LOG.open("a", encoding="utf-8") as f: f.write(msg.rstrip()+"\n")
    except: pass

def prefs_load():
    try: return json.loads(PREFS.read_text(encoding="utf-8"))
    except: return {}

def prefs_save(x):
    try: PREFS.write_text(json.dumps(x,indent=2),encoding="utf-8")
    except: pass

import urllib.request
class API:
    def __init__(self):
        self.sonar = None
        self.mode = "classic"
        self.last_stage = "Not connected"

    def _json_request(self, base, path, method="GET"):
        u = urlparse(base if "://" in base else "https://"+base)
        host, port = u.hostname, u.port
        if not host or not port: raise RuntimeError("Invalid GG address: "+base)
        if u.scheme == "https":
            ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
            con=http.client.HTTPSConnection(host,port,timeout=3,context=ctx)
        else:
            con=http.client.HTTPConnection(host,port,timeout=3)
        try:
            con.request(method, path, body=b"" if method in ("PUT","POST") else None,
                        headers={"Content-Length":"0"} if method in ("PUT","POST") else {})
            r=con.getresponse(); raw=r.read()
            body=raw.decode("utf-8",errors="replace")
            if method != "GET":
                log(f"WRITE {method} {path} -> HTTP {r.status} body={body[:220]!r}")
            if r.status < 200 or r.status >= 300:
                raise RuntimeError(f"{method} {path} returned HTTP {r.status}")
            if not raw: return {"_http_status":r.status}
            try: return json.loads(body)
            except: return body
        finally: con.close()

    def discover(self):
        self.sonar=None
        candidates=[
            Path(os.environ.get("PROGRAMDATA",r"C:\ProgramData"))/"SteelSeries"/"SteelSeries Engine 3"/"coreProps.json",
            Path(os.environ.get("PROGRAMDATA",r"C:\ProgramData"))/"SteelSeries"/"GG"/"coreProps.json",
        ]
        errors=[]

        def get_json_absolute(url, insecure=False, timeout=2.5):
            req=urllib.request.Request(url,method="GET",headers={"Accept":"application/json"})
            ctx=ssl._create_unverified_context() if insecure else None
            with urllib.request.urlopen(req,timeout=timeout,context=ctx) as r:
                raw=r.read().decode("utf-8","replace")
                if not raw.strip(): return {}
                return json.loads(raw)

        for cp in candidates:
            try:
                if not cp.exists():
                    errors.append(f"{cp}: missing")
                    continue

                props=json.loads(cp.read_text(encoding="utf-8-sig"))
                gg=str(props.get("ggEncryptedAddress") or "").strip()
                if not gg:
                    errors.append(f"{cp}: ggEncryptedAddress missing")
                    continue
                if not gg.startswith(("http://","https://")):
                    gg="https://"+gg

                log(f"DISCOVERY coreProps={cp} gg={gg}")
                data=get_json_absolute(gg.rstrip("/")+"/subApps",insecure=True)
                sonar=((data.get("subApps") or {}).get("sonar") or {})
                meta=sonar.get("metadata") or {}
                addr=str(meta.get("webServerAddress") or "").strip()

                log("DISCOVERY sonar flags enabled=%r ready=%r running=%r address=%r" %
                    (sonar.get("isEnabled"),sonar.get("isReady"),sonar.get("isRunning"),addr))

                if not addr:
                    errors.append(f"{cp}: /subApps returned no Sonar webServerAddress")
                    continue

                if not addr.startswith(("http://","https://")):
                    addr="http://"+addr
                addr=addr.replace("://localhost:","://127.0.0.1:")
                candidate=addr.rstrip("/")

                # Prove the Sonar server itself is alive before accepting it.
                mode="classic"
                try:
                    md=get_json_absolute(candidate+"/mode",insecure=candidate.startswith("https://"))
                    mode="streamer" if "stream" in str(md).lower() else "classic"
                except Exception as mode_err:
                    log("MODE probe failed; trying volume endpoint: "+repr(mode_err))

                try:
                    get_json_absolute(candidate+f"/volumeSettings/{mode}",
                                      insecure=candidate.startswith("https://"))
                except Exception:
                    # Mode may be unavailable/odd on some GG builds; classic is the known
                    # working mode on this user's installation.
                    mode="classic"
                    get_json_absolute(candidate+"/volumeSettings/classic",
                                      insecure=candidate.startswith("https://"))

                self.sonar=candidate
                self.mode=mode
                log(f"CONNECTED VERIFIED sonar={self.sonar} mode={self.mode}")
                return True

            except Exception as e:
                self.sonar=None
                errors.append(f"{cp}: {type(e).__name__}: {e}")
                log(f"DISCOVERY candidate failed {cp}: {type(e).__name__}: {e}")

        log("DISCOVERY FAILED | "+" | ".join(errors))
        raise RuntimeError("DuskBloom could not reach the local Sonar service.")
    def req(self,path,method="GET",body=None):
        if not self.sonar:
            raise RuntimeError("Sonar address is not connected")
        url=self.sonar.rstrip("/")+"/"+path.lstrip("/")
        data=None
        headers={"Accept":"application/json"}
        if body is not None:
            data=json.dumps(body).encode("utf-8")
            headers["Content-Type"]="application/json"
        elif method in ("PUT","POST","PATCH"):
            data=b""
            headers["Content-Length"]="0"

        request=urllib.request.Request(url,data=data,method=method,headers=headers)
        ctx=ssl._create_unverified_context() if url.startswith("https://") else None
        try:
            with urllib.request.urlopen(request,timeout=3,context=ctx) as r:
                raw=r.read().decode("utf-8","replace")
                status=getattr(r,"status",200)
                if method!="GET":
                    log(f"WRITE {method} {path} -> HTTP {status} body={raw[:220]!r}")
                if not raw.strip():
                    return {"_http_status":status}
                try:
                    return json.loads(raw)
                except Exception:
                    return raw
        except urllib.error.HTTPError as e:
            raw=e.read().decode("utf-8","replace")
            log(f"{method} {path} -> HTTP {e.code} body={raw[:500]!r}")
            raise RuntimeError(f"{method} {path} returned HTTP {e.code}") from e
        except Exception as e:
            log(f"{method} {path} transport error: {type(e).__name__}: {e}")
            raise

    def volumes(self):
        # Classic is the normal mixer view. Some GG releases expose the live
        # readable mixer more reliably through the streamer endpoint, which
        # includes classic settings as well.
        try:
            data=self.req("/volumeSettings/"+self.mode)
            if isinstance(data,dict) and data:
                return data
        except Exception as e:
            log("PRIMARY VOLUME READ FAILED: "+repr(e))
        for mode in ("classic","streamer"):
            if mode==self.mode: continue
            try:
                data=self.req("/volumeSettings/"+mode)
                if isinstance(data,dict) and data:
                    log(f"VOLUME READ FALLBACK: {mode}")
                    self.mode=mode
                    return data
            except Exception as e:
                log(f"VOLUME READ FALLBACK {mode} FAILED: "+repr(e))
        raise RuntimeError("Sonar mixer read failed")

    def configs(self): return self.req("/configs")
    def selected_configs(self): return self.req("/configs/selected")
    def audio_devices(self): return self.req("/audioDevices")
    def redirections(self):
        return self.req("/classicRedirections" if self.mode=="classic" else "/streamRedirections")
    def select_config(self,config_id):
        return self.req(f"/configs/{config_id}/select","PUT")

    def _channel_state(self,data,ch):
        if not isinstance(data,dict): return {}
        key=self.mode if self.mode in ("classic","streamer") else "classic"
        if ch=="master":
            root=(data.get("masters") or {})
        else:
            root=((data.get("devices") or {}).get(ch) or {})
        branch=root.get(key)
        if not isinstance(branch,dict):
            branch=root.get("classic")
        return branch if isinstance(branch,dict) else {}

    def _read_channel_percent(self,data,ch):
        branch=self._channel_state(data,ch)
        val=branch.get("volume", branch.get("Volume"))
        if isinstance(val,(int,float)):
            return float(val)*100 if float(val) <= 1.0001 else float(val)
        return None

    def set_volume(self,ch,v):
        v=max(0.0,min(1.0,float(v)))
        if self.mode=="streamer":
            path=f"/volumeSettings/streamer/monitoring/{ch}/Volume/{v:.4f}"
        else:
            path=f"/volumeSettings/classic/{ch}/Volume/{v:.4f}"
        requested=v*100
        log(f"SYNC TEST {ch}: requested={requested:.1f}% endpoint={path}")
        write=self.req(path,"PUT")
        time.sleep(0.15)
        data=self.volumes()
        actual=self._read_channel_percent(data,ch)
        if actual is None:
            log(f"SYNC RESULT {ch}: write accepted, readback shape unknown; top_keys={list(data) if isinstance(data,dict) else type(data).__name__}")
            return {"ok":None,"requested":requested,"actual":None}
        ok=abs(actual-requested)<=1.1
        log(f"SYNC RESULT {ch}: requested={requested:.1f}% backend_actual={actual:.1f}% ok={ok}")
        return {"ok":ok,"requested":requested,"actual":actual}

    def set_mute(self,ch,m):
        # Classic endpoint is known; streamer layouts vary across GG builds.
        if self.mode=="streamer":
            candidates=[
                f"/volumeSettings/streamer/monitoring/{ch}/Mute/{str(m).lower()}",
                f"/volumeSettings/streamer/{ch}/Mute/{str(m).lower()}"]
        else:
            candidates=[f"/volumeSettings/classic/{ch}/Mute/{str(m).lower()}"]
        last=None
        for path in candidates:
            try:return self.req(path,"PUT")
            except Exception as e:last=e
        raise last

    def chatmix(self):
        # ChatMix is optional: some current GG/Sonar builds do not expose this endpoint.
        try:
            return self.req("/chatMix")
        except Exception as e:
            log("CHATMIX unavailable (ignored): " + repr(e))
            return None

    def set_chatmix(self,v):
        # Do not turn a working Sonar connection into "offline" just because ChatMix is absent.
        try:
            return self.req(f"/chatMix/{v:.3f}","PUT")
        except Exception as e:
            log("CHATMIX set unavailable (ignored): " + repr(e))
            return None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.api=API(); self.prefs=prefs_load(); self.theme=self.prefs.get("theme","cozy_pink")
        if self.theme == "dark": self.theme = "cozy_pink"
        if self.theme not in THEMES:self.theme="cozy_pink"
        self.theme_order=["cozy_pink","strawberry_milk","cotton_candy","lavender","sky_blue","blueberry","ocean","sage_rose","matcha","peach_cream","sunset","cherry_cola","mocha","midnight","steel","light"]
        self.online=False; self.refreshing=False; self.user_adjusting_until=0; self.chatmix_checked=False; self.timers={}; self.vars={}; self.mutes={}; self.widgets={}
        self.compact=bool(self.prefs.get("compact",False))
        self.opacity=float(self.prefs.get("opacity",0.98))
        self.show_master=bool(self.prefs.get("show_master",True))
        self.settings_open=False
        self.topVar=tk.BooleanVar(value=bool(self.prefs.get("topmost",True)))
        self.mini=bool(self.prefs.get("mini",False))
        self.autostart=bool(self.prefs.get("autostart",True))
        self.startup_delay=int(self.prefs.get("startup_delay",12))
        self.locked_channels=set(self.prefs.get("locked_channels",[]))
        self.favorites=self.prefs.get("favorites",{"master":100,"game":75,"chatRender":70,"media":60,"aux":60,"chatCapture":80})
        self.profiles=self.prefs.get("profiles",{})
        self.app_profiles=self.prefs.get("app_profiles",{})
        self.last_auto_profile=None
        self.custom_themes=self.prefs.get("custom_themes",{})
        self.quick_levels=[25,50,75,100]
        self.drag_x=self.drag_y=0

        self.title("DuskBloom Sonar v15.2")
        self.overrideredirect(True)
        self.attributes("-topmost", bool(self.prefs.get("topmost", True)))
        try:self.attributes("-alpha",self.opacity)
        except:pass
        self.geometry(self.prefs.get("geometry","486x760+120+120"))
        self.minsize(360,90)

        # rounded-widget illusion: borderless window + carefully shaped card
        self.configure(bg="#0f0d10")
        self.shell=tk.Frame(self,bd=0,highlightthickness=1)
        self.shell.pack(fill="both",expand=True,padx=1,pady=1)

        self.build()
        self.paint()
        self.bind("<Escape>",lambda e:self.close())
        self.after(100,self.sync)
        self.after(3500,self.poll)

    def build(self):
        # ---------- Header / brand ----------
        self.header=tk.Frame(self.shell,bd=0,cursor="fleur")
        self.header.pack(fill="x",padx=18,pady=(16,9))
        self.header.bind("<ButtonPress-1>",self.drag_start); self.header.bind("<B1-Motion>",self.drag_move)

        brand=tk.Frame(self.header,bd=0,cursor="fleur"); brand.pack(side="left",fill="x",expand=True)
        brand.bind("<ButtonPress-1>",self.drag_start); brand.bind("<B1-Motion>",self.drag_move)
        self.icon=tk.Label(brand,text="✿",font=("Segoe UI Symbol",18),cursor="fleur")
        self.icon.pack(side="left",padx=(0,10))
        self.icon.bind("<ButtonPress-1>",self.drag_start); self.icon.bind("<B1-Motion>",self.drag_move)

        text=tk.Frame(brand,bd=0,cursor="fleur"); text.pack(side="left")
        text.bind("<ButtonPress-1>",self.drag_start); text.bind("<B1-Motion>",self.drag_move)
        self.titleL=tk.Label(text,text="DuskBloom Sonar",font=("Segoe UI Variable Display",16,"bold"),cursor="fleur")
        self.titleL.pack(anchor="w")
        self.status=tk.Label(text,text="soft control for your Sonar mix",font=("Segoe UI Variable Text",8),cursor="fleur")
        self.status.pack(anchor="w")
        for w in (self.titleL,self.status):
            w.bind("<ButtonPress-1>",self.drag_start); w.bind("<B1-Motion>",self.drag_move)

        self.closeB=self.icon_button(self.header,"×",self.close); self.closeB.pack(side="right",padx=(5,0))
        self.compactB=self.icon_button(self.header,"—",self.toggle_compact); self.compactB.pack(side="right",padx=(5,0))
        self.themeB=self.icon_button(self.header,"✦",self.toggle_theme); self.themeB.pack(side="right",padx=(5,0))
        self.headerPinB=self.icon_button(self.header,"📌" if self.topVar.get() else "○",self.toggle_top); self.headerPinB.pack(side="right",padx=(5,0))

        # ---------- Main body ----------
        self.body=tk.Frame(self.shell,bd=0)
        self.body.pack(fill="both",expand=True,padx=16,pady=(0,16))

        # Hero connection card
        self.livebar=tk.Frame(self.body,bd=0,highlightthickness=1)
        self.livebar.pack(fill="x",pady=(0,11))
        liveleft=tk.Frame(self.livebar,bd=0); liveleft.pack(side="left",padx=12,pady=10)
        self.dot=tk.Label(liveleft,text="●",font=("Segoe UI",8)); self.dot.pack(side="left",padx=(0,6))
        self.liveText=tk.Label(liveleft,text="SONAR • CONNECTING",font=("Segoe UI",8,"bold")); self.liveText.pack(side="left")
        self.modeText=tk.Label(self.livebar,text="connecting to SteelSeries Sonar…",font=("Segoe UI",8)); self.modeText.pack(side="right",padx=12)

        # Mixer heading
        self.mixerHead=tk.Frame(self.body,bd=0); self.mixerHead.pack(fill="x",pady=(1,5))
        self.mixerTitle=tk.Label(self.mixerHead,text="MIXER",font=("Segoe UI",8,"bold")); self.mixerTitle.pack(side="left",padx=2)
        self.mixerHint=tk.Label(self.mixerHead,text="double-click a slider for exact volume",font=("Segoe UI",7)); self.mixerHint.pack(side="right",padx=2)

        self.channels=tk.Frame(self.body,bd=0); self.channels.pack(fill="x")
        for ch,name in CHANNELS:self.card(ch,name)
        if not self.show_master:self.widgets["master"]["frame"].pack_forget()

        # ChatMix card
        self.mix=tk.Frame(self.body,bd=0,highlightthickness=1); self.mix.pack(fill="x",pady=(9,0))
        mt=tk.Frame(self.mix,bd=0); mt.pack(fill="x",padx=13,pady=(9,0))
        self.mixTitle=tk.Label(mt,text="GAME  ↔  CHAT",font=("Segoe UI",8,"bold")); self.mixTitle.pack(side="left")
        self.mixVal=tk.Label(mt,text="centered",font=("Segoe UI",8)); self.mixVal.pack(side="right")
        mr=tk.Frame(self.mix,bd=0); mr.pack(fill="x",padx=13,pady=(5,10))
        self.mixVar=tk.DoubleVar(value=0)
        self.mixScale=ttk.Scale(mr,from_=-1,to=1,variable=self.mixVar,command=self.mix_change,style="Bloom.Horizontal.TScale")
        self.mixScale.pack(fill="x")

        # Quick actions
        self.quick=tk.Frame(self.body,bd=0); self.quick.pack(fill="x",pady=(10,0))
        self.muteAllB=self.pill(self.quick,"♡  mute all",self.mute_all); self.muteAllB.pack(side="left")
        self.quietB=self.pill(self.quick,"☾  quiet",self.quiet_mode); self.quietB.pack(side="left",padx=5)
        self.resetB=self.pill(self.quick,"100% all",self.reset_all); self.resetB.pack(side="left")
        self.settingsB=self.pill(self.quick,"⚙",self.toggle_settings); self.settingsB.pack(side="right")
        self.rereadB=self.pill(self.quick,"↻",self.sync); self.rereadB.pack(side="right",padx=5)

        # Profiles
        self.profileBar=tk.Frame(self.body,bd=0,highlightthickness=1); self.profileBar.pack(fill="x",pady=(8,0))
        self.profileCaption=tk.Label(self.profileBar,text="PROFILE",font=("Segoe UI",7,"bold")); self.profileCaption.pack(side="left",padx=(11,6),pady=9)
        self.profileVar=tk.StringVar(value="Choose a profile")
        self.profileMenu=ttk.Combobox(self.profileBar,textvariable=self.profileVar,state="readonly",width=17,style="Bloom.TCombobox")
        self.profileMenu.pack(side="left",fill="x",expand=True,pady=6); self.profileMenu.bind("<<ComboboxSelected>>",self.load_profile_event)
        self.saveProfileB=self.pill(self.profileBar,"＋ save",self.save_profile_dialog); self.saveProfileB.pack(side="left",padx=6)
        self.miniModeB=self.pill(self.profileBar,"▱ mini",self.toggle_mini); self.miniModeB.pack(side="right",padx=(0,7))

        # Gentle sync status
        self.syncText=tk.Label(self.body,text="Sonar is the source of truth • changes sync both ways",font=("Segoe UI",8,"bold"),anchor="w")
        self.syncText.pack(fill="x",padx=3,pady=(7,0))

        # Collapsible settings
        self.settingsPanel=tk.Frame(self.body,bd=0,highlightthickness=1)
        self.settingsTitle=tk.Label(self.settingsPanel,text="CUSTOMIZE",font=("Segoe UI",8,"bold"),anchor="w")
        self.settingsTitle.pack(fill="x",padx=11,pady=(10,5))

        themeRow=tk.Frame(self.settingsPanel,bd=0); themeRow.pack(fill="x",padx=11,pady=3)
        tk.Label(themeRow,text="Theme",font=("Segoe UI",9)).pack(side="left")
        self.themeChoice=tk.StringVar(value=THEMES[self.theme]["name"])
        self.themeMenu=ttk.Combobox(themeRow,textvariable=self.themeChoice,state="readonly",width=18,
                                    values=[THEMES[k]["name"] for k in self.theme_order],style="Bloom.TCombobox")
        self.themeMenu.pack(side="right"); self.themeMenu.bind("<<ComboboxSelected>>",self.choose_theme)

        opRow=tk.Frame(self.settingsPanel,bd=0); opRow.pack(fill="x",padx=11,pady=4)
        tk.Label(opRow,text="Window opacity",font=("Segoe UI",9)).pack(side="left")
        self.opacityVar=tk.DoubleVar(value=self.opacity*100)
        self.opacityScale=ttk.Scale(opRow,from_=70,to=100,variable=self.opacityVar,command=self.change_opacity,style="Bloom.Horizontal.TScale")
        self.opacityScale.pack(side="right",fill="x",expand=True,padx=(18,0))

        toggles=tk.Frame(self.settingsPanel,bd=0); toggles.pack(fill="x",padx=11,pady=(6,5))
        self.masterB=self.pill(toggles,"Master ✓" if self.show_master else "Master",self.toggle_master); self.masterB.pack(side="left")
        self.startupB=self.pill(toggles,"Startup ✓" if self.autostart else "Start with Windows",self.toggle_startup); self.startupB.pack(side="left",padx=5)
        self.customB=self.pill(toggles,"Accent",self.custom_accent); self.customB.pack(side="right")

        delayrow=tk.Frame(self.settingsPanel,bd=0); delayrow.pack(fill="x",padx=11,pady=(2,6))
        tk.Label(delayrow,text="Startup delay",font=("Segoe UI",9)).pack(side="left")
        self.delayVar=tk.StringVar(value=str(self.startup_delay))
        self.delayMenu=ttk.Combobox(delayrow,textvariable=self.delayVar,state="readonly",width=8,
                                    values=["0","3","5","8","10","15","20","30"],style="Bloom.TCombobox")
        self.delayMenu.pack(side="right"); self.delayMenu.bind("<<ComboboxSelected>>",self.change_startup_delay)

        advanced=tk.Frame(self.settingsPanel,bd=0); advanced.pack(fill="x",padx=11,pady=(2,10))
        self.themeEditorB=self.pill(advanced,"✿ Theme studio",self.theme_creator); self.themeEditorB.pack(side="left")
        self.appProfileB=self.pill(advanced,"App profiles",self.app_profile_dialog); self.appProfileB.pack(side="left",padx=5)
        self.presetB=self.pill(advanced,"Sonar presets",self.preset_browser); self.presetB.pack(side="right")

        # Sonar details / footer
        self.sonarInfo=tk.Frame(self.body,bd=0,highlightthickness=1); self.sonarInfo.pack(fill="x",pady=(9,0))
        self.presetLabel=tk.Label(self.sonarInfo,text="Preset  •  reading Sonar…",font=("Segoe UI",8),anchor="w")
        self.presetLabel.pack(fill="x",padx=11,pady=(8,2))
        self.deviceLabel=tk.Label(self.sonarInfo,text="Output  •  reading Sonar…",font=("Segoe UI",8),anchor="w")
        self.deviceLabel.pack(fill="x",padx=11,pady=(2,8))

        self.actions=tk.Frame(self.body,bd=0); self.actions.pack(fill="x",pady=(9,0))
        self.themeName=tk.Label(self.actions,text=THEMES[self.theme]["name"],font=("Segoe UI",8,"bold")); self.themeName.pack(side="left",padx=2)
        self.syncB=self.pill(self.actions,"sync",self.sync); self.syncB.pack(side="right")
        self.openB=self.pill(self.actions,"open GG",self.open_gg); self.openB.pack(side="right",padx=5)
        self.topVar=tk.BooleanVar(value=bool(self.prefs.get("topmost",True)))
        

    def icon_button(self,parent,text,cmd):
        c=THEMES[self.theme]
        return tk.Button(parent,text=text,command=cmd,width=3,bd=0,relief="flat",cursor="hand2",
                         font=("Segoe UI Symbol",10,"bold"),pady=5,
                         bg=c["panel"],fg=c["muted"],activebackground=c["accent2"],
                         activeforeground=c["text"],highlightthickness=0)

    def pill(self,parent,text,cmd):
        c=THEMES[self.theme]
        return tk.Button(parent,text=text,command=cmd,bd=0,relief="flat",cursor="hand2",
                         font=("Segoe UI",8,"bold"),padx=10,pady=6,
                         bg=c["panel2"],fg=c["text"],activebackground=c["accent2"],
                         activeforeground=c["text"],highlightthickness=0)

    def card(self,ch,name):
        desc={"master":"overall output","game":"games & apps","chatRender":"voice chat","media":"music & video","aux":"extra audio","chatCapture":"microphone"}[ch]
        glyph={"master":"✦","game":"◆","chatRender":"●","media":"♪","aux":"＋","chatCapture":"♩"}[ch]
        f=tk.Frame(self.channels,bd=0,highlightthickness=1); f.pack(fill="x",pady=3)
        f.columnconfigure(2,weight=1)
        accent=tk.Frame(f,width=3,bd=0); accent.grid(row=0,column=0,rowspan=2,sticky="ns")
        g=tk.Label(f,text=glyph,width=2,font=("Segoe UI Symbol",11)); g.grid(row=0,column=1,rowspan=2,padx=(10,4),pady=9)
        labels=tk.Frame(f,bd=0); labels.grid(row=0,column=2,sticky="w",pady=(7,0))
        n=tk.Label(labels,text=name,font=("Segoe UI",9,"bold"),anchor="w"); n.pack(anchor="w")
        d=tk.Label(labels,text=desc,font=("Segoe UI",7),anchor="w"); d.pack(anchor="w")
        v=tk.DoubleVar(value=0)
        p=tk.Label(f,text="--%",width=5,font=("Segoe UI",9,"bold")); p.grid(row=0,column=3,padx=(5,6),pady=(7,0))
        controls=tk.Frame(f,bd=0); controls.grid(row=0,column=4,rowspan=2,padx=(0,7),pady=5)
        tc=THEMES[self.theme]
        favb=tk.Button(controls,text="★",width=2,bd=0,relief="flat",cursor="hand2",command=lambda c=ch:self.favorite_channel(c),
                       font=("Segoe UI Symbol",9),bg=tc["panel2"],fg=tc["accent"],activebackground=tc["accent2"],activeforeground=tc["text"],highlightthickness=0)
        favb.pack(side="left",padx=1)
        lockb=tk.Button(controls,text="○",width=2,bd=0,relief="flat",cursor="hand2",command=lambda c=ch:self.toggle_lock(c),
                        font=("Segoe UI Symbol",9),bg=tc["panel2"],fg=tc["muted"],activebackground=tc["accent2"],activeforeground=tc["text"],highlightthickness=0)
        lockb.pack(side="left",padx=1)
        b=tk.Button(controls,text="♡",width=2,bd=0,relief="flat",cursor="hand2",font=("Segoe UI Symbol",10),
                    command=lambda c=ch:self.mute(c),bg=tc["panel2"],fg=tc["muted"],
                    activebackground=tc["accent2"],activeforeground=tc["text"],highlightthickness=0)
        b.pack(side="left",padx=1)
        s=ttk.Scale(f,from_=0,to=100,variable=v,command=lambda x,c=ch:self.vol_change(c,x),style="Bloom.Horizontal.TScale")
        s.grid(row=1,column=2,columnspan=2,sticky="ew",padx=(0,8),pady=(2,8))
        self.vars[ch]=v; self.mutes[ch]=False
        self.widgets[ch]={"frame":f,"accent":accent,"glyph":g,"labels":labels,"name":n,"desc":d,"pct":p,
                          "controls":controls,"mute":b,"scale":s,"lock":lockb,"fav":favb}
        menu=tk.Menu(self,tearoff=0)
        for q in (25,50,75,100):menu.add_command(label=f"Set {q}%",command=lambda c=ch,v=q:self.set_exact(c,v))
        menu.add_separator();menu.add_command(label="Set favorite to current",command=lambda c=ch:self.set_favorite_current(c))
        menu.add_command(label="Mute / unmute",command=lambda c=ch:self.mute(c))
        for target in (f,n,d,p,s,b,lockb,favb):
            target.bind("<Button-3>",lambda e,m=menu:m.tk_popup(e.x_root,e.y_root))
        s.bind("<ButtonPress-1>",lambda e,c=ch:self.slider_press(c),add="+")
        s.bind("<ButtonRelease-1>",lambda e,c=ch:self.slider_release(c),add="+")
        s.bind("<Double-Button-1>",lambda e,c=ch:self.ask_exact(c))
        s.bind("<MouseWheel>",lambda e,c=ch:self.wheel_volume(c,e.delta))

    def paint(self):
        c=THEMES[self.theme]
        self.configure(bg=c["bg"]); self.shell.config(bg=c["bg"],highlightbackground=c["border"])
        def setbg(w,col):
            try:w.config(bg=col)
            except:pass
        for w in (self.header,self.body,self.channels,self.quick,self.actions,self.mixerHead):setbg(w,c["bg"])
        # Header contains nested brand/text frames. Paint every nested frame so
        # Windows never leaks its default white control background into the title bar.
        def paint_header_tree(widget):
            for child in widget.winfo_children():
                if isinstance(child,tk.Frame):
                    child.config(bg=c["bg"])
                    paint_header_tree(child)
        paint_header_tree(self.header)
        self.icon.config(bg=c["bg"],fg=c["accent"]); self.titleL.config(bg=c["bg"],fg=c["text"]); self.status.config(bg=c["bg"],fg=c["muted"])
        self.mixerTitle.config(bg=c["bg"],fg=c["accent"]); self.mixerHint.config(bg=c["bg"],fg=c["muted"])
        for b in (self.themeB,self.headerPinB,self.compactB,self.closeB):
            b.config(bg=c["panel"],fg=c["muted"],activebackground=c["accent2"],activeforeground=c["text"])

        self.livebar.config(bg=c["panel"],highlightbackground=c["border"])
        for child in self.livebar.winfo_children():
            try:child.config(bg=c["panel"])
            except:pass
            if isinstance(child,tk.Frame):
                for x in child.winfo_children():
                    try:x.config(bg=c["panel"])
                    except:pass
        self.dot.config(fg=c["good"] if self.online else c["bad"])
        self.liveText.config(fg=c["text"],text="SONAR • LIVE" if self.online else "SONAR • CONNECTING")
        self.modeText.config(bg=c["panel"],fg=c["muted"])

        for ch,w in self.widgets.items():
            w["frame"].config(bg=c["panel"],highlightbackground=c["border"])
            w["accent"].config(bg=c["accent"])
            w["labels"].config(bg=c["panel"]); w["controls"].config(bg=c["panel"])
            for k in ("glyph","name","desc","pct"):w[k].config(bg=c["panel"])
            w["glyph"].config(fg=c["accent"]); w["name"].config(fg=c["text"])
            w["desc"].config(fg=c["muted"]); w["pct"].config(fg=c["text"])
            muted=self.mutes[ch]
            w["mute"].config(bg=c["accent2"] if muted else c["panel2"],fg=c["bad"] if muted else c["muted"],
                             activebackground=c["accent2"],activeforeground=c["text"],text="●" if muted else "♡")
            w["lock"].config(bg=c["panel2"],fg=c["accent"] if ch in self.locked_channels else c["muted"],
                             activebackground=c["accent2"],activeforeground=c["text"],
                             text="●" if ch in self.locked_channels else "○")
            w["fav"].config(bg=c["panel2"],fg=c["accent"],activebackground=c["accent2"],activeforeground=c["text"])

        self.mix.config(bg=c["panel"],highlightbackground=c["border"])
        for w in self.mix.winfo_children():
            try:w.config(bg=c["panel"])
            except:pass
            if isinstance(w,tk.Frame):
                for x in w.winfo_children():
                    try:x.config(bg=c["panel"])
                    except:pass
        self.mixTitle.config(fg=c["text"]); self.mixVal.config(fg=c["muted"])

        self.profileBar.config(bg=c["panel"],highlightbackground=c["border"])
        self.profileCaption.config(bg=c["panel"],fg=c["accent"])
        self.syncText.config(bg=c["bg"],fg=c["muted"])
        self.themeName.config(bg=c["bg"],fg=c["accent"],text=c["name"])

        for panel in (self.settingsPanel,self.sonarInfo):
            panel.config(bg=c["panel"],highlightbackground=c["border"])
            for x in panel.winfo_children():
                try:x.config(bg=c["panel"],fg=c["text"])
                except:pass
                if isinstance(x,tk.Frame):
                    x.config(bg=c["panel"])
                    for y in x.winfo_children():
                        try:y.config(bg=c["panel"],fg=c["text"])
                        except:pass

        for b in (self.syncB,self.openB,self.muteAllB,self.resetB,self.settingsB,self.rereadB,
                  self.masterB,self.startupB,self.customB,self.saveProfileB,self.quietB,self.miniModeB,
                  self.themeEditorB,self.appProfileB,self.presetB):
            b.config(bg=c["panel2"],fg=c["text"],activebackground=c["accent2"],activeforeground=c["text"])

        st=ttk.Style(self)
        try:st.theme_use("clam")
        except:pass
        st.configure("Bloom.Horizontal.TScale",background=c["panel"],troughcolor=c["track"],
                     bordercolor=c["panel"],lightcolor=c["accent"],darkcolor=c["accent"],
                     sliderthickness=13,gripcount=0)
        st.map("Bloom.Horizontal.TScale",background=[("active",c["accent"])])
        st.configure("Bloom.TCombobox",fieldbackground=c["panel2"],background=c["panel2"],
                     foreground=c["text"],arrowcolor=c["accent"],bordercolor=c["border"],
                     lightcolor=c["border"],darkcolor=c["border"])
        st.map("Bloom.TCombobox",fieldbackground=[("readonly",c["panel2"])],
               foreground=[("readonly",c["text"])],selectbackground=[("readonly",c["panel2"])],
               selectforeground=[("readonly",c["text"])])
        self.save_prefs()

    def save_prefs(self):
        prefs_save({
            "theme":self.theme,
            "geometry":self.geometry(),
            "compact":self.compact,
            "topmost":bool(self.attributes("-topmost")),
            "opacity":self.opacity,
            "show_master":self.show_master,
            "mini":self.mini,
            "locked_channels":sorted(self.locked_channels),
            "favorites":self.favorites,
            "profiles":self.profiles,
            "app_profiles":self.app_profiles,
            "custom_themes":self.custom_themes,
            "autostart":self.autostart,
            "startup_delay":self.startup_delay
        })

    def drag_start(self,e): self.drag_x=e.x_root-self.winfo_x(); self.drag_y=e.y_root-self.winfo_y()
    def drag_move(self,e): self.geometry(f"+{e.x_root-self.drag_x}+{e.y_root-self.drag_y}")

    def bgcall(self,fn,done=None):
        def go():
            try:
                r=fn()
                if done:self.after(0,lambda:done(r))
            except Exception as e:
                log("ERROR: "+repr(e)); log(traceback.format_exc())
                self.api.sonar=None
                self.after(0,lambda:self.set_status(False,"connection problem"))
                self.after(0,lambda:self.syncText.config(text="reconnecting to SteelSeries Sonar", fg=THEMES[self.theme]["bad"]))
        threading.Thread(target=go,daemon=True).start()

    def set_status(self,on,msg):
        self.online=on; self.status.config(text=("synced to your current Sonar mix" if on else msg))
        self.modeText.config(text=(f"{self.api.mode.title()} mode • live" if on else "reconnecting…"))
        self.paint()

    @staticmethod
    def find(obj,key):
        if isinstance(obj,dict):
            if key in obj and isinstance(obj[key],dict):return obj[key]
            for v in obj.values():
                z=App.find(v,key)
                if z is not None:return z
        return None

    def sync(self):
        def fetch():
            if not self.api.sonar:
                self.api.discover()
            return self.api.volumes()
        def apply(data):
            self.refreshing=True
            try:
                for ch,_ in CHANNELS:
                    if ch == self.dragging_channel:
                        continue
                    state=self.api._channel_state(data,ch)
                    if not state:continue
                    vol=state.get("volume",state.get("Volume"))
                    mute=state.get("muted",state.get("mute",state.get("Mute")))
                    if isinstance(vol,(int,float)):
                        val=vol*100 if vol<=1.01 else vol; val=max(0,min(100,val))
                        self.vars[ch].set(val); self.widgets[ch]["pct"].config(text=f"{val:.0f}%")
                    if isinstance(mute,bool):self.mutes[ch]=mute
            finally:self.refreshing=False
            self.update_mute_all_button()
            self.set_status(True,"SONAR • LIVE")
            self.syncText.config(text="synced with SteelSeries Sonar", fg=THEMES[self.theme]["accent"])
            self.update_mute_all_button()
            if not getattr(self,"info_loaded",False):
                self.info_loaded=True; self.update_sonar_info()
            if not self.chatmix_checked:
                self.chatmix_checked=True
                self.bgcall(self.api.chatmix,self.apply_mix)
        self.bgcall(fetch,apply)

    def live_sync_loop(self):
        # Kept for compatibility. The single poll loop below owns live syncing.
        return

    def apply_mix(self,d):
        if d is None:
            # This Sonar build returned 404 for /chatMix. Hide only that optional control.
            try:
                self.mix.pack_forget()
            except Exception:
                pass
            return
        try:
            if not self.mix.winfo_manager():
                self.mix.pack(fill="x",pady=(8,0),before=self.actions)
        except Exception:
            pass
        v=None
        if isinstance(d,(int,float)):v=float(d)
        elif isinstance(d,dict):
            for k in ("balance","chatMix","value","position"):
                if isinstance(d.get(k),(int,float)):v=float(d[k]);break
        if v is not None:
            self.refreshing=True; self.mixVar.set(max(-1,min(1,v))); self.refreshing=False; self.mix_label(v)

    def refresh_profile_menu(self):
        try:self.profileMenu["values"]=["Profiles ♡"]+sorted(self.profiles)
        except:pass

    def current_levels(self): return {ch:round(float(self.vars[ch].get()),1) for ch,_ in CHANNELS}

    def save_profile_dialog(self):
        win=tk.Toplevel(self);win.title("Save profile ♡");win.attributes("-topmost",True)
        tk.Label(win,text="Profile name",font=("Segoe UI",10,"bold")).pack(padx=18,pady=(14,5))
        e=tk.Entry(win,width=24);e.pack(padx=18,pady=5);e.focus_set()
        def save():
            n=e.get().strip()
            if n:self.profiles[n]=self.current_levels();self.profileVar.set(n);self.refresh_profile_menu();self.save_prefs();win.destroy()
        tk.Button(win,text="Save current mixer",command=save).pack(pady=(6,14));e.bind("<Return>",lambda x:save())
        self.darken_dialog(win)

    def load_profile_event(self,event=None):
        if self.profileVar.get() in self.profiles:self.apply_profile(self.profileVar.get())

    def apply_profile(self,name):
        for ch,v in self.profiles.get(name,{}).items():
            if ch in self.vars and ch not in self.locked_channels:self.set_exact(ch,v)
        self.syncText.config(text=f"♡ {name} loaded",fg=THEMES[self.theme]["accent"])

    def set_favorite_current(self,ch):
        self.favorites[ch]=round(float(self.vars[ch].get()),1)
        self.syncText.config(text=f"★ {dict(CHANNELS).get(ch,ch)} favorite saved at {self.favorites[ch]:.0f}%",
                             fg=THEMES[self.theme]["accent"])
        self.save_prefs()

    def favorite_channel(self,ch):
        if ch not in self.locked_channels:self.set_exact(ch,float(self.favorites.get(ch,75)))

    def toggle_lock(self,ch):
        if ch in self.locked_channels:self.locked_channels.remove(ch)
        else:self.locked_channels.add(ch)
        self.widgets[ch]["lock"].config(text="🔒" if ch in self.locked_channels else "🔓");self.save_prefs()

    def quiet_mode(self):
        for ch,v in {"master":55,"game":35,"chatRender":60,"media":25,"aux":25,"chatCapture":75}.items():
            if ch not in self.locked_channels:self.set_exact(ch,v)
        self.syncText.config(text="☾ Quiet mode",fg=THEMES[self.theme]["accent"])

    def toggle_mini(self):
        self.mini=not self.mini
        if self.mini:
            for ch,_ in CHANNELS:self.widgets[ch]["frame"].pack_forget()
            self.profileBar.pack_forget();self.sonarInfo.pack_forget();self.geometry(f"486x168+{self.winfo_x()}+{self.winfo_y()}")
        else:
            for ch,_ in CHANNELS:
                if ch!="master" or self.show_master:self.widgets[ch]["frame"].pack(fill="x",pady=3)
            self.profileBar.pack(fill="x",pady=(7,0));self.sonarInfo.pack(fill="x",pady=(8,0));self.geometry(f"486x760+{self.winfo_x()}+{self.winfo_y()}")
        self.save_prefs()

    def theme_creator(self):
        win=tk.Toplevel(self);win.title("Theme Creator ✿");win.attributes("-topmost",True)
        tk.Label(win,text="Make your own theme ♡",font=("Segoe UI",12,"bold")).pack(padx=18,pady=(14,8))
        name=tk.Entry(win,width=26);name.insert(0,"My Theme");name.pack(pady=4)
        picks={k:THEMES[self.theme][k] for k in ("bg","panel","text","accent","border")}
        for label,key in (("Background","bg"),("Cards","panel"),("Text","text"),("Accent","accent"),("Border","border")):
            row=tk.Frame(win);row.pack(fill="x",padx=18,pady=3);tk.Label(row,text=label,width=12,anchor="w").pack(side="left")
            btn=tk.Button(row,text=picks[key],width=12)
            def choose(k=key,b=btn):
                col=colorchooser.askcolor(color=picks[k],title=f"Choose {k}")[1]
                if col:picks[k]=col;b.config(text=col)
            btn.config(command=choose);btn.pack(side="right")
        def save():
            key="custom_"+re.sub(r"[^a-z0-9]+","_",name.get().lower()).strip("_")
            base=dict(THEMES[self.theme]);base.update(picks);base["name"]=name.get().strip() or "My Theme";THEMES[key]=base;self.custom_themes[key]=base
            if key not in self.theme_order:self.theme_order.append(key)
            self.theme=key;self.themeMenu["values"]=[THEMES[k]["name"] for k in self.theme_order];self.paint();self.save_prefs();win.destroy()
        tk.Button(win,text="Save theme ✿",command=save).pack(pady=14)
        self.darken_dialog(win)

    def app_profile_dialog(self):
        win=tk.Toplevel(self);win.title("App Profiles 🎮");win.attributes("-topmost",True)
        tk.Label(win,text="Switch profile when an app is running",font=("Segoe UI",10,"bold")).pack(padx=18,pady=(14,4))
        app=tk.Entry(win,width=36);app.insert(0,"Discord.exe");app.pack(pady=5)
        prof=ttk.Combobox(win,state="readonly",values=sorted(self.profiles),width=28);prof.pack(pady=5)
        def save():
            if app.get().strip() and prof.get():self.app_profiles[app.get().strip().lower()]=prof.get();self.save_prefs();win.destroy()
        tk.Button(win,text="Save app profile",command=save).pack(pady=(6,14))
        self.darken_dialog(win)

    def check_app_profiles(self):
        try:
            out=subprocess.check_output(["tasklist","/FO","CSV","/NH"],creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0)).decode(errors="ignore").lower()
            for exe,profile in self.app_profiles.items():
                if exe in out and self.last_auto_profile!=profile:self.last_auto_profile=profile;self.apply_profile(profile);break
        except:pass
        self.after(5000,self.check_app_profiles)

    def preset_browser(self): self.bgcall(self.api.configs,self._show_presets)

    def _show_presets(self,data):
        win=tk.Toplevel(self);win.title("Sonar Presets 🎧");win.attributes("-topmost",True)
        tk.Label(win,text="Actual Sonar presets",font=("Segoe UI",11,"bold")).pack(padx=15,pady=(12,6))
        box=tk.Listbox(win,width=48,height=14);box.pack(padx=15,pady=5);found=[]
        def walk(x):
            if isinstance(x,dict):
                if isinstance(x.get("id"),str) and isinstance(x.get("name"),str):found.append((x["name"],x["id"]))
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
        walk(data);unique=[];seen=set()
        for item in found:
            if item[1] not in seen:seen.add(item[1]);unique.append(item)
        for n,i in unique:box.insert("end",n)
        def select():
            if not box.curselection():return
            n,i=unique[box.curselection()[0]];self.bgcall(lambda:self.api.select_config(i),lambda r:self.syncText.config(text=f"🎧 {n}",fg=THEMES[self.theme]["accent"]));win.destroy()
        tk.Button(win,text="Use selected preset",command=select).pack(pady=(4,12))
        self.darken_dialog(win)

    def darken_dialog(self,win):
        c=THEMES[self.theme]
        try:win.configure(bg=c["bg"])
        except:pass
        def walk(w):
            for child in w.winfo_children():
                try:
                    if isinstance(child,(tk.Frame,tk.Label)):
                        child.configure(bg=c["bg"],fg=c["text"] if isinstance(child,tk.Label) else None)
                    elif isinstance(child,tk.Button):
                        child.configure(bg=c["panel2"],fg=c["text"],activebackground=c["accent2"],
                                        activeforeground=c["text"],highlightthickness=0,bd=0)
                    elif isinstance(child,tk.Entry):
                        child.configure(bg=c["panel2"],fg=c["text"],insertbackground=c["text"],
                                        relief="flat",highlightthickness=1,highlightbackground=c["border"])
                    elif isinstance(child,tk.Listbox):
                        child.configure(bg=c["panel2"],fg=c["text"],selectbackground=c["accent"],
                                        selectforeground=c["bg"],highlightbackground=c["border"])
                except:pass
                walk(child)
        walk(win)

    def set_exact(self,ch,value):
        self.user_adjusting_until=time.time()+2.0
        self.vars[ch].set(value); self.widgets[ch]["pct"].config(text=f"{value}%")
        self.bgcall(lambda:self.api.set_volume(ch,value/100),lambda r:self.show_sync_result(ch,r))

    def ask_exact(self,ch):
        win=tk.Toplevel(self); win.title("Exact volume"); win.resizable(False,False)
        win.attributes("-topmost",True)
        tk.Label(win,text=f"{dict(CHANNELS).get(ch,ch)} volume %").pack(padx=18,pady=(14,5))
        ent=tk.Entry(win,width=10,justify="center"); ent.insert(0,str(round(self.vars[ch].get()))); ent.pack(pady=4); ent.focus_set()
        def go():
            try:v=max(0,min(100,float(ent.get()))); self.set_exact(ch,v); win.destroy()
            except:pass
        tk.Button(win,text="Set",command=go).pack(pady=(4,14)); ent.bind("<Return>",lambda e:go())
        self.darken_dialog(win)

    def wheel_volume(self,ch,delta):
        step=2 if delta>0 else -2
        self.set_exact(ch,max(0,min(100,round(self.vars[ch].get()+step))))

    def mute_all(self):
        all_muted=all(bool(self.mutes.get(ch,False)) for ch,_ in CHANNELS)
        target=not all_muted
        self.user_adjusting_until=time.time()+2.0

        def work():
            out=[]
            for ch,_ in CHANNELS:
                try:
                    result=self.api.set_mute(ch,target)
                    out.append((ch,True,result))
                except Exception as e:
                    out.append((ch,False,e))
            return out

        def done(results):
            failed=[ch for ch,ok,_ in results if not ok]
            for ch,_ in CHANNELS:
                if ch not in failed:
                    self.mutes[ch]=target
            self.update_mute_all_button()
            if failed:
                self.syncText.config(
                    text="Mute update incomplete • retrying Sonar sync",
                    fg=THEMES[self.theme]["bad"]
                )
            else:
                self.online=True
                self.syncText.config(
                    text="All channels muted • synced" if target else "All channels unmuted • synced",
                    fg=THEMES[self.theme]["accent"]
                )
            self.paint()
            self.after(350,self.sync)

        self.bgcall(work,done)

    def update_mute_all_button(self):
        if not hasattr(self,"muteAllB"): return
        all_muted=all(bool(self.mutes.get(ch,False)) for ch,_ in CHANNELS)
        self.muteAllB.config(text="♡ unmute all" if all_muted else "♡ mute all")


    def reset_all(self):
        for ch,_ in CHANNELS:self.set_exact(ch,100)

    def toggle_settings(self):
        self.settings_open=not self.settings_open
        if self.settings_open:self.settingsPanel.pack(fill="x",pady=(8,0),before=self.sonarInfo)
        else:self.settingsPanel.pack_forget()

    def choose_theme(self,event=None):
        name=self.themeChoice.get()
        for k,v in THEMES.items():
            if v["name"]==name:self.theme=k;break
        self.paint()

    def change_opacity(self,x):
        self.opacity=max(.70,min(1.0,float(x)/100))
        try:self.attributes("-alpha",self.opacity)
        except:pass

    def toggle_master(self):
        self.show_master=not self.show_master
        f=self.widgets["master"]["frame"]
        if self.show_master:f.pack(fill="x",pady=4,before=self.widgets["game"]["frame"])
        else:f.pack_forget()
        self.masterB.config(text="Master ✓" if self.show_master else "Master")

    def startup_path(self):
        # Kept for cleanup of older builds that used a Startup-folder BAT.
        return Path(os.environ.get("APPDATA",""))/"Microsoft"/"Windows"/"Start Menu"/"Programs"/"Startup"/"Sonar Widget v10.2.bat"

    def _startup_command(self):
        if getattr(sys, "frozen", False):
            return f'"{Path(sys.executable).resolve()}"'
        pyw = Path(sys.executable).with_name("pythonw.exe")
        runner = pyw if pyw.exists() else Path(sys.executable)
        return f'"{runner}" "{Path(__file__).resolve()}"'

    def install_startup(self):
        import winreg
        # Remove the fragile old BAT if present.
        try:
            old=self.startup_path()
            if old.exists(): old.unlink()
        except Exception: pass
        key=winreg.CreateKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run")
        winreg.SetValueEx(key,"DuskBloom Sonar",0,winreg.REG_SZ,self._startup_command())
        winreg.CloseKey(key)
        return True

    def remove_startup(self):
        import winreg
        try:
            key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_SET_VALUE)
            try: winreg.DeleteValue(key,"DuskBloom Sonar")
            finally: winreg.CloseKey(key)
        except FileNotFoundError: pass
        try:
            old=self.startup_path()
            if old.exists(): old.unlink()
        except Exception: pass

    def ensure_startup(self):
        if not self.autostart:return
        try:
            self.install_startup()
            self.startupB.config(text="Startup ✓")
            log("AUTOSTART registry entry verified")
        except Exception as e:
            self.autostart=False
            self.startupB.config(text="Start with Windows")
            log("AUTOSTART ERROR: "+repr(e))

    def toggle_startup(self):
        try:
            if self.autostart:
                self.autostart=False; self.remove_startup(); self.startupB.config(text="Start with Windows")
            else:
                self.install_startup(); self.autostart=True; self.startupB.config(text="Startup ✓")
            self.save_prefs()
        except Exception as e:messagebox.showerror("Startup",str(e))

    def change_startup_delay(self,event=None):
        # Registry startup is immediate and reliable; keep the preference only for compatibility.
        try:self.startup_delay=int(self.delayVar.get())
        except:return
        self.save_prefs()

    def custom_accent(self):
        color=colorchooser.askcolor(title="Pick your cute accent")[1]
        if not color:return
        THEMES[self.theme]["accent"]=color
        THEMES[self.theme]["accent2"]=color
        self.paint()

    def update_sonar_info(self):
        def fetch():
            result={}
            for key,fn in (("selected",self.api.selected_configs),("devices",self.api.audio_devices),("routes",self.api.redirections)):
                try:result[key]=fn()
                except Exception as e:result[key]={"error":str(e)}
            return result
        def apply(d):
            selected=d.get("selected")
            preset="Sonar preset connected"
            if isinstance(selected,dict):
                names=[]
                def walk(x):
                    if isinstance(x,dict):
                        for k,v in x.items():
                            if str(k).lower() in ("name","configname","presetname") and isinstance(v,str):names.append(v)
                            else:walk(v)
                    elif isinstance(x,list):
                        for v in x:walk(v)
                walk(selected)
                if names:preset="Preset: "+", ".join(dict.fromkeys(names[:3]))
            self.presetLabel.config(text=preset)
            routes=d.get("routes"); device="Output routing connected"
            if isinstance(routes,dict):
                names=[]
                def walk2(x):
                    if isinstance(x,dict):
                        for k,v in x.items():
                            if str(k).lower() in ("name","devicename","friendlyname") and isinstance(v,str):names.append(v)
                            else:walk2(v)
                    elif isinstance(x,list):
                        for v in x:walk2(v)
                walk2(routes)
                if names:device="Output: "+", ".join(dict.fromkeys(names[:2]))
            self.deviceLabel.config(text=device)
        self.bgcall(fetch,apply)

    def show_sync_result(self,ch,r):
        c=THEMES[self.theme]
        label={"master":"MASTER","game":"GAME","chatRender":"CHAT","media":"MEDIA","aux":"AUX","chatCapture":"MIC"}.get(ch,ch)
        if isinstance(r,dict) and r.get("ok") is True:
            self.syncText.config(text=f"✓ Sonar {label} • {r['actual']:.0f}%",fg=c["good"])
        elif isinstance(r,dict) and r.get("ok") is False:
            self.syncText.config(text=f"✕ {label}: widget {r['requested']:.0f}% • Sonar {r['actual']:.0f}%",fg=c["bad"])
        else:
            self.syncText.config(text=f"⚠ {label}: write sent • readback unknown",fg=c["accent"])

    def mix_label(self,v):
        self.mixVal.config(text="centered" if abs(v)<.05 else f"{abs(v)*100:.0f}% {'game' if v<0 else 'chat'}")

    def slider_press(self,ch):
        self.dragging_channel=ch
        self.user_adjusting_until=time.time()+3.0

    def slider_release(self,ch):
        # Commit the exact final slider position to the real Sonar engine,
        # then wait before reading back so the UI never fights the drag.
        value=max(0,min(100,float(self.vars[ch].get())))
        self.user_adjusting_until=time.time()+2.0
        self.dragging_channel=None
        if ch in self.timers:
            try:self.after_cancel(self.timers[ch])
            except:pass
        self.bgcall(lambda:self.api.set_volume(ch,value/100),
                    lambda r:self.show_sync_result(ch,r))

    def vol_change(self,ch,x):
        if ch in self.locked_channels:
            self.syncText.config(text=f"🔒 {dict(CHANNELS).get(ch,ch)} is locked",fg=THEMES[self.theme]["accent"]); return
        x=float(x); self.user_adjusting_until=time.time()+2.0; self.widgets[ch]["pct"].config(text=f"{x:.0f}%")
        if self.refreshing:return
        if ch in self.timers:
            try:self.after_cancel(self.timers[ch])
            except:pass
        # A small debounce keeps the slider buttery instead of flooding GG with writes.
        self.timers[ch]=self.after(220,lambda v=x,c=ch:self.bgcall(
            lambda:self.api.set_volume(c,v/100),lambda r:self.show_sync_result(c,r)))

    def mute(self,ch):
        self.mutes[ch]=not self.mutes[ch]; self.paint()
        self.bgcall(lambda:self.api.set_mute(ch,self.mutes[ch]))

    def mix_change(self,x):
        v=float(x); self.user_adjusting_until=time.time()+0.8; self.mix_label(v)
        if self.refreshing:return
        if "mix" in self.timers:
            try:self.after_cancel(self.timers["mix"])
            except:pass
        self.timers["mix"]=self.after(150,lambda:self.bgcall(lambda:self.api.set_chatmix(v)))

    def poll(self):
        if self.dragging_channel is None and time.time() >= self.user_adjusting_until:
            if not self.online:
                self.api.sonar=None
            self.sync()
        self.after(5000 if self.online else 8000,self.poll)

    def toggle_theme(self):
        i=self.theme_order.index(self.theme) if self.theme in self.theme_order else 0
        self.theme=self.theme_order[(i+1)%len(self.theme_order)]
        self.paint()
        try:
            self.themeName.config(text=THEMES[self.theme]["name"])
            self.themeChoice.set(THEMES[self.theme]["name"])
        except:pass

    def toggle_top(self):
        v=not bool(self.attributes("-topmost"))
        self.attributes("-topmost",v)
        self.topVar.set(v)
        self.headerPinB.config(text="📌" if v else "○")
        self.save_prefs()

    def toggle_compact(self):
        self.compact=not self.compact
        if self.compact:
            self.body.pack_forget(); self.geometry(f"370x82+{self.winfo_x()}+{self.winfo_y()}"); self.compactB.config(text="□")
        else:
            self.body.pack(fill="both",expand=True,padx=14,pady=(0,14))
            self.geometry(f"486x760+{self.winfo_x()}+{self.winfo_y()}"); self.compactB.config(text="—")

    def open_gg(self):
        p=Path(r"C:\Program Files\SteelSeries\GG\SteelSeriesGG.exe")
        try:
            if p.exists():subprocess.Popen([str(p)])
            else:os.startfile("steelseriesgg://")
        except Exception as e:messagebox.showerror("Open GG",str(e))

    def close(self):
        prefs_save({"theme":self.theme,"geometry":self.geometry(),"compact":self.compact,
                    "topmost":bool(self.attributes("-topmost")),"opacity":self.opacity,
                     "show_master":self.show_master,"mini":self.mini,"locked_channels":sorted(self.locked_channels),
                    "favorites":self.favorites,"profiles":self.profiles,"app_profiles":self.app_profiles,"custom_themes":self.custom_themes,"autostart":self.autostart,"startup_delay":self.startup_delay})
        self.destroy()

def main():
    LOG.write_text("DuskBloom Sonar v15.2 log\n",encoding="utf-8")
    try:App().mainloop()
    except Exception as e:
        log(traceback.format_exc())
        try:messagebox.showerror("Sonar Widget",f"Startup error:\n{e}\n\nDetails saved to:\n{LOG}")
        except:pass

if __name__=="__main__":main()
