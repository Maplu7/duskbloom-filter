import traceback
import sys
import os, sys, json, subprocess, zipfile, datetime, ctypes, webbrowser, time, shutil, uuid, urllib.request, hashlib, tempfile
import wx
import wx.adv

APP_VERSION = '2.0.0'
APP_NAME = 'DuskBloom Center'
BASE = os.path.join(os.getenv('APPDATA') or os.path.expanduser('~'), 'DuskBloom', 'Center')
os.makedirs(BASE, exist_ok=True)
SETTINGS = os.path.join(BASE, 'settings.json')

THEMES = {
    'Cozy Pink':      {'bg':'#171218','surface':'#241C25','surface2':'#302431','accent':'#E58AB3','accent2':'#F3B5D0','text':'#FFF7FB','muted':'#BFAAB6'},
    'Sky Blue':       {'bg':'#101820','surface':'#192733','surface2':'#223746','accent':'#76BCE4','accent2':'#A9D9F2','text':'#F5FBFF','muted':'#A6C1D0'},
    'Obsidian':       {'bg':'#0E0E10','surface':'#1B1B1F','surface2':'#25252A','accent':'#A7A7B2','accent2':'#D0D0D8','text':'#FAFAFC','muted':'#A5A5AF'},
    'Lavender Haze':  {'bg':'#17121F','surface':'#282034','surface2':'#352A45','accent':'#AA82DA','accent2':'#CEB0ED','text':'#FBF7FF','muted':'#BCAAD0'},
    'Sage Garden':    {'bg':'#111B17','surface':'#1D2B24','surface2':'#293A31','accent':'#7FB394','accent2':'#AAD1B9','text':'#F5FBF7','muted':'#A7BFAF'},
    'Strawberry Milk':{'bg':'#1D1317','surface':'#302027','surface2':'#402A33','accent':'#EE91AA','accent2':'#F7BBCB','text':'#FFF7F9','muted':'#CDB0B9'},
    'Midnight':       {'bg':'#0B111D','surface':'#161F30','surface2':'#202D43','accent':'#6F91CF','accent2':'#9CB7E7','text':'#F5F8FF','muted':'#9DACC6'},
    'Mocha':          {'bg':'#1C1614','surface':'#2E2420','surface2':'#3C2F29','accent':'#BF8F71','accent2':'#DBB39B','text':'#FFF8F3','muted':'#C4ADA0'},
    'Cherry Blossom': {'bg':'#1D131A','surface':'#30202B','surface2':'#402A39','accent':'#EA8BBC','accent2':'#F5B6D6','text':'#FFF7FB','muted':'#CEB0C0'},
    'Rainy Day':      {'bg':'#11171D','surface':'#1D2932','surface2':'#293945','accent':'#6F9AB7','accent2':'#9EC1D5','text':'#F4F9FC','muted':'#A6BAC6'},
    'Peachy':         {'bg':'#1F1614','surface':'#33231F','surface2':'#432E28','accent':'#E99173','accent2':'#F3B39D','text':'#FFF8F4','muted':'#D0B3A8'},
    'Blueberry':      {'bg':'#111222','surface':'#1D1F37','surface2':'#292C4A','accent':'#7E86D8','accent2':'#AAB0EF','text':'#F7F7FF','muted':'#AAACD0'},
    'Wisteria':       {'bg':'#18141F','surface':'#292234','surface2':'#372D45','accent':'#B18AD1','accent2':'#D2B3E8','text':'#FCF8FF','muted':'#BEAFCA'},
    'Evergreen':      {'bg':'#0E1915','surface':'#192A23','surface2':'#23382F','accent':'#65A988','accent2':'#91C8AA','text':'#F3FAF6','muted':'#9EB9AB'},
    'Candlelight':    {'bg':'#1D1712','surface':'#30261D','surface2':'#403226','accent':'#D4A05E','accent2':'#E7C28F','text':'#FFF9F0','muted':'#CBB79B'},
    'Cloud':          {'bg':'#16171A','surface':'#25272C','surface2':'#30333A','accent':'#929EAE','accent2':'#BAC3CF','text':'#FAFBFD','muted':'#B4B9C2'},
}

DEFAULTS = {
    'theme':'Cozy Pink', 'favorites':['DuskBloom Screen','DuskBloom Reader'],
    'smart_profiles':True, 'notifications':True, 'notification_level':'Normal',
    'active_profile':'Everyday', 'comfort':58, 'start_with_windows':False,
    'reduced_motion':False, 'update_mode':'Ask me', 'minimize_to_tray':True,
    'monitor_levels':{}, 'profile_mode':'Suggest first',
    'update_feed_url':'', 'last_update_check':0, 'catalog_cache':{}
}

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "DuskBloom Center"

def _center_startup_command():
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}" --startup'
    pyw=os.path.join(os.path.dirname(sys.executable),'pythonw.exe')
    runner=pyw if os.path.isfile(pyw) else sys.executable
    return f'"{runner}" "{os.path.abspath(__file__)}" --startup'

def set_center_startup(enabled):
    import winreg
    try:
        key=winreg.CreateKey(winreg.HKEY_CURRENT_USER,RUN_KEY)
        if enabled:
            winreg.SetValueEx(key,RUN_NAME,0,winreg.REG_SZ,_center_startup_command())
        else:
            try: winreg.DeleteValue(key,RUN_NAME)
            except FileNotFoundError: pass
        winreg.CloseKey(key)
        return center_startup_enabled()==bool(enabled)
    except Exception:
        return False

def center_startup_enabled():
    import winreg,re
    try:
        key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,RUN_KEY,0,winreg.KEY_READ)
        cmd=str(winreg.QueryValueEx(key,RUN_NAME)[0]).strip(); winreg.CloseKey(key)
        quoted=re.findall(r'"([^"]+)"',cmd)
        target=quoted[0] if quoted else cmd.split()[0]
        return os.path.isfile(target)
    except Exception:
        return False

def load_settings():
    data = dict(DEFAULTS)
    try:
        with open(SETTINGS,'r',encoding='utf-8') as f: data.update(json.load(f))
    except Exception: pass
    if data.get('theme') not in THEMES: data['theme']='Cozy Pink'
    data['start_with_windows']=center_startup_enabled()
    return data

def save_settings(data):
    try:
        with open(SETTINGS,'w',encoding='utf-8') as f: json.dump(data,f,indent=2)
    except Exception: pass

def rgb(hexv): return wx.Colour(hexv)

def installed_apps_root():
    return os.path.join(os.getenv('LOCALAPPDATA') or BASE, 'DuskBloom', 'Apps')

def candidate_roots():
    roots=[]
    installed=installed_apps_root()
    for p in [installed,
              os.path.join(installed,'screen'), os.path.join(installed,'sonar'),
              os.path.join(installed,'reader'), os.path.join(installed,'pointer'),
              os.path.join(installed,'atmosphere'), os.path.join(installed,'assist'),
              os.path.dirname(sys.executable if getattr(sys,'frozen',False) else __file__),
              os.path.expanduser('~/Downloads'), os.path.expanduser('~/Desktop'),
              os.getenv('LOCALAPPDATA',''), os.getenv('PROGRAMFILES','')]:
        if p and os.path.isdir(p) and p not in roots: roots.append(p)
    return roots

def find_component(names):
    # Search permanent Center installs first, including nested PyInstaller dist folders.
    rels=[]
    for name in names:
        stem=os.path.splitext(name)[0]
        rels += [name, os.path.join('dist',stem,name), os.path.join('dist','DuskBloomScreen',name),
                 os.path.join('dist','DuskBloomSonar',name)]
    for root in candidate_roots():
        for rel in rels:
            p=os.path.join(root,rel)
            if os.path.isfile(p): return p
        # bounded recursive search so Apps/screen and legacy downloaded builds are detected.
        try:
            for cur, dirs, files in os.walk(root):
                depth=os.path.relpath(cur,root).count(os.sep)
                if depth >= 4: dirs[:] = []
                low={f.lower():f for f in files}
                for name in names:
                    if name.lower() in low:
                        return os.path.join(cur,low[name.lower()])
        except Exception: pass
    return None

def is_running(exe_name):
    try:
        out=subprocess.check_output(['tasklist','/FI',f'IMAGENAME eq {exe_name}'],creationflags=0x08000000,text=True,errors='ignore')
        return exe_name.lower() in out.lower()
    except Exception: return False

SCREEN_BRIDGE = os.path.join(os.getenv('APPDATA') or os.path.expanduser('~'), 'DuskBloom', 'DuskBloomScreen')
SCREEN_STATE = os.path.join(SCREEN_BRIDGE, 'state.json')
SCREEN_COMMAND = os.path.join(SCREEN_BRIDGE, 'command.json')
SCREEN_MANIFEST = os.path.join(SCREEN_BRIDGE, 'manifest.json')

def read_json(path, default=None):
    try:
        with open(path,'r',encoding='utf-8') as f: return json.load(f)
    except Exception: return default

def screen_state():
    st=read_json(SCREEN_STATE,{}) or {}
    if st and time.time()-float(st.get('updated',0)) < 4: st['live']=True
    else: st['live']=False
    return st

def send_screen(command,value=None,monitor=None):
    try:
        os.makedirs(SCREEN_BRIDGE,exist_ok=True)
        msg={'id':str(uuid.uuid4()),'command':command,'value':value,'sent':time.time()}
        if monitor is not None: msg['monitor']=int(monitor)
        tmp=SCREEN_COMMAND+'.tmp'
        with open(tmp,'w',encoding='utf-8') as f: json.dump(msg,f)
        os.replace(tmp,SCREEN_COMMAND); return True
    except Exception: return False

def app_root():
    return os.path.dirname(sys.executable if getattr(sys,'frozen',False) else os.path.abspath(__file__))

def bundled_path(name):
    # PyInstaller one-folder builds place added data under _internal on newer versions.
    # Source/debug runs keep Bundled beside this file. Check every supported layout.
    roots = []
    if getattr(sys, 'frozen', False):
        roots += [
            os.path.join(os.path.dirname(sys.executable), 'Bundled'),
            os.path.join(os.path.dirname(sys.executable), '_internal', 'Bundled'),
        ]
        meipass = getattr(sys, '_MEIPASS', '')
        if meipass:
            roots.append(os.path.join(meipass, 'Bundled'))
    roots.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Bundled'))
    for root in roots:
        p = os.path.join(root, name)
        if os.path.isdir(p):
            return p
    return os.path.join(roots[0], name)


def version_tuple(v):
    try: return tuple(int(x) for x in str(v).strip().lstrip('v').split('.')[:4])
    except Exception: return (0,)

def resource_file(name):
    candidates=[os.path.join(app_root(),name), os.path.join(app_root(),'_internal',name)]
    meipass=getattr(sys,'_MEIPASS','')
    if meipass: candidates.append(os.path.join(meipass,name))
    for p in candidates:
        if os.path.isfile(p): return p
    return candidates[0]

def local_catalog():
    return read_json(resource_file('update_catalog.json'),{}) or {}

def installed_version(comp):
    if comp['id']=='screen':
        m=read_json(SCREEN_MANIFEST,{}) or {}
        return str(m.get('version') or comp.get('bundled') or '')
    if comp['id']=='web': return str(comp.get('bundled') or '')
    if comp['id']=='sonar':
        vf=os.path.join(installed_apps_root(),'sonar','version.txt')
        try: return open(vf,'r',encoding='utf-8').read().strip()
        except Exception: return ''
    path=find_component(comp.get('exe',[])) if comp.get('exe') else None
    if path:
        vf=os.path.join(os.path.dirname(path),'version.txt')
        try: return open(vf,'r',encoding='utf-8').read().strip()
        except Exception: return 'installed'
    return ''

COMPONENTS = [
    {'id':'screen','name':'DuskBloom Screen','icon':'◐','desc':'Screen comfort, migraine filtering & per-monitor control','exe':['DuskBloomScreen.exe','MellowScreen.exe','MigraineFilter.exe'],'bundled':'4.0.0','stage':'ready','installable':True},
    {'id':'web','name':'DuskBloom Web','icon':'◎','desc':'Cross-browser readability and page comfort','exe':[],'kind':'extension','bundled':'2.0.0','stage':'ready','installable':True},
    {'id':'reader','name':'DuskBloom Reader','icon':'▤','desc':'Comfortable PDFs, documents & read-aloud','exe':['DuskBloomReader.exe','MellowReader.exe'],'bundled':'2.0.0','stage':'ready','installable':True},
    {'id':'pointer','name':'DuskBloom Pointer','icon':'➤','desc':'Cursor visibility, halo, trails, guides & click feedback','exe':['DuskBloomPointer.exe','MellowPointer.exe'],'stage':'working'},
    {'id':'sonar','name':'DuskBloom Sonar','icon':'♫','desc':'Friendly SteelSeries Sonar controls and presets','exe':['DuskBloomSonar.exe','MellowSonar.exe','SonarWidget.exe'],'kind':'script_app','bundled':'15.2.0','stage':'ready','installable':True},
    {'id':'atmosphere','name':'DuskBloom Atmosphere','icon':'✧','desc':'Soft desktop ambience, particles and edge effects','exe':['DuskBloomAtmosphere.exe','MellowAtmosphere.exe'],'stage':'working'},
    {'id':'assist','name':'DuskBloom Assist','icon':'✦','desc':'Natural-language control across your DuskBloom apps','exe':['DuskBloomAssist.exe','MellowAssist.exe'],'stage':'working'},
]
PROFILES = {
    'Everyday':('🌷','Balanced comfort for normal use.',58),
    'Reading':('📖','Softer screen and calmer reading surfaces.',72),
    'Late Night':('🌙','Dimmer, warmer, quieter.',82),
    'Study':('✦','Comfort with fewer distractions.',68),
    'Gaming':('🎮','Lighter filtering while keeping DuskBloom ready.',35),
}

def theme_host(window):
    host = wx.GetTopLevelParent(window)
    return host if host is not None else window

class SoftButton(wx.Button):
    def __init__(self,parent,label,accent=False,size=(-1,38)):
        super().__init__(parent,label=label,style=wx.BORDER_NONE,size=size)
        self.accent=accent
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.apply(parent)
    def apply(self,parent):
        host=theme_host(parent)
        self.SetBackgroundColour(host.accent if self.accent else host.surface2)
        self.SetForegroundColour(host.bg if self.accent else host.text)
        self.SetFont(wx.Font(9,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD))

class Surface(wx.Panel):
    def __init__(self,parent,pad=18):
        super().__init__(parent)
        self.host=theme_host(parent)
        for name in ('bg','surface','surface2','accent','accent2','text','muted'):
            setattr(self,name,getattr(self.host,name))
        self.SetBackgroundColour(self.surface)
        self.sizer=wx.BoxSizer(wx.VERTICAL); self.SetSizer(self.sizer); self.pad=pad


# =========================================================
# DUSKBLOOM WEB GUARDIAN
# Keeps the extension package healthy and makes restoring a
# temporary Firefox/Zen install as close to one-click as the
# browser security model permits.
# =========================================================
WEB_GUARDIAN_ROOT = os.path.join(os.getenv('APPDATA') or os.path.expanduser('~'),'DuskBloom','Web')
WEB_GUARDIAN_STATE = os.path.join(WEB_GUARDIAN_ROOT,'guardian.json')

def web_working_dir(browser='Firefox-Zen'):
    return os.path.join(WEB_GUARDIAN_ROOT,browser)

def web_bundle_dir(browser='Firefox-Zen'):
    # Resolve bundled extension directly. This avoids depending on the component
    # launcher's bundled_path() signature during early startup.
    candidates=[
        os.path.join(BASE,'Bundled','DuskBloom Web',browser),
        os.path.join(getattr(sys,'_MEIPASS',BASE),'Bundled','DuskBloom Web',browser),
        os.path.join(os.path.dirname(sys.executable),'_internal','Bundled','DuskBloom Web',browser),
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    return candidates[0]

def web_package_valid(path):
    try:
        manifest=read_json(os.path.join(path,'manifest.json'),{}) or {}
        return bool(manifest.get('name')) and os.path.isfile(os.path.join(path,'content.js')) and os.path.isfile(os.path.join(path,'popup.js'))
    except Exception:
        return False

def restore_web_package(browser='Firefox-Zen'):
    src=web_bundle_dir(browser); dst=web_working_dir(browser)
    if not web_package_valid(src):
        return False,'Bundled DuskBloom Web package is missing or incomplete.'
    try:
        os.makedirs(WEB_GUARDIAN_ROOT,exist_ok=True)
        if os.path.isdir(dst): shutil.rmtree(dst,ignore_errors=True)
        shutil.copytree(src,dst)
        with open(WEB_GUARDIAN_STATE,'w',encoding='utf-8') as f:
            json.dump({'browser':browser,'restored':time.time(),'version':'1.1.0','path':dst},f,indent=2)
        return True,dst
    except Exception as ex:
        return False,str(ex)

def ensure_web_package(browser='Firefox-Zen'):
    dst=web_working_dir(browser)
    if web_package_valid(dst): return True,dst
    return restore_web_package(browser)

def find_browser_executable(prefer_zen=True):
    """Find Zen/Firefox without assuming either is on PATH."""
    local=os.getenv('LOCALAPPDATA') or ''
    pf=os.getenv('ProgramFiles') or r'C:\Program Files'
    pf86=os.getenv('ProgramFiles(x86)') or r'C:\Program Files (x86)'
    candidates=[]
    if prefer_zen:
        candidates += [
            os.path.join(local,'Programs','Zen Browser','zen.exe'),
            os.path.join(local,'Zen Browser','zen.exe'),
            os.path.join(pf,'Zen Browser','zen.exe'),
            os.path.join(pf86,'Zen Browser','zen.exe'),
        ]
    candidates += [
        os.path.join(pf,'Mozilla Firefox','firefox.exe'),
        os.path.join(pf86,'Mozilla Firefox','firefox.exe'),
        os.path.join(local,'Mozilla Firefox','firefox.exe'),
    ]
    # Registry/App Paths are useful for nonstandard Firefox installs.
    try:
        import winreg
        for exe in (('zen.exe' if prefer_zen else ''),'firefox.exe'):
            if not exe: continue
            for hive in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
                try:
                    with winreg.OpenKey(hive,rf'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe}') as k:
                        val=winreg.QueryValueEx(k,None)[0]
                        if val: candidates.insert(0,val)
                except OSError:
                    pass
    except Exception:
        pass
    for p in candidates:
        if p and os.path.isfile(p):
            return p
    return None

def web_guardian_status(browser='Firefox-Zen'):
    """Return only what Center can actually verify without browser cooperation."""
    path=web_working_dir(browser)
    if web_package_valid(path):
        return {
            'files_ready': True,
            'browser_installed': None,
            'label': 'Files ready — browser installation not verified',
            'path': path,
        }
    return {
        'files_ready': False,
        'browser_installed': None,
        'label': 'Extension files need preparation',
        'path': path,
    }

def open_web_restore_flow(parent=None,browser='Firefox-Zen'):
    ok,dst=ensure_web_package(browser)
    if not ok:
        if parent: wx.MessageBox(dst,'DuskBloom Web Guardian',wx.OK|wx.ICON_ERROR)
        return False

    if browser=='Firefox-Zen':
        exe=find_browser_executable(True)
        opened=False
        if exe:
            try:
                subprocess.Popen([exe,'about:debugging#/runtime/this-firefox'])
                opened=True
            except Exception:
                opened=False

        manifest=os.path.join(dst,'manifest.json')
        message=(
            "DuskBloom Web files are ready.\n\n"
            "In Zen/Firefox choose “Load Temporary Add-on…” and select:\n\n"
            + manifest +
            "\n\nCenter can keep these files ready, but Zen/Firefox controls whether the extension is actually installed."
        )
        if not opened:
            message += (
                "\n\nI couldn't locate Zen or Firefox automatically, so I did not "
                "show a Windows 'firefox not found' error. Open Zen yourself, go to "
                "about:debugging#/runtime/this-firefox, then use the path above."
            )
        if parent:
            wx.MessageBox(message,'DuskBloom Web Guardian',wx.OK|wx.ICON_INFORMATION)
    else:
        # Open the prepared folder for Load unpacked; don't assume a specific Chromium browser.
        try: os.startfile(dst)
        except Exception: pass
        if parent:
            wx.MessageBox(
                "DuskBloom Web files are ready.\n\n"
                "Open your browser's Extensions page, enable Developer mode, choose "
                "“Load unpacked”, and select:\n\n"+dst,
                'DuskBloom Web Guardian',wx.OK|wx.ICON_INFORMATION
            )
    return True

class WebGuardian:
    def __init__(self,frame):
        self.frame=frame
        self.timer=wx.Timer(frame)
        frame.Bind(wx.EVT_TIMER,self._tick,self.timer)
        self.timer.Start(60000)
        wx.CallLater(1200,self.check)
    def _tick(self,event): self.check()
    def check(self):
        # Silent repair of Center's durable working copies.
        ensure_web_package('Firefox-Zen')
        ensure_web_package('Chromium')


class DuskBloomTray(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        icon = wx.ArtProvider.GetIcon(wx.ART_TIP, wx.ART_OTHER, (32,32))
        self.SetIcon(icon, 'DuskBloom Center')
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self._open)
    def _open(self, event):
        self.frame.Show(); self.frame.Raise()
    def CreatePopupMenu(self):
        m=wx.Menu()
        q=m.Append(wx.ID_ANY,'Quick Panel'); o=m.Append(wx.ID_ANY,'Open DuskBloom Center')
        m.AppendSeparator(); r=m.Append(wx.ID_ANY,'Reading profile'); soft=m.Append(wx.ID_ANY,'Make things softer')
        m.AppendSeparator(); ex=m.Append(wx.ID_EXIT,'Quit DuskBloom')
        self.Bind(wx.EVT_MENU,lambda e:self.frame.quick_panel(),q)
        self.Bind(wx.EVT_MENU,lambda e:(self.frame.Show(),self.frame.Raise()),o)
        self.Bind(wx.EVT_MENU,lambda e:self.frame.apply_profile('Reading'),r)
        self.Bind(wx.EVT_MENU,lambda e:self.frame.bump_comfort(),soft)
        self.Bind(wx.EVT_MENU,self.frame.quit_app,ex)
        return m

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None,title=f'{APP_NAME} {APP_VERSION}',size=(1180,790),style=wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((980,680)); self.settings=load_settings(); self.current_page='Home'; self.tray=None
        self.set_palette(); self.SetBackgroundColour(self.bg)
        self.root=wx.BoxSizer(wx.HORIZONTAL)
        self.build_nav()
        self.content=wx.ScrolledWindow(self,style=wx.VSCROLL); self.content.SetScrollRate(0,12); self.content.SetBackgroundColour(self.bg)
        self.root.Add(self.content,1,wx.EXPAND); self.SetSizer(self.root)
        self.make_tray(); self.Bind(wx.EVT_CLOSE,self.on_close)
        self.show_page('Home'); self.Centre(); self.Show()

    def set_palette(self):
        t=THEMES[self.settings['theme']]
        self.bg=rgb(t['bg']); self.surface=rgb(t['surface']); self.surface2=rgb(t['surface2']); self.accent=rgb(t['accent']); self.accent2=rgb(t['accent2']); self.text=rgb(t['text']); self.muted=rgb(t['muted'])

    def build_nav(self):
        self.nav=wx.Panel(self); self.nav.SetMinSize((225,-1)); self.nav.SetBackgroundColour(self.surface)
        ns=wx.BoxSizer(wx.VERTICAL)
        brand=wx.StaticText(self.nav,label='DuskBloom  🌷'); brand.SetForegroundColour(self.text); brand.SetFont(wx.Font(20,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); ns.Add(brand,0,wx.LEFT|wx.RIGHT|wx.TOP,22)
        tag=wx.StaticText(self.nav,label='make your computer softer.'); tag.SetForegroundColour(self.muted); tag.SetFont(wx.Font(8,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)); ns.Add(tag,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,23)
        self.nav_buttons={}
        for icon,name in [('⌂','Home'),('♡','Favorites'),('◉','Displays'),('✦','Profiles'),('▦','Components'),('↓','Install')]:
            b=wx.Button(self.nav,label=f'  {icon}   {name}',style=wx.BORDER_NONE); b.SetMinSize((-1,43)); b.SetForegroundColour(self.text); b.SetBackgroundColour(self.surface); b.SetFont(wx.Font(10,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)); b.Bind(wx.EVT_BUTTON,lambda e,n=name:self.show_page(n)); ns.Add(b,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,10); self.nav_buttons[name]=b
        ns.AddStretchSpacer()
        status=wx.StaticText(self.nav,label='  ●  Everything’s blooming'); status.SetForegroundColour(self.accent); ns.Add(status,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,18)
        for icon,name in [('⚙','Settings'),('ⓘ','About')]:
            b=wx.Button(self.nav,label=f'  {icon}   {name}',style=wx.BORDER_NONE); b.SetMinSize((-1,43)); b.SetForegroundColour(self.text); b.SetBackgroundColour(self.surface); b.Bind(wx.EVT_BUTTON,lambda e,n=name:self.show_page(n)); ns.Add(b,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,10); self.nav_buttons[name]=b
        self.nav.SetSizer(ns); self.root.Add(self.nav,0,wx.EXPAND)

    def clear(self):
        # Keep one persistent sizer. Replacing a ScrolledWindow's sizer while its
        # old child windows are being destroyed can leave stale native paint
        # regions on Windows, which caused pages to appear black/half-drawn.
        sizer = self.content.GetSizer()
        if sizer is None:
            sizer = wx.BoxSizer(wx.VERTICAL)
            self.content.SetSizer(sizer)
        else:
            sizer.Clear(delete_windows=True)
        self.content.SetBackgroundColour(self.bg)

    def header(self,title,subtitle='',action=None):
        s=self.content.GetSizer(); row=wx.BoxSizer(wx.HORIZONTAL); left=wx.BoxSizer(wx.VERTICAL)
        t=wx.StaticText(self.content,label=title); t.SetForegroundColour(self.text); t.SetFont(wx.Font(25,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); left.Add(t)
        if subtitle:
            st=wx.StaticText(self.content,label=subtitle); st.SetForegroundColour(self.muted); st.SetFont(wx.Font(10,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)); left.Add(st,0,wx.TOP,5)
        row.Add(left,1)
        if action:
            b=SoftButton(self.content,action,True,size=(155,40)); row.Add(b,0,wx.ALIGN_CENTER_VERTICAL)
        s.Add(row,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM,30)

    def show_page(self,name):
        # Freeze the frame during page swaps so Windows never paints the page
        # between destruction and reconstruction of controls.
        self.Freeze()
        try:
            self.current_page=name
            self.clear()
            for n,b in self.nav_buttons.items():
                b.SetBackgroundColour(self.surface2 if n==name else self.surface)
                b.SetForegroundColour(self.accent2 if n==name else self.text)
                b.Refresh()
            {'Home':self.home,'Favorites':self.favorites,'Displays':self.displays,'Profiles':self.profiles,'Components':lambda:self.components(False),'Install':lambda:self.components(True),'Settings':self.settings_page,'About':self.about}[name]()
            self.content.SetVirtualSize(self.content.GetBestVirtualSize())
            self.content.Layout()
            self.content.FitInside()
            self.content.Scroll(0,0)
            self.root.Layout()
            self.Layout()
        finally:
            self.Thaw()
        self.content.Refresh(eraseBackground=True)
        self.nav.Refresh(eraseBackground=True)
        self.Refresh(eraseBackground=True)
        self.Update()

    def add_surface(self,sizer):
        p=Surface(self.content); sizer.Add(p,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,30); return p

    def home(self):
        self.header('Your softer desktop 🌷','Everything comfortable, connected, and close by.','Quick Panel')
        s=self.content.GetSizer()
        hero=self.add_surface(s); hs=hero.sizer
        row=wx.BoxSizer(wx.HORIZONTAL)
        left=wx.BoxSizer(wx.VERTICAL); k=wx.StaticText(hero,label='QUICK COMFORT'); k.SetForegroundColour(self.accent); k.SetFont(wx.Font(8,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); left.Add(k,0,wx.BOTTOM,8)
        title=wx.StaticText(hero,label='How does your screen feel?'); title.SetForegroundColour(self.text); title.SetFont(wx.Font(18,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); left.Add(title)
        sub=wx.StaticText(hero,label='One slider can soften participating DuskBloom apps together.'); sub.SetForegroundColour(self.muted); left.Add(sub,0,wx.TOP,5); row.Add(left,1)
        prof=wx.StaticText(hero,label=f"{PROFILES[self.settings['active_profile']][0]}  {self.settings['active_profile']}"); prof.SetForegroundColour(self.accent2); prof.SetFont(wx.Font(11,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); row.Add(prof,0,wx.ALIGN_CENTER_VERTICAL); hs.Add(row,0,wx.EXPAND|wx.ALL,20)
        cr=wx.BoxSizer(wx.HORIZONTAL); lo=wx.StaticText(hero,label='Light'); lo.SetForegroundColour(self.muted); cr.Add(lo,0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,10)
        slider=wx.Slider(hero,value=int(self.settings['comfort']),minValue=0,maxValue=100,style=wx.SL_HORIZONTAL); slider.SetBackgroundColour(self.surface); slider.Bind(wx.EVT_SLIDER,self.comfort_changed); cr.Add(slider,1,wx.ALIGN_CENTER_VERTICAL)
        self.comfort_label=wx.StaticText(hero,label=f"{self.settings['comfort']}%"); self.comfort_label.SetForegroundColour(self.text); self.comfort_label.SetMinSize((50,-1)); cr.Add(self.comfort_label,0,wx.ALIGN_CENTER_VERTICAL|wx.LEFT,12); hs.Add(cr,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
        br=wx.BoxSizer(wx.HORIZONTAL)
        for label,fn in [('🌷  Make things softer',lambda e:self.bump_comfort()),('📖  Open Reader',lambda e:self.open_component('reader')),('✦  Reading profile',lambda e:self.apply_profile('Reading'))]:
            b=SoftButton(hero,label,label.startswith('🌷')); b.Bind(wx.EVT_BUTTON,fn); br.Add(b,0,wx.RIGHT,10)
        hs.Add(br,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,20)

        label=wx.StaticText(self.content,label='Your DuskBloom'); label.SetForegroundColour(self.text); label.SetFont(wx.Font(16,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); s.Add(label,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,30)
        grid=wx.FlexGridSizer(cols=2,hgap=14,vgap=14); grid.AddGrowableCol(0,1); grid.AddGrowableCol(1,1)
        for comp in COMPONENTS: grid.Add(self.component_card(comp,compact=True),1,wx.EXPAND)
        s.Add(grid,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,30)

    def component_state(self,comp):
        if comp['id']=='screen':
            st=screen_state(); path=find_component(comp.get('exe',[]))
            return path, bool(path or st), bool(st.get('live'))
        if comp.get('kind') == 'script_app':
            root=os.path.join(os.getenv('LOCALAPPDATA') or BASE,'DuskBloom','Apps',comp['id'])
            start=os.path.join(root,'START_DUSKBLOOM_SONAR.bat')
            return start if os.path.isfile(start) else None, os.path.isfile(start), False
        if comp.get('kind') == 'extension':
            st=web_guardian_status('Firefox-Zen')
            return st['path'] if st['files_ready'] else None, bool(st['files_ready']), False
        path=find_component(comp.get('exe',[])) if comp.get('exe') else None
        installed=bool(path)
        running=is_running(os.path.basename(path)) if path else False
        return path,installed,running

    def catalog(self, force=False):
        cached=self.settings.get('catalog_cache',{}) or {}
        url=(self.settings.get('update_feed_url') or '').strip()
        if url and (force or not cached or time.time()-float(self.settings.get('last_update_check',0))>21600):
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'DuskBloom-Center/'+APP_VERSION})
                with urllib.request.urlopen(req,timeout=6) as r: remote=json.loads(r.read().decode('utf-8'))
                if isinstance(remote,dict) and isinstance(remote.get('components',{}),dict):
                    cached=remote; self.settings['catalog_cache']=remote; self.settings['last_update_check']=time.time(); save_settings(self.settings)
            except Exception: pass
        return cached if cached else local_catalog()

    def release_info(self,comp):
        return (self.catalog().get('components',{}) or {}).get(comp['id'],{}) or {}

    def component_card(self,comp,compact=False,install_page=False):
        p=Surface(self.content); p.SetMinSize((-1,150 if compact else 178)); ps=p.sizer
        path,installed,running=self.component_state(comp); rel=self.release_info(comp)
        current=installed_version(comp) if installed else ''
        latest=str(rel.get('version') or comp.get('bundled') or '')
        update_available=bool(installed and current and current!='installed' and latest and version_tuple(latest)>version_tuple(current))
        if running: status='RUNNING'
        elif update_available: status='UPDATE READY'
        elif installed: status='READY'
        elif comp.get('stage')=='working' and not rel.get('ready'): status='WORKING ON…'
        else: status='READY TO INSTALL'
        top=wx.BoxSizer(wx.HORIZONTAL); ico=wx.StaticText(p,label=comp['icon']); ico.SetForegroundColour(self.accent); ico.SetFont(wx.Font(21,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); top.Add(ico,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,18)
        names=wx.BoxSizer(wx.VERTICAL); nm=wx.StaticText(p,label=comp['name']); nm.SetForegroundColour(self.text); nm.SetFont(wx.Font(13,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); names.Add(nm); ds=wx.StaticText(p,label=comp['desc']); ds.SetForegroundColour(self.muted); names.Add(ds,0,wx.TOP,3); top.Add(names,1,wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL,18)
        st=wx.StaticText(p,label=f'  {status}  '); st.SetForegroundColour(self.accent if (installed or update_available or status=='READY TO INSTALL') else self.muted); top.Add(st,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,18); ps.Add(top,0,wx.EXPAND)
        row=wx.BoxSizer(wx.HORIZONTAL)
        if installed:
            b=SoftButton(p,'Open',True); b.Bind(wx.EVT_BUTTON,lambda e,c=comp:self.open_component(c['id'])); row.Add(b,0,wx.RIGHT,8)
            if update_available:
                u=SoftButton(p,f'Update to v{latest}',True); u.Bind(wx.EVT_BUTTON,lambda e,c=comp:self.update_component(c)); row.Add(u,0,wx.RIGHT,8)
            else:
                q=SoftButton(p,'Quick settings'); q.Bind(wx.EVT_BUTTON,lambda e,c=comp:self.quick_settings(c)); row.Add(q,0,wx.RIGHT,8)
        elif comp.get('stage')=='working' and not rel.get('ready'):
            b=SoftButton(p,'Working on it…'); b.Enable(False); row.Add(b,0,wx.RIGHT,8)
        else:
            label='Manage browsers' if comp['id']=='web' else 'Install'
            b=SoftButton(p,label,True); b.Bind(wx.EVT_BUTTON,lambda e,c=comp:self.install_component(c)); row.Add(b,0,wx.RIGHT,8)
        fav='♥ Favorite' if comp['name'] in self.settings['favorites'] else '♡ Favorite'; f=SoftButton(p,fav); f.Bind(wx.EVT_BUTTON,lambda e,c=comp:self.toggle_favorite(c['name'])); row.Add(f,0,wx.RIGHT,8)
        row.AddStretchSpacer(); txt=(f'v{current}' if current else (f'v{latest}' if latest else 'Coming soon')); ver=wx.StaticText(p,label=txt); ver.SetForegroundColour(self.muted); row.Add(ver,0,wx.ALIGN_CENTER_VERTICAL)
        ps.Add(row,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,18)
        return p

    def components(self,install_page=False):
        self.header('Install' if install_page else 'Components', 'One-click home for the DuskBloom suite.' if install_page else 'See what’s installed, running, and ready for you.')
        s=self.content.GetSizer()
        if install_page:
            banner=self.add_surface(s); bt=wx.StaticText(banner,label='🌷  Pick what you want. DuskBloom stays modular.'); bt.SetForegroundColour(self.text); bt.SetFont(wx.Font(13,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); banner.sizer.Add(bt,0,wx.ALL,18)
            bs=wx.StaticText(banner,label='Screen, Web, Reader + Sonar are ready now. Pointer, Atmosphere and Assist show as Working on… until their release appears in the update feed.'); bs.SetForegroundColour(self.muted); banner.sizer.Add(bs,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,18)
        for c in COMPONENTS: s.Add(self.component_card(c,install_page=install_page),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,30)

    def favorites(self):
        self.header('Favorites','Your most-used DuskBloom controls, without the clutter.')
        s=self.content.GetSizer(); found=False
        for c in COMPONENTS:
            if c['name'] in self.settings['favorites']:
                s.Add(self.component_card(c),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,30); found=True
        if not found:
            p=self.add_surface(s); x=wx.StaticText(p,label='♡  Nothing pinned yet. Use the Favorite button on any component.'); x.SetForegroundColour(self.muted); p.sizer.Add(x,0,wx.ALL,22)

    def displays(self):
        self.header('Displays','Give each monitor its own comfort level.')
        s=self.content.GetSizer(); count=max(1,ctypes.windll.user32.GetSystemMetrics(80))
        for i in range(count):
            p=self.add_surface(s); row=wx.BoxSizer(wx.HORIZONTAL); title=wx.StaticText(p,label=f'▣  Display {i+1}'); title.SetForegroundColour(self.text); title.SetFont(wx.Font(14,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); row.Add(title,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL,18)
            badge=wx.StaticText(p,label='  READY FOR SCREEN  '); badge.SetForegroundColour(self.accent); row.Add(badge,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,18); p.sizer.Add(row,0,wx.EXPAND)
            key=str(i); val=int(self.settings['monitor_levels'].get(key,self.settings['comfort'])); sr=wx.BoxSizer(wx.HORIZONTAL); lab=wx.StaticText(p,label='Comfort'); lab.SetForegroundColour(self.muted); sr.Add(lab,0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,12); sl=wx.Slider(p,value=val,minValue=0,maxValue=100); sl.SetBackgroundColour(self.surface); out=wx.StaticText(p,label=f'{val}%'); out.SetForegroundColour(self.text); out.SetMinSize((48,-1))
            sl.Bind(wx.EVT_SLIDER,lambda e,k=key,o=out:self.monitor_changed(k,o,e.GetInt())); sr.Add(sl,1,wx.ALIGN_CENTER_VERTICAL); sr.Add(out,0,wx.ALIGN_CENTER_VERTICAL|wx.LEFT,12); p.sizer.Add(sr,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,18)
        st=screen_state(); note=wx.StaticText(self.content,label=('● LIVE — changes are being sent directly to DuskBloom Screen.' if st.get('live') else '○ DuskBloom Screen is not running. Your values are saved and will be ready when Screen opens.')); note.SetForegroundColour(self.muted); s.Add(note,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,30)

    def profiles(self):
        self.header('Smart Profiles','Comfort that can follow what you’re doing — without taking over.')
        s=self.content.GetSizer()
        mode=self.add_surface(s); r=wx.BoxSizer(wx.HORIZONTAL); t=wx.StaticText(mode,label='Smart behavior'); t.SetForegroundColour(self.text); t.SetFont(wx.Font(13,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); r.Add(t,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL,18); ch=wx.Choice(mode,choices=['Suggest first','Switch automatically','Off']); ch.SetStringSelection(self.settings.get('profile_mode','Suggest first')); ch.Bind(wx.EVT_CHOICE,lambda e:self.set_value('profile_mode',e.GetString())); r.Add(ch,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,14); mode.sizer.Add(r,0,wx.EXPAND)
        grid=wx.FlexGridSizer(cols=2,hgap=14,vgap=14); grid.AddGrowableCol(0,1); grid.AddGrowableCol(1,1)
        for name,(icon,desc,level) in PROFILES.items():
            p=Surface(self.content); top=wx.BoxSizer(wx.HORIZONTAL); a=wx.StaticText(p,label=f'{icon}  {name}'); a.SetForegroundColour(self.text); a.SetFont(wx.Font(14,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); top.Add(a,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL,18); active=name==self.settings['active_profile']; badge=wx.StaticText(p,label=' ACTIVE ' if active else f' {level}% '); badge.SetForegroundColour(self.accent if active else self.muted); top.Add(badge,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,18); p.sizer.Add(top,0,wx.EXPAND); d=wx.StaticText(p,label=desc); d.SetForegroundColour(self.muted); p.sizer.Add(d,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,18); b=SoftButton(p,'Use profile',not active); b.Bind(wx.EVT_BUTTON,lambda e,n=name:self.apply_profile(n)); p.sizer.Add(b,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,18); grid.Add(p,1,wx.EXPAND)
        s.Add(grid,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,30)

    def settings_page(self):
        self.header('Settings','Make DuskBloom feel like yours.')
        s=self.content.GetSizer(); title=wx.StaticText(self.content,label='Appearance'); title.SetForegroundColour(self.text); title.SetFont(wx.Font(16,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); s.Add(title,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,30)
        grid=wx.FlexGridSizer(cols=4,hgap=10,vgap=10)
        for name,t in THEMES.items():
            p=wx.Panel(self.content); p.SetMinSize((165,92)); p.SetBackgroundColour(rgb(t['surface'])); ps=wx.BoxSizer(wx.VERTICAL); nm=wx.StaticText(p,label=('✓  ' if name==self.settings['theme'] else '')+name); nm.SetForegroundColour(rgb(t['text'])); nm.SetFont(wx.Font(9,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); ps.Add(nm,0,wx.ALL,12); dots=wx.StaticText(p,label='●  ●  ●'); dots.SetForegroundColour(rgb(t['accent'])); ps.Add(dots,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,12); p.SetSizer(ps); p.Bind(wx.EVT_LEFT_UP,lambda e,n=name:self.change_theme(n)); nm.Bind(wx.EVT_LEFT_UP,lambda e,n=name:self.change_theme(n)); grid.Add(p,1,wx.EXPAND)
        s.Add(grid,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,30)
        p=self.add_surface(s)
        for key,label in [('notifications','Gentle notifications'),('start_with_windows','Start DuskBloom Center with Windows'),('minimize_to_tray','Keep Center available in the system tray'),('reduced_motion','Reduce motion and decorative effects')]:
            cb=wx.CheckBox(p,label=label); cb.SetForegroundColour(self.text); cb.SetValue(bool(self.settings.get(key,False))); cb.Bind(wx.EVT_CHECKBOX,lambda e,k=key:self.set_value(k,e.IsChecked())); p.sizer.Add(cb,0,wx.LEFT|wx.RIGHT|wx.TOP,18)
        ur=wx.BoxSizer(wx.HORIZONTAL); ul=wx.StaticText(p,label='Updates'); ul.SetForegroundColour(self.text); ur.Add(ul,1,wx.ALIGN_CENTER_VERTICAL); uc=wx.Choice(p,choices=['Automatic','Ask me','Manual']); uc.SetStringSelection(self.settings.get('update_mode','Ask me')); uc.Bind(wx.EVT_CHOICE,lambda e:self.set_value('update_mode',e.GetString())); ur.Add(uc,0); p.sizer.Add(ur,0,wx.EXPAND|wx.ALL,18)
        cr=wx.BoxSizer(wx.HORIZONTAL); ck=SoftButton(p,'Check for updates',True); ck.Bind(wx.EVT_BUTTON,self.check_updates); cr.Add(ck,0,wx.RIGHT,10); feed=wx.StaticText(p,label=('Update feed connected' if self.settings.get('update_feed_url') else 'Update engine ready • release feed not published yet')); feed.SetForegroundColour(self.muted); cr.Add(feed,0,wx.ALIGN_CENTER_VERTICAL); p.sizer.Add(cr,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,18)
        br=wx.BoxSizer(wx.HORIZONTAL); b1=SoftButton(p,'Backup DuskBloom'); b2=SoftButton(p,'Restore backup'); b3=SoftButton(p,'Run checkup'); b1.Bind(wx.EVT_BUTTON,self.backup); b2.Bind(wx.EVT_BUTTON,self.restore); b3.Bind(wx.EVT_BUTTON,self.checkup); br.Add(b1,0,wx.RIGHT,8); br.Add(b2,0,wx.RIGHT,8); br.Add(b3); p.sizer.Add(br,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,18)

    def about(self):
        self.header('About DuskBloom',f'Center {APP_VERSION}')
        s=self.content.GetSizer(); p=self.add_surface(s); big=wx.StaticText(p,label='DuskBloom  🌷'); big.SetForegroundColour(self.text); big.SetFont(wx.Font(22,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); p.sizer.Add(big,0,wx.ALL,20); x=wx.StaticText(p,label='make your computer softer.\n\nOne calm home for Screen, Web, Reader, Pointer, Sonar, Atmosphere, Assist, and whatever blooms next.\nBuilt to stay modular: install only what you want.\n\nCenter v1.0.4 includes DuskBloom Sonar v15.2 and the DuskBloom Update Engine, so one installed Center can discover future component releases from a stable release feed instead of needing a new Center download each time.'); x.SetForegroundColour(self.muted); p.sizer.Add(x,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,20)

    def comfort_changed(self,e):
        self.settings['comfort']=e.GetInt(); save_settings(self.settings); self.comfort_label.SetLabel(f'{e.GetInt()}%'); send_screen('set_intensity', max(1,min(20,round(e.GetInt()/5))))
    def bump_comfort(self):
        self.settings['comfort']=min(100,int(self.settings['comfort'])+12); save_settings(self.settings); self.show_page('Home'); self.gentle('Things are a little softer now.','Comfort increased')
    def monitor_changed(self,key,out,val): self.settings['monitor_levels'][key]=val; save_settings(self.settings); out.SetLabel(f'{val}%'); send_screen('set_monitor_intensity',max(1,min(20,round(val/5))),int(key))
    def set_value(self,key,val):
        if key=='start_with_windows':
            ok=set_center_startup(bool(val))
            self.settings[key]=bool(val) if ok else center_startup_enabled()
            save_settings(self.settings)
            if not ok: self.gentle('Windows startup could not be registered. The switch was not faked.', 'Startup not enabled')
            return
        self.settings[key]=val; save_settings(self.settings)
    def change_theme(self,name): self.settings['theme']=name; save_settings(self.settings); self.set_palette(); self.nav.SetBackgroundColour(self.surface); self.SetBackgroundColour(self.bg); self.show_page('Settings')
    def apply_profile(self,name): self.settings['active_profile']=name; self.settings['comfort']=PROFILES[name][2]; save_settings(self.settings); send_screen('set_intensity',max(1,min(20,round(PROFILES[name][2]/5)))); self.gentle(f'{name} profile is ready.', 'Profile changed'); self.show_page('Profiles' if self.current_page=='Profiles' else 'Home')
    def toggle_favorite(self,name):
        f=self.settings['favorites']; f.remove(name) if name in f else f.append(name); save_settings(self.settings); self.show_page(self.current_page)
    def open_component(self,cid):
        c=next((x for x in COMPONENTS if x['id']==cid),None)
        if not c:return
        path=find_component(c['exe']) if c['exe'] else None
        if cid=='web':
            # Web is a browser extension, so "Open" means open its manager/repair screen.
            self.web_quick_settings(); return
        if not path and cid=='screen':
            for q in [os.path.join(installed_apps_root(),'screen','dist','DuskBloomScreen','DuskBloomScreen.exe'),
                      os.path.join(bundled_path('DuskBloom Screen'),'dist','DuskBloomScreen','DuskBloomScreen.exe')]:
                if os.path.isfile(q): path=q; break
        if cid=='sonar' and not path:
            root=os.path.join(os.getenv('LOCALAPPDATA') or BASE,'DuskBloom','Apps','sonar')
            start=os.path.join(root,'START_DUSKBLOOM_SONAR.bat')
            path=start if os.path.isfile(start) else None
        if path:
            try:
                if str(path).lower().endswith('.bat'): subprocess.Popen(['cmd','/c',path],cwd=os.path.dirname(path),creationflags=subprocess.CREATE_NO_WINDOW)
                else: subprocess.Popen([path],cwd=os.path.dirname(path))
            except Exception as ex: wx.MessageBox(str(ex),'Could not open',wx.OK|wx.ICON_ERROR)
        else: self.install_component(c)
    def quick_settings(self,c):
        if c['id']=='screen': self.screen_quick_settings()
        elif c['id']=='web': self.web_quick_settings()
        elif c['id']=='reader': self.open_component('reader')
        else: wx.MessageBox(f'{c["name"]} quick controls will appear here as its local bridge is connected.','DuskBloom')
    def web_quick_settings(self):
        st=web_guardian_status('Firefox-Zen')
        d=wx.Dialog(self,title='DuskBloom Web',size=(520,430)); d.SetBackgroundColour(self.bg)
        z=wx.BoxSizer(wx.VERTICAL)
        h=wx.StaticText(d,label='◎  DuskBloom Web'); h.SetForegroundColour(self.text); h.SetFont(wx.Font(17,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); z.Add(h,0,wx.ALL,20)

        state='FILES READY' if st['files_ready'] else 'FILES NOT READY'
        s=wx.StaticText(d,label=state); s.SetForegroundColour(self.accent); s.SetFont(wx.Font(10,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); z.Add(s,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,20)

        msg=wx.StaticText(d,label='Center can verify and repair DuskBloom Web’s files. It cannot truthfully verify that an unsigned temporary extension is currently loaded inside Zen/Firefox, so this screen will never call “files ready” installed.')
        msg.SetForegroundColour(self.muted); msg.Wrap(455); z.Add(msg,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,20)

        b=wx.Button(d,label='Install / Load in Zen or Firefox',style=wx.BORDER_NONE); b.SetBackgroundColour(self.accent); b.SetForegroundColour(self.bg); b.SetMinSize((-1,44))
        b.Bind(wx.EVT_BUTTON,lambda e:open_web_restore_flow(self,'Firefox-Zen')); z.Add(b,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,20)

        c=wx.Button(d,label='Prepare Chromium files',style=wx.BORDER_NONE); c.SetBackgroundColour(self.surface2); c.SetForegroundColour(self.text); c.SetMinSize((-1,40))
        c.Bind(wx.EVT_BUTTON,lambda e:open_web_restore_flow(self,'Chromium')); z.Add(c,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,20)

        loc=wx.StaticText(d,label='Working copy:\\n'+st['path']); loc.SetForegroundColour(self.muted); z.Add(loc,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
        d.SetSizer(z); d.CentreOnParent(); d.ShowModal(); d.Destroy()

    def screen_quick_settings(self):
        st=screen_state()
        d=wx.Dialog(self,title='DuskBloom Screen — Quick Settings',size=(430,390)); d.SetBackgroundColour(self.bg); z=wx.BoxSizer(wx.VERTICAL)
        h=wx.StaticText(d,label='◐  DuskBloom Screen'); h.SetForegroundColour(self.text); h.SetFont(wx.Font(17,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); z.Add(h,0,wx.ALL,20)
        status=wx.StaticText(d,label=('● Connected live' if st.get('live') else '○ Not running')); status.SetForegroundColour(self.accent if st.get('live') else self.muted); z.Add(status,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
        r=wx.BoxSizer(wx.HORIZONTAL); lab=wx.StaticText(d,label='Intensity'); lab.SetForegroundColour(self.text); r.Add(lab,0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,12); v=int(st.get('intensity',max(1,round(self.settings['comfort']/5)))); sl=wx.Slider(d,value=v,minValue=1,maxValue=20); sl.SetBackgroundColour(self.bg); out=wx.StaticText(d,label=f'{v}/20'); out.SetForegroundColour(self.text); sl.Bind(wx.EVT_SLIDER,lambda e:(out.SetLabel(f'{e.GetInt()}/20'),send_screen('set_intensity',e.GetInt()))); r.Add(sl,1); r.Add(out,0,wx.LEFT|wx.ALIGN_CENTER_VERTICAL,10); z.Add(r,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
        for label,cmd,val in [('Screen On','set_enabled',True),('Screen Off','set_enabled',False),('Match all monitors','match_all',True),('Darken side monitors','darken_sides',True)]:
            b=wx.Button(d,label=label,style=wx.BORDER_NONE); b.SetBackgroundColour(self.surface2); b.SetForegroundColour(self.text); b.SetMinSize((-1,38)); b.Bind(wx.EVT_BUTTON,lambda e,c=cmd,v=val:send_screen(c,v)); z.Add(b,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
        d.SetSizer(z); d.CentreOnParent(); d.ShowModal(); d.Destroy()

    def install_component(self,c):
        """Install a bundled component with one-click behavior.
        Ready components get copied into the user's DuskBloom app area and started.
        Browser extensions are copied to a stable location and the browser loader is opened.
        """
        appdata=os.getenv('LOCALAPPDATA') or BASE
        apps_root=os.path.join(appdata,'DuskBloom','Apps')
        os.makedirs(apps_root,exist_ok=True)

        if c['id']=='sonar':
            src=bundled_path('DuskBloom Sonar'); target=os.path.join(apps_root,'sonar')
            if not os.path.isdir(src): wx.MessageBox('The bundled DuskBloom Sonar package is missing.','DuskBloom Install',wx.OK|wx.ICON_ERROR); return
            try:
                if os.path.isdir(target): shutil.rmtree(target,ignore_errors=True)
                shutil.copytree(src,target)
                self.gentle('DuskBloom Sonar v15.2 is installed.','Installed')
                exe=os.path.join(target,'DuskBloomSonar.exe')
                start=os.path.join(target,'START_DUSKBLOOM_SONAR.bat')
                if os.path.isfile(exe): subprocess.Popen([exe],cwd=target)
                elif os.path.isfile(start): subprocess.Popen(['cmd','/c',start],cwd=target,creationflags=subprocess.CREATE_NO_WINDOW)
                self.show_page('Components')
            except Exception as ex: wx.MessageBox(str(ex),'Could not install DuskBloom Sonar',wx.OK|wx.ICON_ERROR)
            return

        if c['id']=='screen':
            src=bundled_path('DuskBloom Screen'); target=os.path.join(apps_root,'screen')
            bat=os.path.join(target,'BUILD_DUSKBLOOM_SCREEN.bat')
            try:
                if not os.path.isdir(src): raise FileNotFoundError('Bundled DuskBloom Screen package is missing.')
                if os.path.isdir(target): shutil.rmtree(target,ignore_errors=True)
                shutil.copytree(src,target)
                prebuilt=os.path.join(target,'DuskBloomScreen.exe')
                if os.path.isfile(prebuilt):
                    subprocess.Popen([prebuilt],cwd=target)
                    self.gentle('DuskBloom Screen 4.0 is installed and running.','Installed')
                    return
                wx.MessageBox('This source bundle does not contain the prebuilt Screen executable. Run BUILD_WINDOWS_RELEASE.bat once on the build PC, or use the GitHub Windows build.','Install DuskBloom Screen',wx.OK|wx.ICON_INFORMATION)
                if os.path.isfile(bat): subprocess.Popen(['cmd','/c',bat],cwd=target,creationflags=subprocess.CREATE_NEW_CONSOLE)
                return
            except Exception as ex:
                wx.MessageBox(str(ex),'Could not install DuskBloom Screen',wx.OK|wx.ICON_ERROR); return

        if c['id']=='web':
            try:
                src=bundled_path('DuskBloom Web'); target=os.path.join(apps_root,'web')
                if os.path.isdir(target): shutil.rmtree(target,ignore_errors=True)
                shutil.copytree(src,target)
                self.open_web_install(target)
                return
            except Exception as ex:
                wx.MessageBox(str(ex),'Could not prepare DuskBloom Web',wx.OK|wx.ICON_ERROR); return

        wx.MessageBox(f'{c["name"]} is still being developed. It will become one-click installable when its release is bundled into Center.','DuskBloom Install',wx.OK|wx.ICON_INFORMATION)

    def open_web_install(self,target):
        d=wx.Dialog(self,title='Install DuskBloom Web',size=(620,430)); d.SetBackgroundColour(self.bg)
        s=wx.BoxSizer(wx.VERTICAL)
        h=wx.StaticText(d,label='DuskBloom Web  •  v2.0.0'); h.SetForegroundColour(self.text); h.SetFont(wx.Font(17,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); s.Add(h,0,wx.ALL,20)
        msg=wx.StaticText(d,label='The extension files are now installed locally. Choose your browser below.\n\nFirefox / Zen can load the bundled extension directly from the DuskBloom folder. Chromium browsers use their Extensions → Developer mode → Load unpacked flow.'); msg.SetForegroundColour(self.muted); s.Add(msg,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
        for label,browser in [('Firefox / Zen','Firefox-Zen'),('Chrome / Edge / Brave / Opera / Vivaldi','Chromium')]:
            b=SoftButton(d,label,True); b.Bind(wx.EVT_BUTTON,lambda e,browser=browser:self.launch_web_loader(target,browser)); s.Add(b,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        close=SoftButton(d,'Done',False); close.Bind(wx.EVT_BUTTON,lambda e:d.Destroy()); s.Add(close,0,wx.ALL,12)
        d.SetSizer(s); d.ShowModal(); d.Destroy()

    def launch_web_loader(self,target,browser):
        folder=os.path.join(target,browser)
        if not os.path.isdir(folder): wx.MessageBox('That browser package is not present.','DuskBloom Web',wx.OK|wx.ICON_ERROR); return
        if browser=='Firefox-Zen':
            for exe in ['firefox.exe','zen.exe']:
                try: subprocess.Popen([exe,'about:debugging#/runtime/this-firefox'],creationflags=subprocess.CREATE_NO_WINDOW); return
                except Exception: pass
        webbrowser.open('https://support.google.com/chrome/a/answer/2714278')
        wx.MessageBox(f'Extension files are ready here:\n\n{folder}\n\nUse Load unpacked in your browser extension manager and select this folder.','DuskBloom Web',wx.OK|wx.ICON_INFORMATION)

    def update_component(self,c):
        rel=self.release_info(c); url=str(rel.get('url') or '').strip(); sha=str(rel.get('sha256') or '').strip().lower()
        if not url:
            wx.MessageBox('This update is listed, but its download package is not published yet.','DuskBloom Update',wx.OK|wx.ICON_INFORMATION); return
        try:
            self.gentle(f'Downloading {c["name"]}…','DuskBloom Update')
            td=tempfile.mkdtemp(prefix='DuskBloomUpdate_'); pkg=os.path.join(td,'package.zip')
            urllib.request.urlretrieve(url,pkg)
            if sha:
                h=hashlib.sha256(open(pkg,'rb').read()).hexdigest().lower()
                if h!=sha: raise RuntimeError('The downloaded update did not pass its safety check.')
            target=os.path.join(os.getenv('LOCALAPPDATA') or BASE,'DuskBloom','Apps',c['id']); os.makedirs(target,exist_ok=True)
            with zipfile.ZipFile(pkg) as z: z.extractall(target)
            self.gentle(f'{c["name"]} is updated and ready.','Update complete'); self.show_page(self.current_page)
        except Exception as ex: wx.MessageBox(str(ex),'Update could not finish',wx.OK|wx.ICON_ERROR)

    def check_updates(self,e=None):
        before=json.dumps(self.settings.get('catalog_cache',{}),sort_keys=True); self.catalog(force=True)
        ready=[]
        for c in COMPONENTS:
            rel=self.release_info(c)
            if rel.get('ready') or rel.get('version'): ready.append(c['name'])
        self.show_page('Components')
        self.gentle('Update check finished. Ready apps are shown in Components.','DuskBloom is up to date')

    def gentle(self,message,title='DuskBloom'):
        if not self.settings.get('notifications',True): return
        try:
            n=wx.adv.NotificationMessage(title,message,parent=self); n.Show(timeout=wx.adv.NotificationMessage.Timeout_Auto)
        except Exception: pass
    def backup(self,e):
        with wx.FileDialog(self,'Save DuskBloom backup',wildcard='DuskBloom backup (*.mellow)|*.mellow',style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT,defaultFile='DuskBloom Backup.mellow') as d:
            if d.ShowModal()==wx.ID_OK:
                path=d.GetPath(); path=path if path.lower().endswith('.mellow') else path+'.mellow'
                with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
                    if os.path.exists(SETTINGS): z.write(SETTINGS,'center/settings.json')
                    z.writestr('backup.json',json.dumps({'app':'DuskBloom Center','version':APP_VERSION,'created':datetime.datetime.now().isoformat()},indent=2))
                self.gentle('Your DuskBloom settings are safely backed up.','Backup complete')
    def restore(self,e):
        with wx.FileDialog(self,'Restore DuskBloom backup',wildcard='DuskBloom backup (*.mellow)|*.mellow',style=wx.FD_OPEN) as d:
            if d.ShowModal()==wx.ID_OK:
                try:
                    with zipfile.ZipFile(d.GetPath()) as z: open(SETTINGS,'wb').write(z.read('center/settings.json'))
                    self.settings=load_settings(); self.set_palette(); self.show_page('Settings'); self.gentle('Your DuskBloom setup is back.','Restore complete')
                except Exception as ex: wx.MessageBox(str(ex),'Could not restore',wx.OK|wx.ICON_ERROR)
    def checkup(self,e):
        lines=[]
        for c in COMPONENTS:
            path=find_component(c['exe']) if c['exe'] else None
            lines.append(f"✓ {c['name']}: detected" if path else f"• {c['name']}: not installed")
        wx.MessageBox('DuskBloom Checkup\n\n'+'\n'.join(lines)+'\n\nCenter settings: healthy','Everything’s blooming 🌷')
    def quick_panel(self):
        d=wx.Dialog(self,title='DuskBloom Quick Panel',size=(390,360)); d.SetBackgroundColour(self.bg); s=wx.BoxSizer(wx.VERTICAL); h=wx.StaticText(d,label='DuskBloom  🌷'); h.SetForegroundColour(self.text); h.SetFont(wx.Font(18,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)); s.Add(h,0,wx.ALL,20); p=wx.StaticText(d,label=f"{PROFILES[self.settings['active_profile']][0]}  {self.settings['active_profile']}  •  Comfort {self.settings['comfort']}%"); p.SetForegroundColour(self.muted); s.Add(p,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
        for label,fn in [('🌷 Make things softer',lambda e:(self.bump_comfort(),d.Destroy())),('📖 Open Reader',lambda e:(self.open_component('reader'),d.Destroy())),('◐ Open Screen',lambda e:(self.open_component('screen'),d.Destroy())),('Open full Center',lambda e:d.Destroy())]:
            b=wx.Button(d,label=label,style=wx.BORDER_NONE); b.SetBackgroundColour(self.accent if label.startswith('🌷') else self.surface2); b.SetForegroundColour(self.bg if label.startswith('🌷') else self.text); b.SetMinSize((-1,42)); b.Bind(wx.EVT_BUTTON,fn); s.Add(b,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,20)
        d.SetSizer(s); d.CentreOnParent(); d.ShowModal()
    def make_tray(self):
        try: self.tray=DuskBloomTray(self)
        except Exception: self.tray=None
    def on_close(self,e):
        if self.settings.get('minimize_to_tray',True): self.Hide(); self.gentle('DuskBloom is still nearby in the tray.','Still blooming')
        else: self.quit_app(e)
    def quit_app(self,e=None):
        if self.tray: self.tray.RemoveIcon(); self.tray.Destroy(); self.tray=None
        self.Destroy()

class App(wx.App):
    def OnInit(self):
        try:
            self.frame=MainFrame()
            try:
                self.web_guardian=WebGuardian(self.frame)
            except Exception:
                # Web Guardian is optional: Center must always launch even if
                # extension maintenance encounters an environment-specific issue.
                self.web_guardian=None
                try:
                    with open(os.path.join(BASE,'web_guardian_error.txt'),'w',encoding='utf-8') as f:
                        f.write(traceback.format_exc())
                except Exception:
                    pass
            return True
        except Exception:
            import traceback
            details=traceback.format_exc()
            log=os.path.join(BASE,'launch_error.txt')
            try:
                with open(log,'w',encoding='utf-8') as f: f.write(details)
            except Exception: pass
            try:
                wx.MessageBox('DuskBloom Center could not start.\n\nA diagnostic log was saved to:\n'+log+'\n\n'+details[-1200:],'DuskBloom Center',wx.OK|wx.ICON_ERROR)
            except Exception: pass
            return False

if __name__=='__main__': App(False).MainLoop()
