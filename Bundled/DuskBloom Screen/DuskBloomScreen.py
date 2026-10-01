
"""
Migraine Filter for Windows
Install: pip install wxPython pystray pillow
Run: python MigraineFilter_Windows.py
"""

import sys, os, json, ctypes, ctypes.wintypes, threading, time, shutil, re
import wx, pystray
from PIL import Image, ImageDraw
import winreg

# ── Admin ──────────────────────────────────────────────────────────────────────
# Preserve the original admin behavior, but relaunch a packaged EXE correctly.
if not ctypes.windll.shell32.IsUserAnAdmin():
    if getattr(sys, "frozen", False):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, None, None, 1)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, '"%s"' % os.path.abspath(__file__), None, 1)
    sys.exit()

u32 = ctypes.windll.user32

APP_VERSION = "4.0.0"

# ── Win32 overlay helpers ──────────────────────────────────────────────────────
GWL_EXSTYLE       = -20
WS_EX_LAYERED     = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW  = 0x00000080
WS_EX_NOACTIVATE  = 0x08000000
HWND_TOPMOST      = -1
SWP_NOMOVE        = 0x0002
SWP_NOSIZE        = 0x0001
SWP_NOACTIVATE    = 0x0010

def fix_window(hwnd):
    s = u32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    u32.SetWindowLongW(
        hwnd,
        GWL_EXSTYLE,
        s | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE,
    )
    u32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

def get_monitors():
    out = []

    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

    class MINFO(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("mon", RECT), ("work", RECT), ("fl", ctypes.c_ulong)]

    CB = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_longlong)

    def h(hm, hd, lp, x):
        m = MINFO()
        m.cb = ctypes.sizeof(MINFO)
        u32.GetMonitorInfoW(hm, ctypes.byref(m))
        r = m.mon
        out.append((r.left, r.top, r.right - r.left, r.bottom - r.top))
        return True

    u32.EnumDisplayMonitors(None, None, CB(h), 0)
    if not out:
        out = [(0, 0, u32.GetSystemMetrics(0), u32.GetSystemMetrics(1))]
    return out

# ── Theme / settings ───────────────────────────────────────────────────────────
def app_base_dir():
    root = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "MigraineFilter")
    os.makedirs(root, exist_ok=True)
    return root

SETTINGS_FILE = os.path.join(app_base_dir(), "migraine_settings.json")

THEMES = {
    "Cozy Pink":   {"bg": wx.Colour(25,18,25), "card": wx.Colour(43,30,40), "accent": wx.Colour(224,126,169), "text": wx.Colour(250,242,247), "sub": wx.Colour(201,171,187), "pink": wx.Colour(255,181,211)},
    "Dusty Rose":  {"bg": wx.Colour(28,20,25), "card": wx.Colour(52,35,44), "accent": wx.Colour(181,108,139), "text": wx.Colour(252,243,247), "sub": wx.Colour(205,173,187), "pink": wx.Colour(231,157,188)},
    "Sky Blue":    {"bg": wx.Colour(15,24,33), "card": wx.Colour(26,40,53), "accent": wx.Colour(104,177,220), "text": wx.Colour(241,248,252), "sub": wx.Colour(164,194,210), "pink": wx.Colour(155,214,242)},
    "Lavender":    {"bg": wx.Colour(22,18,31), "card": wx.Colour(38,31,51), "accent": wx.Colour(157,116,210), "text": wx.Colour(246,241,251), "sub": wx.Colour(185,169,202), "pink": wx.Colour(213,181,244)},
    "Sage":        {"bg": wx.Colour(18,27,23), "card": wx.Colour(31,44,37), "accent": wx.Colour(121,174,141), "text": wx.Colour(242,248,244), "sub": wx.Colour(169,194,178), "pink": wx.Colour(174,220,190)},
    "Peach":       {"bg": wx.Colour(34,22,22), "card": wx.Colour(53,35,33), "accent": wx.Colour(224,143,122), "text": wx.Colour(255,244,239), "sub": wx.Colour(210,174,164), "pink": wx.Colour(255,188,169)},
    "Berry":       {"bg": wx.Colour(29,16,27), "card": wx.Colour(49,26,43), "accent": wx.Colour(194,91,148), "text": wx.Colour(252,240,248), "sub": wx.Colour(203,160,188), "pink": wx.Colour(241,151,199)},
    "Obsidian":    {"bg": wx.Colour(10,11,15), "card": wx.Colour(20,22,29), "accent": wx.Colour(105,116,143), "text": wx.Colour(240,242,248), "sub": wx.Colour(148,154,171), "pink": wx.Colour(188,194,217)},
    "Midnight":    {"bg": wx.Colour(10,15,29), "card": wx.Colour(20,28,47), "accent": wx.Colour(89,119,190), "text": wx.Colour(239,244,255), "sub": wx.Colour(148,166,204), "pink": wx.Colour(147,172,232)},
    "Cream Cocoa": {"bg": wx.Colour(35,29,25), "card": wx.Colour(56,45,38), "accent": wx.Colour(194,151,116), "text": wx.Colour(252,243,231), "sub": wx.Colour(205,183,160), "pink": wx.Colour(231,190,154)},
}

DEFAULT_SETTINGS = {
    "global_filter": "pink_blackout",
    "global_intensity": "7",
    "global_on": True,
    "per_monitor": {},
    "use_per_monitor": False,
    "profiles": {
        "Migraine": {"filter": "obsidian", "intensity": "18"},
        "Study": {"filter": "warm_white", "intensity": "7"},
        "Night": {"filter": "midnight", "intensity": "12"},
    },
    "default_profile": "",
    "idle_threshold": 300,
    "idle_boost": 5,
    "startup": False,
    "emergency_restore_mins": 10,
    "transition_speed": 0.25,
    "paused_until": 0,
    "white_point_killer": False,
    "white_point_killer_boost": 3,
    "theme_name": "Cozy Pink",
    "window_opacity": 220,
    "mode_name": "Everyday",
    "diary_entries": [],
    "usage_today_secs": 0,
    "usage_today_date": "",
    "hotkeys": {
        "toggle":    {"mod": 0x0006, "vk": 0x46, "label": "Ctrl+Shift+F"},
        "emergency": {"mod": 0x0006, "vk": 0x45, "label": "Ctrl+Shift+E"},
        "intensity_up":   {"mod": 0x0006, "vk": 0x26, "label": "Ctrl+Shift+Up"},
        "intensity_down": {"mod": 0x0006, "vk": 0x28, "label": "Ctrl+Shift+Down"},
        "cycle_filter":   {"mod": 0x0006, "vk": 0x09, "label": "Ctrl+Shift+Tab"},
    },
}

PRESETS = {
    "Cozy":    {"filter": "dusty_rose", "intensity": "9",  "white_point_killer": False},
    "Migraine":{"filter": "obsidian",   "intensity": "18", "white_point_killer": True},
    "Reading": {"filter": "warm_white", "intensity": "7",  "white_point_killer": False},
    "Night":   {"filter": "midnight",   "intensity": "12", "white_point_killer": True},
    "Movie":   {"filter": "smoke",      "intensity": "8",  "white_point_killer": False},
    "Gaming":  {"filter": "navy",       "intensity": "6",  "white_point_killer": False},
    "Pause":   {"pause": 10},
}

MODES = {
    "Everyday": ("dusty_rose", "8", False),
    "Reading":  ("warm_white", "7", False),
    "Migraine": ("obsidian", "18", True),
    "Night":    ("midnight", "12", True),
    "Movie":    ("smoke", "8", False),
    "Gaming":   ("navy", "6", False),
}

def load_settings():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            s = json.load(f)
        for k, v in DEFAULT_SETTINGS.items():
            if k not in s:
                s[k] = v
        return s
    except Exception:
        return dict(DEFAULT_SETTINGS)

def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass

# ── Filters ────────────────────────────────────────────────────────────────────
FILTERS = {
    "pink":          {"name": "🌸 Pink",           "icon": (255, 182, 193), "col": "#FFB8CC"},
    "pink_blackout": {"name": "💗 Pink Blackout", "icon": (214, 126, 156), "col": "#D67E9C"},
    "dark_pink":     {"name": "🌹 Dark Pink",     "icon": (180, 80, 110),  "col": "#C8607A"},
    "rose_dim":      {"name": "🌷 Rose Dim",      "icon": (210, 100, 130), "col": "#D4607A"},
    "purple":        {"name": "🟣 Lavender",      "icon": (180, 130, 220), "col": "#C8A0E8"},
    "amber":         {"name": "🟠 Amber",         "icon": (255, 160, 60),  "col": "#FFB347"},
    "green":         {"name": "🟢 Forest Green",  "icon": (100, 180, 100), "col": "#90EE90"},
    "warm_white":    {"name": "⚪ Warm White",    "icon": (255, 240, 200), "col": "#FFF5CC"},
    "deep_red":      {"name": "🔴 Deep Red",      "icon": (200, 50, 50),   "col": "#CC3333"},
    "bluelight":     {"name": "💙 Blue Light",    "icon": (100, 160, 255), "col": "#BFD6FF"},
    "dark":          {"name": "🌑 Dark Dimmer",   "icon": (40, 40, 40),    "col": "#000000"},
    "midnight":      {"name": "🌙 Midnight Dim",  "icon": (25, 18, 36),    "col": "#030207"},
    "obsidian":      {"name": "🖤 Obsidian Dim",  "icon": (10, 10, 14),    "col": "#000000"},
    "dusty_rose": {"name": "🌸 Dusty Rose", "icon": (112, 72, 90), "col": "#70485A"},
    "peach":      {"name": "🍑 Peach",      "icon": (124, 78, 65), "col": "#7C4E41"},
    "sepia":      {"name": "🤎 Sepia",      "icon": (105, 82, 58), "col": "#69523A"},
    "sage":       {"name": "🌿 Sage",       "icon": (70, 91, 73),  "col": "#465B49"},
    "soft_cyan":  {"name": "🩵 Soft Cyan",  "icon": (55, 87, 92),  "col": "#37575C"},
    "mauve":      {"name": "🪻 Mauve",      "icon": (88, 66, 91),  "col": "#58425B"},
    "smoke":      {"name": "☁ Smoke",       "icon": (55, 58, 66),  "col": "#373A42"},
    "cocoa":      {"name": "☕ Cocoa",       "icon": (72, 53, 47),  "col": "#48352F"},
    "navy":       {"name": "🌌 Navy",       "icon": (31, 43, 68),  "col": "#1F2B44"},
    "burgundy":   {"name": "🍷 Burgundy",   "icon": (75, 35, 49),  "col": "#4B2331"},

}

ALPHAS = {
    "pink":          [3, 5, 7, 10, 13, 17, 22, 28, 34, 42, 50, 60, 71, 84, 100, 118, 138, 160, 185, 210],
    "pink_blackout": [10, 14, 18, 24, 31, 39, 49, 60, 72, 86, 101, 117, 134, 152, 171, 190, 207, 221, 232, 240],
    "dark_pink":     [6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120, 136, 153, 171, 189, 206, 220, 232],
    "rose_dim":      [7, 11, 16, 22, 30, 39, 49, 60, 72, 85, 99, 114, 130, 147, 165, 183, 200, 216, 228, 238],
    "purple":        [5, 8, 12, 17, 23, 30, 38, 47, 57, 68, 80, 93, 107, 122, 138, 155, 173, 191, 208, 224],
    "amber":         [5, 8, 12, 16, 21, 27, 34, 42, 51, 61, 72, 84, 97, 111, 126, 142, 159, 176, 193, 208],
    "green":         [5, 8, 12, 16, 21, 27, 34, 42, 51, 61, 72, 84, 97, 111, 126, 142, 159, 176, 193, 208],
    "warm_white":    [3, 5, 8, 11, 15, 19, 24, 30, 37, 44, 53, 62, 73, 85, 98, 112, 127, 143, 160, 178],
    "deep_red":      [6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120, 136, 153, 171, 189, 206, 220, 232],
    "bluelight":     [4, 7, 11, 15, 20, 26, 33, 41, 50, 60, 71, 83, 96, 110, 125, 140, 156, 172, 188, 205],
    "dark":          [5, 10, 16, 23, 31, 40, 50, 61, 73, 86, 100, 115, 131, 148, 165, 183, 200, 215, 228, 240],
    "midnight":      [8, 13, 20, 28, 37, 47, 58, 70, 83, 97, 112, 128, 145, 163, 181, 198, 214, 227, 238, 246],
    "obsidian":      [10, 16, 24, 33, 43, 54, 66, 79, 93, 108, 124, 141, 159, 178, 196, 212, 226, 237, 246, 252],
    "dusty_rose": [6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,189,206,220,232],
    "peach":      [5,8,12,16,21,27,34,42,51,61,72,84,97,111,126,142,159,176,193,208],
    "sepia":      [5,8,12,16,21,27,34,42,51,61,72,84,97,111,126,142,159,176,193,208],
    "sage":       [5,8,12,16,21,27,34,42,51,61,72,84,97,111,126,142,159,176,193,208],
    "soft_cyan":  [4,7,11,15,20,26,33,41,50,60,71,83,96,110,125,140,156,172,188,205],
    "mauve":      [5,8,12,17,23,30,38,47,57,68,80,93,107,122,138,155,173,191,208,224],
    "smoke":      [5,10,16,23,31,40,50,61,73,86,100,115,131,148,165,183,200,215,228,240],
    "cocoa":      [6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,189,206,220,232],
    "navy":       [8,13,20,28,37,47,58,70,83,97,112,128,145,163,181,198,214,227,238,246],
    "burgundy":   [6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,189,206,220,232],

}

def get_alpha(fk, level_str):
    idx = int(level_str) - 1
    return ALPHAS.get(fk, ALPHAS["dark"])[max(0, min(19, idx))]

def get_color(fk):
    return FILTERS[fk]["col"]

def wxcol(h):
    h = h.lstrip("#")
    return wx.Colour(int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16))

def mkicon():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    petal_color = (255, 160, 190, 230)
    petal_r = 11
    import math
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        px = int(cx + 13 * math.cos(angle))
        py = int(cy + 13 * math.sin(angle))
        d.ellipse([px - petal_r, py - petal_r, px + petal_r, py + petal_r], fill=petal_color)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 220, 80, 255))
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 240, 140, 255))
    return img

# ── Startup registry ───────────────────────────────────────────────────────────
REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_NAME = "DuskBloom Screen"

def _pythonw_path():
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return pyw if os.path.exists(pyw) else sys.executable

def set_startup(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE)
        if enable:
            if getattr(sys, "frozen", False):
                cmd = f'"{sys.executable}"'
            else:
                cmd = f'"{_pythonw_path()}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, REG_NAME)
            except Exception:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def get_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ)
        cmd = str(winreg.QueryValueEx(key, REG_NAME)[0]).strip()
        winreg.CloseKey(key)
        # A startup toggle is only ON when Windows points at something that exists.
        quoted = re.findall(r'"([^"]+)"', cmd)
        target = quoted[0] if quoted else cmd.split()[0]
        return bool(target and os.path.isfile(target))
    except Exception:
        return False

# ── Overlay / popup ────────────────────────────────────────────────────────────
class Panel(wx.Frame):
    def __init__(self, x, y, w, h):
        super().__init__(None, style=wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.FRAME_TOOL_WINDOW)
        self.SetPosition((x, y))
        self.SetSize((w, h))
        self.SetBackgroundColour(wx.Colour(255, 184, 204))
        self.SetTransparent(36)
        self.Show(False)
        self._target_alpha = 36
        self._cur_alpha = 0.0

    def set_target(self, color, alpha):
        self._target_alpha = int(alpha)
        self.SetBackgroundColour(wxcol(color))
        self.Refresh()

    def step_transition(self, speed=0.25):
        diff = self._target_alpha - self._cur_alpha
        if abs(diff) < 1.0:
            self._cur_alpha = float(self._target_alpha)
            self.SetTransparent(int(self._cur_alpha))
            return False
        step = diff * min(1.0, 0.016 / max(speed, 0.01) * 8)
        self._cur_alpha += step
        self.SetTransparent(int(max(0, min(254, self._cur_alpha))))
        return True

    def show_now(self):
        if not self.IsShown():
            self.Show(True)
            self.Update()
        fix_window(self.GetHandle())

    def push(self):
        if self.IsShown():
            fix_window(self.GetHandle())

    def hide(self):
        self.Show(False)

def _toast(title, msg):
    _toast._queue.append((title, msg))
_toast._queue = []

def _flush_toasts(tray):
    while _toast._queue:
        title, msg = _toast._queue.pop(0)
        try:
            tray.notify(msg, title)
        except Exception:
            pass

class MiniPopup(wx.Frame):
    def __init__(self):
        super().__init__(None, style=wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.FRAME_TOOL_WINDOW)
        self.SetBackgroundColour(wx.Colour(18, 18, 28))
        self.SetSize((260, 150))
        self.SetTransparent(0)
        self._timer = wx.Timer(self)
        self._fade_timer = wx.Timer(self)
        self._alpha = 0
        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)
        self.Bind(wx.EVT_TIMER, self._on_fade, self._fade_timer)
        self.Bind(wx.EVT_LEFT_DOWN, lambda e: self.Hide())

        outer = wx.BoxSizer(wx.VERTICAL)
        self._title = wx.StaticText(self, label="🌸 Migraine Filter")
        self._title.SetForegroundColour(wx.Colour(255, 184, 204))
        self._title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self._filter_lbl = wx.StaticText(self, label="Filter: —")
        self._filter_lbl.SetForegroundColour(wx.Colour(240, 240, 240))
        self._level_lbl = wx.StaticText(self, label="Level: —")
        self._level_lbl.SetForegroundColour(wx.Colour(240, 240, 240))
        self._status_lbl = wx.StaticText(self, label="Status: —")
        self._status_lbl.SetForegroundColour(wx.Colour(150, 150, 170))
        self._hint = wx.StaticText(self, label="Click to dismiss")
        self._hint.SetForegroundColour(wx.Colour(90, 90, 110))
        for w in (self._title, self._filter_lbl, self._level_lbl, self._status_lbl, self._hint):
            outer.Add(w, 0, wx.LEFT | wx.TOP, 12)
        self.SetSizer(outer)
        self.Show(False)

    def show_near_tray(self, s):
        fk = s.get("global_filter", "dark")
        lv = s.get("global_intensity", "?")
        on = s.get("global_on", True)
        pm = s.get("use_per_monitor", False)
        pau = s.get("paused_until", 0) > time.time()
        wpk = s.get("white_point_killer", False)

        self._filter_lbl.SetLabel(f"Filter: {FILTERS.get(fk, {}).get('name', fk)}")
        self._level_lbl.SetLabel(f"Level: {lv} / 20")
        status = "⏸ Paused" if pau else ("🖥️ Per-monitor" if pm else ("✅ Active" if on else "⬜ Off"))
        if wpk:
            status += " · White Killer"
        self._status_lbl.SetLabel(f"Status: {status}")

        sw, sh = u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)
        w, h = self.GetSize()
        self.SetPosition((sw - w - 10, sh - h - 50))
        self.SetTransparent(0)
        self._alpha = 0
        self.Show(True)
        self.Raise()
        self._fade_mode = "in"
        self._fade_timer.Start(15)
        self._timer.Start(3500)

    def _on_timer(self, e):
        self._timer.Stop()
        self._fade_mode = "out"
        self._fade_timer.Start(15)

    def _on_fade(self, e):
        if self._fade_mode == "in":
            self._alpha += 24
            if self._alpha >= 235:
                self._alpha = 235
                self._fade_timer.Stop()
        else:
            self._alpha -= 18
            if self._alpha <= 0:
                self._alpha = 0
                self._fade_timer.Stop()
                self.Hide()
        self.SetTransparent(self._alpha)


class MiniController(wx.Frame):
    def __init__(self, app):
        super().__init__(None, title="♡ DuskBloom Screen", size=(380, 165),
                         style=wx.CAPTION | wx.STAY_ON_TOP | wx.FRAME_TOOL_WINDOW | wx.CLOSE_BOX)
        self.app = app
        th = THEMES.get(app.s.get("theme_name", "Cozy Pink"), THEMES["Cozy Pink"])
        self.SetBackgroundColour(th["bg"])
        s = wx.BoxSizer(wx.VERTICAL)
        t = wx.StaticText(self, label="♡  DuskBloom Screen · Mini")
        t.SetForegroundColour(th["pink"])
        t.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        s.Add(t, 0, wx.ALL, 10)
        r = wx.BoxSizer(wx.HORIZONTAL)
        for label, mode in [("📖 Reading","Reading"),("☾ Night","Night"),("🎮 Gaming","Gaming")]:
            b = wx.Button(self, label=label, size=(105,30))
            b.SetBackgroundColour(th["card"]); b.SetForegroundColour(th["text"])
            b.Bind(wx.EVT_BUTTON, lambda e, n=mode: self.app._apply_mode(n))
            r.Add(b, 0, wx.RIGHT, 6)
        s.Add(r, 0, wx.LEFT | wx.RIGHT, 10)
        r2 = wx.BoxSizer(wx.HORIZONTAL)
        for label, fn in [
            ("−", self.app._intensity_down), ("+", self.app._intensity_up),
            ("Pause 10m", lambda: self.app._pause_for_minutes(10))
        ]:
            b = wx.Button(self, label=label, size=(92 if "Pause" in label else 48, 30))
            b.Bind(wx.EVT_BUTTON, lambda e, f=fn: f())
            r2.Add(b, 0, wx.RIGHT, 6)
        peek = wx.Button(self, label="👁 Peek", size=(88,30))
        peek.Bind(wx.EVT_LEFT_DOWN, lambda e: self.app._peek_start())
        peek.Bind(wx.EVT_LEFT_UP, lambda e: self.app._peek_end())
        r2.Add(peek, 0)
        s.Add(r2, 0, wx.ALL, 10)
        self.SetSizer(s)
        self.Bind(wx.EVT_CLOSE, lambda e: self.Hide())

    def show_safe(self):
        self.SetPosition((110,110))
        self.Show()
        self.Raise()
        wx.CallLater(120, lambda: self.SetTransparent(225))

# ── DuskBloom Center bridge ───────────────────────────────────────────────────────
MELLOW_BRIDGE_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"),
                                 "DuskBloom", "DuskBloomScreen")
LEGACY_MELLOW_BRIDGE_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"),
                                        "Mellow", "MellowScreen")
MELLOW_STATE_FILE = os.path.join(MELLOW_BRIDGE_DIR, "state.json")
MELLOW_COMMAND_FILE = os.path.join(MELLOW_BRIDGE_DIR, "command.json")
MELLOW_MANIFEST_FILE = os.path.join(MELLOW_BRIDGE_DIR, "manifest.json")

def _atomic_json_write(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
        return True
    except Exception:
        return False


# ── Settings window ────────────────────────────────────────────────────────────
class SettingsWindow(wx.Frame):
    def __init__(self, parent_app):
        self.app = parent_app
        self.s = parent_app.s
        theme = THEMES.get(self.s.get("theme_name", "Cozy Pink"), THEMES["Cozy Pink"])
        self.BG = theme["bg"]; self.CARD = theme["card"]; self.ACC = theme["accent"]
        self.TXT = theme["text"]; self.SUB = theme["sub"]; self.PINK = theme["pink"]

        super().__init__(None, title="DuskBloom Screen", size=(940, 740),
                         style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU)
        self.SetBackgroundColour(self.BG)
        self.SetPosition((80, 80))
        self._monitor_controls = []

        # DuskBloom's own navigation shell — no native Windows tab strip.
        self.shell = wx.Panel(self)
        self.shell.SetBackgroundColour(self.BG)
        self.sidebar = wx.Panel(self.shell, size=(178, -1))
        self.sidebar.SetBackgroundColour(self.CARD)
        self.page_host = wx.Panel(self.shell)
        self.page_host.SetBackgroundColour(self.BG)

        self.tab_main = self._make_scroll(self.page_host)
        self.tab_mon = self._make_scroll(self.page_host)
        self.tab_prof = self._make_scroll(self.page_host)
        self.tab_app = self._make_scroll(self.page_host)
        self.tab_diary = self._make_scroll(self.page_host)
        self._pages = [self.tab_main, self.tab_mon, self.tab_prof, self.tab_app, self.tab_diary]

        self._build_main_tab()
        self._build_mon_tab()
        self._build_prof_tab()
        self._build_app_tab()
        self._build_diary_tab()

        side = wx.BoxSizer(wx.VERTICAL)
        brand = wx.StaticText(self.sidebar, label="DuskBloom")
        brand.SetForegroundColour(self.PINK)
        brand.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        side.Add(brand, 0, wx.LEFT | wx.TOP, 18)
        product = wx.StaticText(self.sidebar, label="S C R E E N")
        product.SetForegroundColour(self.SUB)
        product.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        side.Add(product, 0, wx.LEFT | wx.TOP, 18)
        side.AddSpacer(26)

        self._nav_buttons = []
        for label, idx in [("♡   Home",0), ("▣   Screens",1), ("✿   Presets",2),
                           ("✧   Appearance",3), ("☾   Comfort Log",4)]:
            b = wx.Button(self.sidebar, label=label, style=wx.BORDER_NONE, size=(-1, 42))
            b.SetBackgroundColour(self.CARD)
            b.SetForegroundColour(self.TXT)
            b.Bind(wx.EVT_BUTTON, lambda e, i=idx: self._show_page(i))
            self._nav_buttons.append(b)
            side.Add(b, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        side.AddStretchSpacer(1)
        self._side_state = wx.StaticText(self.sidebar, label="●  Screen filter active")
        self._side_state.SetForegroundColour(self.PINK)
        side.Add(self._side_state, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 16)
        ver = wx.StaticText(self.sidebar, label="v" + APP_VERSION)
        ver.SetForegroundColour(self.SUB)
        side.Add(ver, 0, wx.LEFT | wx.BOTTOM, 18)
        self.sidebar.SetSizer(side)

        pages = wx.BoxSizer(wx.VERTICAL)
        for p in self._pages:
            pages.Add(p, 1, wx.EXPAND)
        self.page_host.SetSizer(pages)

        shell_sizer = wx.BoxSizer(wx.HORIZONTAL)
        shell_sizer.Add(self.sidebar, 0, wx.EXPAND)
        shell_sizer.Add(self.page_host, 1, wx.EXPAND)
        self.shell.SetSizer(shell_sizer)

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(self.shell, 1, wx.EXPAND)
        self.SetSizer(outer)
        self._show_page(0)
        self.Bind(wx.EVT_CLOSE, lambda e: self.Hide())
        self._sync_from_settings()

    def _show_page(self, idx):
        # Hide first and show one page only. This prevents stale first-paint
        # content in Windows ScrolledWindow when using our custom navigation.
        for page in self._pages:
            page.Hide()
        page = self._pages[idx]
        page.Show()

        for i, b in enumerate(self._nav_buttons):
            b.SetBackgroundColour(self.ACC if i == idx else self.CARD)
            b.SetForegroundColour(wx.Colour(255,255,255) if i == idx else self.TXT)

        try:
            page.FitInside()
            page.Layout()
        except Exception:
            pass
        self.page_host.Layout()
        self.shell.Layout()
        self.Layout()
        page.Refresh()
        self.page_host.Refresh()
        self.sidebar.Refresh()
        self.Update()
        wx.CallAfter(self._finish_page_switch, page)

    def _finish_page_switch(self, page):
        # Repaint once after Windows has processed the show/layout messages.
        try:
            page.FitInside()
            page.Layout()
            self.page_host.Layout()
            page.Refresh()
            self.page_host.Refresh()
            self.sidebar.Refresh()
            self.Update()
        except Exception:
            pass

    def _make_scroll(self, parent):
        sw = wx.ScrolledWindow(parent, style=wx.VSCROLL)
        sw.SetBackgroundColour(self.BG)
        sw.SetScrollRate(0, 12)
        return sw

    def _title(self, parent, txt):
        t = wx.StaticText(parent, label=txt)
        t.SetForegroundColour(self.PINK)
        t.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        return t

    def _label(self, parent, txt):
        t = wx.StaticText(parent, label=txt)
        t.SetForegroundColour(self.TXT)
        return t

    def _sub(self, parent, txt):
        t = wx.StaticText(parent, label=txt)
        t.SetForegroundColour(self.SUB)
        t.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        return t

    def _preset_button(self, parent, name, desc):
        p = wx.Panel(parent)
        p.SetBackgroundColour(self.CARD)
        s = wx.BoxSizer(wx.VERTICAL)
        a = wx.StaticText(p, label=name)
        a.SetForegroundColour(self.PINK)
        a.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        b = wx.StaticText(p, label=desc)
        b.SetForegroundColour(self.SUB)
        btn = wx.Button(p, label="♡ Use preset", size=(-1, 32))
        btn.SetBackgroundColour(self.ACC)
        btn.SetForegroundColour(wx.Colour(255, 255, 255))
        btn.Bind(wx.EVT_BUTTON, lambda e, n=name: self.app._apply_preset(n))
        s.Add(a, 0, wx.ALL, 10)
        s.Add(b, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        s.Add(btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        p.SetSizer(s)
        return p

    def _build_main_tab(self):
        main = wx.BoxSizer(wx.VERTICAL)
        pad = 18

        # Header
        main.AddSpacer(16)
        top = wx.BoxSizer(wx.HORIZONTAL)
        left = wx.BoxSizer(wx.VERTICAL)
        hdr = wx.StaticText(self.tab_main, label="DuskBloom Screen  🌷")
        hdr.SetForegroundColour(self.PINK)
        hdr.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        left.Add(hdr, 0)
        left.AddSpacer(3)
        left.Add(self._sub(self.tab_main, "soft screen comfort for every display."), 0)
        top.Add(left, 1)

        center_badge = wx.StaticText(self.tab_main, label="  DuskBloom Center · connected  ")
        center_badge.SetForegroundColour(self.ACC)
        center_badge.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        top.Add(center_badge, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        main.Add(top, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        main.AddSpacer(14)

        # Comfort Dashboard
        dash = wx.Panel(self.tab_main)
        dash.SetBackgroundColour(self.CARD)
        ds = wx.BoxSizer(wx.VERTICAL)
        dash_title = wx.StaticText(dash, label="♡  Your comfort setup")
        dash_title.SetForegroundColour(self.PINK)
        dash_title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        ds.Add(dash_title, 0, wx.LEFT | wx.TOP, 14)

        self._home_status = wx.StaticText(dash, label="")
        self._home_status.SetForegroundColour(self.TXT)
        self._home_status.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        ds.Add(self._home_status, 0, wx.LEFT | wx.RIGHT | wx.TOP, 14)

        self._home_substatus = wx.StaticText(dash, label="")
        self._home_substatus.SetForegroundColour(self.SUB)
        ds.Add(self._home_substatus, 0, wx.LEFT | wx.RIGHT | wx.TOP, 14)

        actions = wx.BoxSizer(wx.HORIZONTAL)
        softer = wx.Button(dash, label="− Softer", size=(92, 32))
        softer.SetBackgroundColour(self.CARD); softer.SetForegroundColour(self.TXT)
        softer.Bind(wx.EVT_BUTTON, lambda e: self.app._intensity_down())
        actions.Add(softer, 0, wx.RIGHT, 7)

        brighter = wx.Button(dash, label="+ Stronger", size=(96, 32))
        brighter.SetBackgroundColour(self.CARD); brighter.SetForegroundColour(self.TXT)
        brighter.Bind(wx.EVT_BUTTON, lambda e: self.app._intensity_up())
        actions.Add(brighter, 0, wx.RIGHT, 7)

        peek = wx.Button(dash, label="◉ Peek", size=(82, 32))
        peek.SetBackgroundColour(self.CARD); peek.SetForegroundColour(self.TXT)
        peek.Bind(wx.EVT_LEFT_DOWN, lambda e: self.app._peek_start())
        peek.Bind(wx.EVT_LEFT_UP, lambda e: self.app._peek_end())
        actions.Add(peek, 0, wx.RIGHT, 7)

        pause_btn = wx.Button(dash, label="Pause 10m", size=(94, 32))
        pause_btn.SetBackgroundColour(self.ACC)
        pause_btn.SetForegroundColour(wx.Colour(255,255,255))
        pause_btn.Bind(wx.EVT_BUTTON, lambda e: self.app._pause_for_minutes(10))
        actions.Add(pause_btn, 0, wx.RIGHT, 7)

        mini_btn = wx.Button(dash, label="♡ Mini", size=(78, 32))
        mini_btn.SetBackgroundColour(self.CARD); mini_btn.SetForegroundColour(self.TXT)
        mini_btn.Bind(wx.EVT_BUTTON, lambda e: self.app._show_mini_controller())
        actions.Add(mini_btn, 0)

        ds.Add(actions, 0, wx.ALL, 14)
        dash.SetSizer(ds)
        main.Add(dash, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        main.AddSpacer(18)

        # Main toggles in a quiet row
        toggles = wx.BoxSizer(wx.HORIZONTAL)
        self._global_on_cb = wx.CheckBox(self.tab_main, label="Screen filter")
        self._global_on_cb.SetForegroundColour(self.TXT)
        self._global_on_cb.Bind(wx.EVT_CHECKBOX, lambda e: self.app._set_global_on(e.IsChecked()))
        toggles.Add(self._global_on_cb, 0, wx.RIGHT, 22)

        self._wpk_cb = wx.CheckBox(self.tab_main, label="White Point Killer")
        self._wpk_cb.SetForegroundColour(self.TXT)
        self._wpk_cb.Bind(wx.EVT_CHECKBOX, lambda e: self._set_opt("white_point_killer", e.IsChecked()))
        toggles.Add(self._wpk_cb, 0)
        main.Add(toggles, 0, wx.LEFT, pad)
        main.AddSpacer(20)

        # Comfort modes - primary way to change the whole setup
        main.Add(self._title(self.tab_main, "Comfort Modes"), 0, wx.LEFT, pad)
        main.AddSpacer(8)
        mode_grid = wx.GridSizer(rows=2, cols=3, hgap=8, vgap=8)
        mode_icons = {
            "Everyday": "♡ Everyday", "Reading": "📖 Reading", "Migraine": "✦ Migraine",
            "Night": "☾ Night", "Movie": "◐ Movie", "Gaming": "◇ Gaming"
        }
        for mode_name in MODES:
            b = wx.Button(self.tab_main, label=mode_icons.get(mode_name, mode_name), size=(-1, 36))
            b.SetBackgroundColour(self.CARD)
            b.SetForegroundColour(self.TXT)
            b.Bind(wx.EVT_BUTTON, lambda e, n=mode_name: self.app._apply_mode(n))
            mode_grid.Add(b, 1, wx.EXPAND)
        main.Add(mode_grid, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        main.AddSpacer(20)

        # Quick presets: no giant cards on Home anymore
        main.Add(self._title(self.tab_main, "Quick Presets"), 0, wx.LEFT, pad)
        main.AddSpacer(8)
        preset_row = wx.WrapSizer()
        for name in ["Cozy", "Migraine", "Reading", "Night", "Movie", "Gaming"]:
            if name not in PRESETS:
                continue
            b = wx.Button(self.tab_main, label="♡ " + name, size=(108, 32))
            b.SetBackgroundColour(self.ACC if name == "Cozy" else self.CARD)
            b.SetForegroundColour(wx.Colour(255,255,255) if name == "Cozy" else self.TXT)
            b.Bind(wx.EVT_BUTTON, lambda e, n=name: self.app._apply_preset(n))
            preset_row.Add(b, 0, wx.RIGHT | wx.BOTTOM, 7)
        main.Add(preset_row, 0, wx.LEFT | wx.RIGHT, pad)
        main.AddSpacer(20)

        # Compact color picker instead of 23 large buttons
        main.Add(self._title(self.tab_main, "Screen Color"), 0, wx.LEFT, pad)
        main.AddSpacer(8)
        color_row = wx.BoxSizer(wx.HORIZONTAL)
        color_names = [FILTERS[k]["name"] for k in FILTERS]
        self._home_color_choice = wx.Choice(self.tab_main, choices=color_names, size=(260, -1))
        keys = list(FILTERS.keys())
        try:
            self._home_color_choice.SetSelection(keys.index(self.s.get("global_filter", keys[0])))
        except Exception:
            self._home_color_choice.SetSelection(0)
        self._home_color_choice.Bind(
            wx.EVT_CHOICE,
            lambda e: self.app._set_filter_all(keys[self._home_color_choice.GetSelection()])
        )
        color_row.Add(self._home_color_choice, 0, wx.RIGHT, 10)

        palette_btn = wx.Button(self.tab_main, label="View full palette →", size=(135, 30))
        palette_btn.SetBackgroundColour(self.CARD); palette_btn.SetForegroundColour(self.TXT)
        palette_btn.Bind(wx.EVT_BUTTON, lambda e: self._open_appearance_tab())
        color_row.Add(palette_btn, 0)
        main.Add(color_row, 0, wx.LEFT, pad)
        main.AddSpacer(18)

        # Clean intensity control
        int_head = wx.BoxSizer(wx.HORIZONTAL)
        int_head.Add(self._title(self.tab_main, "Intensity"), 1)
        self._int_value_label = wx.StaticText(self.tab_main, label=str(self.s.get("global_intensity", "8")) + " / 20")
        self._int_value_label.SetForegroundColour(self.PINK)
        self._int_value_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        int_head.Add(self._int_value_label, 0)
        main.Add(int_head, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        main.AddSpacer(7)

        self._int_slider = wx.Slider(self.tab_main, value=int(self.s["global_intensity"]),
                                    minValue=1, maxValue=20, style=wx.SL_HORIZONTAL)
        self._int_slider.Bind(wx.EVT_SLIDER, self._on_intensity_slider)
        main.Add(self._int_slider, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        # Keep a hidden-compatible spin control because sync code expects it.
        self._int_spin = wx.SpinCtrl(self.tab_main, min=1, max=20,
                                     value=self.s["global_intensity"], size=(1, 1))
        self._int_spin.Hide()
        main.AddSpacer(22)

        # Per-monitor hint instead of duplicating controls
        monitor_card = wx.Panel(self.tab_main)
        monitor_card.SetBackgroundColour(self.CARD)
        ms = wx.BoxSizer(wx.HORIZONTAL)
        mt = wx.StaticText(monitor_card, label="🖥  Need different settings on each screen?")
        mt.SetForegroundColour(self.TXT)
        ms.Add(mt, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 12)
        mb = wx.Button(monitor_card, label="Open Screens →", size=(120, 30))
        mb.SetBackgroundColour(self.CARD); mb.SetForegroundColour(self.PINK)
        mb.Bind(wx.EVT_BUTTON, lambda e: self._open_screens_tab())
        ms.Add(mb, 0, wx.ALL, 8)
        monitor_card.SetSizer(ms)
        main.Add(monitor_card, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        main.AddSpacer(18)

        self.tab_main.SetSizer(main)

    def _open_screens_tab(self):
        self._show_page(1)

    def _open_appearance_tab(self):
        self._show_page(3)


    def _build_mon_tab(self):
        main = wx.BoxSizer(wx.VERTICAL)
        pad = 16

        main.AddSpacer(pad)
        main.Add(self._title(self.tab_mon, "My Screens  🖥 ♡"), 0, wx.LEFT, pad)
        main.AddSpacer(4)
        main.Add(self._sub(self.tab_mon, "Give each screen its own comfort level."), 0, wx.LEFT, pad)
        main.AddSpacer(10)

        quick = wx.BoxSizer(wx.HORIZONTAL)
        match_btn = wx.Button(self.tab_mon, label="♡ Apply Home to All", size=(145, 32))
        match_btn.SetBackgroundColour(self.ACC); match_btn.SetForegroundColour(wx.Colour(255,255,255))
        match_btn.Bind(wx.EVT_BUTTON, lambda e: self.app._match_all_monitors())
        quick.Add(match_btn, 0, wx.RIGHT, 8)
        side_btn = wx.Button(self.tab_mon, label="☾ Darken side screens", size=(155, 32))
        side_btn.SetBackgroundColour(self.CARD); side_btn.SetForegroundColour(self.TXT)
        side_btn.Bind(wx.EVT_BUTTON, lambda e: self.app._darken_side_monitors())
        quick.Add(side_btn, 0)
        main.Add(quick, 0, wx.LEFT, pad)
        main.AddSpacer(12)

        main.Add(self._title(self.tab_mon, "Screen Overview"), 0, wx.LEFT, pad)
        main.AddSpacer(7)
        overview = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(len(self.app.panels)):
            c = wx.Panel(self.tab_mon, size=(-1, 76))
            c.SetBackgroundColour(self.CARD)
            cs = wx.BoxSizer(wx.VERTICAL)
            num = wx.StaticText(c, label=f"Screen {i+1}")
            num.SetForegroundColour(self.PINK)
            num.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            cs.Add(num, 0, wx.ALL, 9)
            geo = self.app.mon_info[i] if i < len(self.app.mon_info) else (0,0,0,0)
            detail = wx.StaticText(c, label=f"{geo[2]}×{geo[3]}")
            detail.SetForegroundColour(self.SUB)
            cs.Add(detail, 0, wx.LEFT | wx.BOTTOM, 9)
            c.SetSizer(cs)
            overview.Add(c, 1, wx.RIGHT, 8)
        main.Add(overview, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        main.AddSpacer(16)

        self._pm_cb = wx.CheckBox(self.tab_mon, label="Enable per-monitor mode")
        self._pm_cb.SetForegroundColour(self.TXT)
        self._pm_cb.Bind(wx.EVT_CHECKBOX, lambda e: self._set_opt("use_per_monitor", e.IsChecked()))
        main.Add(self._pm_cb, 0, wx.LEFT, pad)
        main.AddSpacer(12)

        self._monitors_box = wx.BoxSizer(wx.VERTICAL)
        filter_choices = [FILTERS[k]["name"] for k in FILTERS]
        filter_keys = list(FILTERS.keys())

        for idx in range(len(self.app.panels)):
            mon_key = str(idx)
            mon_s = self.s["per_monitor"].setdefault(mon_key, {
                "filter": self.s["global_filter"],
                "intensity": self.s["global_intensity"],
                "on": self.s["global_on"],
            })

            card = wx.Panel(self.tab_mon)
            card.SetBackgroundColour(self.CARD)
            cs = wx.BoxSizer(wx.VERTICAL)
            title = wx.StaticText(card, label=f"Monitor {idx + 1}")
            title.SetForegroundColour(self.PINK)
            title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            cs.Add(title, 0, wx.ALL, 10)

            r = wx.BoxSizer(wx.HORIZONTAL)
            enabled_cb = wx.CheckBox(card, label="Enabled")
            enabled_cb.SetValue(mon_s.get("on", True))
            enabled_cb.SetForegroundColour(self.TXT)
            enabled_cb.Bind(wx.EVT_CHECKBOX, lambda e, i=idx: self.app._set_monitor_on(i, e.IsChecked()))
            r.Add(enabled_cb, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 14)

            lf = wx.StaticText(card, label="Filter:")
            lf.SetForegroundColour(self.TXT)
            r.Add(lf, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 8)

            choice = wx.Choice(card, choices=filter_choices)
            choice.SetSelection(filter_keys.index(mon_s.get("filter", self.s["global_filter"])))
            choice.Bind(wx.EVT_CHOICE, lambda e, i=idx, keys=filter_keys: self.app._set_monitor_filter(i, keys[e.GetSelection()]))
            r.Add(choice, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 14)

            ll = wx.StaticText(card, label="Level:")
            ll.SetForegroundColour(self.TXT)
            r.Add(ll, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 8)

            spin = wx.SpinCtrl(card, min=1, max=20, value=str(mon_s.get("intensity", self.s["global_intensity"])), size=(80, -1))
            spin.Bind(wx.EVT_SPINCTRL, lambda e, i=idx: self.app._set_monitor_intensity(i, e.GetEventObject().GetValue()))
            r.Add(spin, 0, wx.ALIGN_CENTER_VERTICAL)

            cs.Add(r, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
            card.SetSizer(cs)
            self._monitors_box.Add(card, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, pad)
            self._monitor_controls.append({"enabled": enabled_cb, "choice": choice, "spin": spin})

        main.Add(self._monitors_box, 0, wx.EXPAND)
        self.tab_mon.SetSizer(main)

    def _build_prof_tab(self):
        main = wx.BoxSizer(wx.VERTICAL)
        pad = 16

        main.AddSpacer(pad)
        main.Add(self._title(self.tab_prof, "Profiles"), 0, wx.LEFT, pad)
        main.AddSpacer(4)
        main.Add(self._sub(self.tab_prof, "Save and organize your favorite settings."), 0, wx.LEFT, pad)
        main.AddSpacer(10)

        self._profiles_panel = wx.Panel(self.tab_prof)
        self._profiles_panel.SetBackgroundColour(self.BG)
        self._profiles_sizer = wx.BoxSizer(wx.VERTICAL)
        self._profiles_panel.SetSizer(self._profiles_sizer)
        main.Add(self._profiles_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, pad)
        self._build_profiles_list()

        main.AddSpacer(10)
        save_row = wx.BoxSizer(wx.HORIZONTAL)
        self._prof_name = wx.TextCtrl(self.tab_prof, value="My Profile", size=(160, -1))
        save_btn = wx.Button(self.tab_prof, label="Save as New", size=(110, 28))
        save_btn.SetBackgroundColour(self.ACC)
        save_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        save_btn.Bind(wx.EVT_BUTTON, self._save_profile_ui)
        save_row.Add(self._prof_name, 0, wx.RIGHT, 8)
        save_row.Add(save_btn, 0)
        main.Add(save_row, 0, wx.LEFT, pad)
        main.AddSpacer(16)

        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self._label(self.tab_prof, "Default startup profile:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        choices = ["(none)"] + list(self.s.get("profiles", {}).keys())
        self._default_profile_choice = wx.Choice(self.tab_prof, choices=choices)
        cur = self.s.get("default_profile") or "(none)"
        self._default_profile_choice.SetSelection(choices.index(cur) if cur in choices else 0)
        self._default_profile_choice.Bind(wx.EVT_CHOICE, self._on_default_profile)
        row.Add(self._default_profile_choice, 0)
        main.Add(row, 0, wx.LEFT, pad)

        self.tab_prof.SetSizer(main)

    def _build_app_tab(self):
        main = wx.BoxSizer(wx.VERTICAL)
        pad = 18
        main.AddSpacer(14)
        main.Add(self._title(self.tab_app, "Make DuskBloom yours  ✧"), 0, wx.LEFT, pad)
        main.AddSpacer(4)
        main.Add(self._sub(self.tab_app, "Menu themes change DuskBloom itself. Screen colors change your displays."), 0, wx.LEFT, pad)
        main.AddSpacer(18)

        # Menu theme studio
        main.Add(self._title(self.tab_app, "Menu Themes"), 0, wx.LEFT, pad)
        main.AddSpacer(4)
        main.Add(self._sub(self.tab_app, "Preview a whole look before applying it."), 0, wx.LEFT, pad)
        main.AddSpacer(10)

        theme_grid = wx.GridSizer(rows=0, cols=2, hgap=10, vgap=10)
        for name, th in THEMES.items():
            card = wx.Panel(self.tab_app)
            card.SetBackgroundColour(th["card"])
            cs = wx.BoxSizer(wx.VERTICAL)
            top = wx.BoxSizer(wx.HORIZONTAL)
            swatch = wx.Panel(card, size=(30, 30)); swatch.SetBackgroundColour(th["accent"])
            top.Add(swatch, 0, wx.RIGHT, 9)
            labels = wx.BoxSizer(wx.VERTICAL)
            nm = wx.StaticText(card, label=name)
            nm.SetForegroundColour(th["text"])
            nm.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            labels.Add(nm, 0)
            tiny = wx.StaticText(card, label="●  ●  ●")
            tiny.SetForegroundColour(th["pink"])
            labels.Add(tiny, 0)
            top.Add(labels, 1)
            cs.Add(top, 0, wx.ALL | wx.EXPAND, 10)
            pb = wx.Button(card, label="Preview  →", size=(-1, 29))
            pb.SetBackgroundColour(th["accent"]); pb.SetForegroundColour(th["text"])
            pb.Bind(wx.EVT_BUTTON, lambda e, n=name: self._preview_theme(n))
            cs.Add(pb, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
            card.SetSizer(cs)
            theme_grid.Add(card, 1, wx.EXPAND)
        main.Add(theme_grid, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        main.AddSpacer(20)

        # Glass studio
        main.Add(self._title(self.tab_app, "Glass & Window"), 0, wx.LEFT, pad)
        main.AddSpacer(5)
        main.Add(self._sub(self.tab_app, "Solid on the right, dreamier glass on the left."), 0, wx.LEFT, pad)
        main.AddSpacer(8)
        glassrow = wx.BoxSizer(wx.HORIZONTAL)
        glassrow.Add(wx.StaticText(self.tab_app, label="More glass"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self._glass_slider = wx.Slider(self.tab_app, value=int(self.s.get("window_opacity", 220)),
                                      minValue=195, maxValue=255, size=(300, -1))
        self._glass_slider.Bind(wx.EVT_SLIDER, self._on_glass_slider)
        glassrow.Add(self._glass_slider, 1, wx.RIGHT, 8)
        glassrow.Add(wx.StaticText(self.tab_app, label="Solid"), 0, wx.ALIGN_CENTER_VERTICAL)
        main.Add(glassrow, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, pad)
        main.AddSpacer(20)

        # Whole setup memory
        main.Add(self._title(self.tab_app, "My Setup  ♡"), 0, wx.LEFT, pad)
        main.AddSpacer(5)
        main.Add(self._sub(self.tab_app, "Save the whole arrangement: screens, colors, levels, mode and menu theme."), 0, wx.LEFT, pad)
        main.AddSpacer(8)
        sr = wx.BoxSizer(wx.HORIZONTAL)
        sb = wx.Button(self.tab_app, label="♡ Save current setup", size=(155, 32))
        sb.SetBackgroundColour(self.ACC); sb.SetForegroundColour(wx.Colour(255,255,255))
        sb.Bind(wx.EVT_BUTTON, lambda e: self._save_current_setup())
        rb = wx.Button(self.tab_app, label="Restore My Setup", size=(145, 32))
        rb.SetBackgroundColour(self.CARD); rb.SetForegroundColour(self.TXT)
        rb.Bind(wx.EVT_BUTTON, lambda e: self._restore_my_setup())
        sr.Add(sb, 0, wx.RIGHT, 8); sr.Add(rb, 0)
        main.Add(sr, 0, wx.LEFT, pad)
        main.AddSpacer(20)

        # Full screen palette
        main.Add(self._title(self.tab_app, "Screen Color Palette"), 0, wx.LEFT, pad)
        main.AddSpacer(5)
        main.Add(self._sub(self.tab_app, "These tint the displays. They are separate from your menu theme."), 0, wx.LEFT, pad)
        main.AddSpacer(9)
        palette_wrap = wx.WrapSizer()
        self._filter_rb = {}
        for key, fi in FILTERS.items():
            r, g, b = fi["icon"]
            luma = 0.299*r + 0.587*g + 0.114*b
            fg = wx.Colour(255,255,255) if luma < 150 else wx.Colour(20,10,30)
            btn = wx.Button(self.tab_app, label=fi["name"], size=(-1, 31))
            btn.SetBackgroundColour(wx.Colour(r,g,b)); btn.SetForegroundColour(fg)
            btn.Bind(wx.EVT_BUTTON, lambda e, fk=key: self.app._set_filter_all(fk))
            self._filter_rb[key] = btn
            palette_wrap.Add(btn, 0, wx.RIGHT | wx.BOTTOM, 5)
        main.Add(palette_wrap, 0, wx.LEFT | wx.RIGHT, pad)
        main.AddSpacer(20)

        # Practical settings
        main.Add(self._title(self.tab_app, "Little Things"), 0, wx.LEFT, pad)
        main.AddSpacer(8)
        self._startup_cb = wx.CheckBox(self.tab_app, label="Start DuskBloom Screen with Windows")
        self._startup_cb.SetForegroundColour(self.TXT)
        self._startup_cb.Bind(wx.EVT_CHECKBOX, lambda e: self._set_opt("startup", e.IsChecked()))
        main.Add(self._startup_cb, 0, wx.LEFT, pad)
        main.AddSpacer(7)

        self._tray_cb = wx.CheckBox(self.tab_app, label="Keep DuskBloom in the system tray")
        self._tray_cb.SetForegroundColour(self.TXT)
        self._tray_cb.Bind(wx.EVT_CHECKBOX, lambda e: self._set_opt("tray", e.IsChecked()))
        main.Add(self._tray_cb, 0, wx.LEFT, pad)
        main.AddSpacer(7)

        self._transition_cb = wx.CheckBox(self.tab_app, label="Use gentle filter transitions")
        self._transition_cb.SetForegroundColour(self.TXT)
        self._transition_cb.Bind(wx.EVT_CHECKBOX, lambda e: self._set_opt("smooth_transition", e.IsChecked()))
        main.Add(self._transition_cb, 0, wx.LEFT, pad)
        main.AddSpacer(22)

        self.tab_app.SetSizer(main)


    def _build_diary_tab(self):
        main = wx.BoxSizer(wx.VERTICAL)
        pad = 16
        main.AddSpacer(pad)
        main.Add(self._title(self.tab_diary, "Diary"), 0, wx.LEFT, pad)
        main.AddSpacer(4)
        main.Add(self._sub(self.tab_diary, "Simple notes so you can remember what worked."), 0, wx.LEFT, pad)
        main.AddSpacer(10)

        self._diary_list = wx.TextCtrl(self.tab_diary, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE, size=(-1,280))
        self._diary_list.SetBackgroundColour(self.CARD)
        self._diary_list.SetForegroundColour(self.TXT)
        main.Add(self._diary_list, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, pad)
        self._refresh_diary_display()

        main.AddSpacer(10)
        self._usage_lbl = self._label(self.tab_diary, "Filter active today: 0 minutes")
        main.Add(self._usage_lbl, 0, wx.LEFT, pad)
        main.AddSpacer(10)

        self._diary_note = wx.TextCtrl(self.tab_diary, size=(-1,60), style=wx.TE_MULTILINE)
        self._diary_note.SetBackgroundColour(self.CARD)
        self._diary_note.SetForegroundColour(self.TXT)
        main.Add(self._diary_note, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, pad)
        main.AddSpacer(8)

        note_row = wx.BoxSizer(wx.HORIZONTAL)
        sev_lbl = wx.StaticText(self.tab_diary, label="Severity (1-10):")
        sev_lbl.SetForegroundColour(self.TXT)
        self._diary_sev = wx.SpinCtrl(self.tab_diary, min=1, max=10, value="5", size=(70,-1))
        add_note_btn = wx.Button(self.tab_diary, label="Add Entry", size=(100,28))
        add_note_btn.SetBackgroundColour(self.ACC)
        add_note_btn.SetForegroundColour(wx.Colour(255,255,255))
        add_note_btn.Bind(wx.EVT_BUTTON, self._add_diary_entry)
        clr_btn = wx.Button(self.tab_diary, label="Clear All", size=(90,28))
        clr_btn.SetBackgroundColour(wx.Colour(80,30,50))
        clr_btn.SetForegroundColour(wx.Colour(255,255,255))
        clr_btn.Bind(wx.EVT_BUTTON, self._clear_diary)
        note_row.Add(sev_lbl, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 6)
        note_row.Add(self._diary_sev, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 12)
        note_row.Add(add_note_btn, 0, wx.RIGHT, 8)
        note_row.Add(clr_btn, 0)
        main.Add(note_row, 0, wx.LEFT, pad)

        self.tab_diary.SetSizer(main)

    def _refresh_diary_display(self):
        entries = self.s.get("diary_entries", [])
        if not entries:
            self._diary_list.SetValue("No entries yet.")
            return
        lines = []
        for entry in reversed(entries[-50:]):
            etype = entry.get('type', 'manual')
            icon = "🆘" if etype == "emergency" else "📝"
            lines.append(f"{icon} [{entry.get('date', '?')}] Sev {entry.get('severity', '?')} — {entry.get('note', '')}")
        self._diary_list.SetValue("\n".join(lines))

    def _add_diary_entry(self, e):
        note = self._diary_note.GetValue().strip()
        entry = {"date": time.strftime("%Y-%m-%d %H:%M"), "severity": self._diary_sev.GetValue(),
                 "note": note or "(no note)", "type": "manual"}
        self.s.setdefault("diary_entries", []).append(entry)
        save_settings(self.s)
        self._diary_note.SetValue("")
        self._refresh_diary_display()

    def _clear_diary(self, e):
        if wx.MessageBox("Clear all diary entries?", "Clear Diary", wx.YES_NO|wx.ICON_WARNING, self) == wx.YES:
            self.s["diary_entries"] = []
            save_settings(self.s)
            self._refresh_diary_display()

    def _build_profiles_list(self):
        self._profiles_sizer.Clear(delete_windows=True)
        for name in list(self.s.get("profiles", {}).keys()):
            prof = self.s["profiles"][name]
            card = wx.Panel(self._profiles_panel)
            card.SetBackgroundColour(self.CARD)
            row = wx.BoxSizer(wx.HORIZONTAL)
            info = wx.BoxSizer(wx.VERTICAL)

            name_lbl = wx.StaticText(card, label=name)
            name_lbl.SetForegroundColour(self.PINK)
            name_lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            det_lbl = wx.StaticText(card, label=f"{FILTERS[prof['filter']]['name']} · Level {prof['intensity']}")
            det_lbl.SetForegroundColour(self.SUB)
            info.Add(name_lbl, 0)
            info.Add(det_lbl, 0)
            row.Add(info, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

            def mk_btn(text, handler):
                b = wx.Button(card, label=text, size=(-1, 24))
                b.SetBackgroundColour(self.ACC)
                b.SetForegroundColour(wx.Colour(255, 255, 255))
                b.Bind(wx.EVT_BUTTON, handler)
                return b

            for text, handler in [
                ("Load", lambda e, n=name: self._load_profile(n)),
                ("Overwrite", lambda e, n=name: self._overwrite_profile(n)),
                ("Duplicate", lambda e, n=name: self._duplicate_profile(n)),
                ("Rename", lambda e, n=name: self._rename_profile(n)),
                ("Delete", lambda e, n=name: self._delete_profile(n)),
            ]:
                row.Add(mk_btn(text, handler), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

            card.SetSizer(row)
            self._profiles_sizer.Add(card, 0, wx.EXPAND | wx.BOTTOM, 6)

        self._profiles_panel.Layout()
        self._profiles_panel.GetParent().FitInside()

    def _refresh_profiles_list(self):
        self._build_profiles_list()
        choices = ["(none)"] + list(self.s.get("profiles", {}).keys())
        self._default_profile_choice.Set(choices)
        cur = self.s.get("default_profile") or "(none)"
        self._default_profile_choice.SetSelection(choices.index(cur) if cur in choices else 0)

    def _load_profile(self, name):
        self.app._load_profile(name)
        self._sync_from_settings()

    def _overwrite_profile(self, name):
        if wx.MessageBox(f"Overwrite '{name}' with current settings?", "Overwrite Profile",
                         wx.YES_NO | wx.ICON_QUESTION, self) == wx.YES:
            self.app._save_profile(name)
            self._refresh_profiles_list()

    def _duplicate_profile(self, name):
        new_name = name + " Copy"
        count = 2
        while new_name in self.s.get("profiles", {}):
            new_name = f"{name} Copy {count}"
            count += 1
        self.s["profiles"][new_name] = dict(self.s["profiles"][name])
        save_settings(self.s)
        self._refresh_profiles_list()
        if self.app.tray:
            self.app.tray.update_menu()

    def _rename_profile(self, old_name):
        dlg = wx.TextEntryDialog(self, f"New name for '{old_name}':", "Rename Profile", old_name)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.GetValue().strip()
            if new_name and new_name != old_name and new_name not in self.s.get("profiles", {}):
                profiles = self.s.get("profiles", {})
                new_profiles = {}
                for k, v in profiles.items():
                    new_profiles[new_name if k == old_name else k] = v
                self.s["profiles"] = new_profiles
                if self.s.get("default_profile") == old_name:
                    self.s["default_profile"] = new_name
                save_settings(self.s)
                self._refresh_profiles_list()
                if self.app.tray:
                    self.app.tray.update_menu()
        dlg.Destroy()

    def _delete_profile(self, name):
        if wx.MessageBox(f"Delete profile '{name}'?", "Delete Profile",
                         wx.YES_NO | wx.ICON_WARNING, self) == wx.YES:
            self.s["profiles"].pop(name, None)
            if self.s.get("default_profile") == name:
                self.s["default_profile"] = ""
            save_settings(self.s)
            self._refresh_profiles_list()
            if self.app.tray:
                self.app.tray.update_menu()

    def _save_profile_ui(self, e):
        name = self._prof_name.GetValue().strip()
        if not name:
            return
        if name in self.s.get("profiles", {}):
            if wx.MessageBox(f"A profile named '{name}' exists. Overwrite it?", "Overwrite?",
                             wx.YES_NO | wx.ICON_QUESTION, self) != wx.YES:
                return
        self.app._save_profile(name)
        wx.MessageBox(f"Profile '{name}' saved!", "Saved", wx.OK | wx.ICON_INFORMATION, self)
        self._refresh_profiles_list()

    def _set_opt(self, key, val):
        self.s[key] = val
        if key == "global_on":
            for i in range(len(self.app.panels)):
                mon = self.s["per_monitor"].setdefault(str(i), {})
                mon["on"] = bool(val)
                mon.setdefault("filter", self.s["global_filter"])
                mon.setdefault("intensity", self.s["global_intensity"])
        if key == "startup":
            set_startup(val)
        save_settings(self.s)
        if key in ("use_per_monitor", "white_point_killer", "white_point_killer_boost", "transition_speed"):
            self.app._apply_all()
        if self.app.tray:
            self.app.tray.update_menu()

    def _on_default_profile(self, e):
        choice = self._default_profile_choice.GetStringSelection()
        self.s["default_profile"] = "" if choice == "(none)" else choice
        save_settings(self.s)

    def _apply_glass(self):
        try:
            self.SetTransparent(int(self.s.get("window_opacity", 220)))
        except Exception:
            pass

    def _on_glass_slider(self, e):
        self.s["window_opacity"] = int(self._glass_slider.GetValue())
        save_settings(self.s)
        wx.CallAfter(self._apply_glass)

    def _preview_theme(self, name):
        dlg = ThemePreviewDialog(self, name)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.s["theme_name"] = name
                save_settings(self.s)
                self._apply_theme_live(name)
        finally:
            dlg.Destroy()

    def _apply_theme_live(self, name):
        # wx native controls cannot all be recolored perfectly in-place.
        # Reopen the settings window using the chosen complete palette.
        save_settings(self.s)
        self.Hide()
        self.app.settings_win = SettingsWindow(self.app)
        self.app.settings_win.Show()
        self.app.settings_win.Raise()
        wx.CallLater(120, self.app.settings_win._apply_glass)

    def _save_current_setup(self):
        setup = {
            "filter": self.s.get("global_filter"),
            "intensity": self.s.get("global_intensity"),
            "global_on": self.s.get("global_on"),
            "white_point_killer": self.s.get("white_point_killer"),
            "use_per_monitor": self.s.get("use_per_monitor"),
            "per_monitor": self.s.get("per_monitor"),
            "mode_name": self.s.get("mode_name"),
            "theme_name": self.s.get("theme_name"),
        }
        self.s["my_setup"] = setup
        save_settings(self.s)
        self.app._show_status("My Setup saved ♡")

    def _restore_my_setup(self):
        setup = self.s.get("my_setup")
        if not setup:
            self.app._show_status("Save My Setup first")
            return
        for k, v in setup.items():
            self.s[k] = v
        save_settings(self.s)
        self.app._apply_all()
        self._sync_from_settings()
        self.app._show_status("My Setup restored ♡")

    def _on_theme_change(self, e):
        self.s["theme_name"] = self._theme_choice.GetStringSelection()
        save_settings(self.s)
        wx.MessageBox("Theme saved. Restart the app to refresh the whole window.", "Theme Saved",
                      wx.OK | wx.ICON_INFORMATION, self)

    def _on_intensity_slider(self, e):
        val = self._int_slider.GetValue()
        self._int_spin.SetValue(val)
        self.app._set_intensity_all(str(val))

    def _sync_from_settings(self):
        self._global_on_cb.SetValue(bool(self.s["global_on"]))
        self._wpk_cb.SetValue(bool(self.s.get("white_point_killer", False)))
        if hasattr(self, "_wpk_spin"):
            self._wpk_spin.SetValue(int(self.s.get("white_point_killer_boost", 3)))
        self._int_spin.SetValue(int(self.s["global_intensity"]))
        self._int_slider.SetValue(int(self.s["global_intensity"]))
        self._pm_cb.SetValue(bool(self.s.get("use_per_monitor", False)))
        if hasattr(self, "_startup_cb"):
            self._startup_cb.SetValue(get_startup())
        if hasattr(self, "_tray_cb"):
            self._tray_cb.SetValue(bool(self.s.get("tray", True)))
        if hasattr(self, "_transition_cb"):
            self._transition_cb.SetValue(bool(self.s.get("smooth_transition", True)))
        if hasattr(self, "_glass_slider"):
            self._glass_slider.SetValue(int(self.s.get("window_opacity", 220)))
        if hasattr(self, "_idle_spin"):
            self._idle_spin.SetValue(int(self.s.get("idle_threshold", 300)))
        if hasattr(self, "_boost_spin"):
            self._boost_spin.SetValue(int(self.s.get("idle_boost", 5)))
        if hasattr(self, "_em_spin"):
            self._em_spin.SetValue(int(self.s.get("emergency_restore_mins", 10)))
        vals = ["0.15", "0.25", "0.3", "0.4", "0.6"]
        cur = str(self.s.get("transition_speed", 0.25))
        if hasattr(self, "_trans_choice"):
            self._trans_choice.SetSelection(vals.index(cur) if cur in vals else 1)
        for k, btn in self._filter_rb.items():
            is_sel = (k == self.s["global_filter"])
            btn.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD if is_sel else wx.FONTWEIGHT_NORMAL))
            btn.Refresh()
        for idx, c in enumerate(self._monitor_controls):
            mon = self.s["per_monitor"].get(str(idx), {})
            c["enabled"].SetValue(mon.get("on", True))
            c["choice"].SetSelection(list(FILTERS.keys()).index(mon.get("filter", self.s["global_filter"])))
            c["spin"].SetValue(int(mon.get("intensity", self.s["global_intensity"])))
            en = self.s.get("use_per_monitor", False)
            c["enabled"].Enable(en); c["choice"].Enable(en); c["spin"].Enable(en)
        self._refresh_profiles_list()
        today = time.strftime("%Y-%m-%d")
        secs = int(self.s.get("usage_today_secs", 0)) if self.s.get("usage_today_date") == today else 0
        self._usage_lbl.SetLabel(f"Filter active today: {secs // 60} minutes")
        self._refresh_diary_display()

        # Home dashboard
        if hasattr(self, "_home_status"):
            fk = self.s.get("global_filter", "pink")
            lv = self.s.get("global_intensity", "8")
            mode = self.s.get("mode_name", "Everyday")
            self._home_status.SetLabel(f"{mode}  ·  {FILTERS.get(fk, FILTERS['pink'])['name']}  ·  Level {lv}")
            screens_on = 0
            for i in range(len(self.app.panels)):
                if self.s.get("use_per_monitor"):
                    screens_on += 1 if self.s["per_monitor"].get(str(i), {}).get("on", True) else 0
                else:
                    screens_on += 1 if self.s.get("global_on", True) else 0
            wpk = " · White Point Killer on" if self.s.get("white_point_killer") else ""
            pm = " · Per-monitor" if self.s.get("use_per_monitor") else ""
            self._home_substatus.SetLabel(f"{screens_on}/{len(self.app.panels)} screens protected{pm}{wpk}")
        if hasattr(self, "_int_value_label"):
            self._int_value_label.SetLabel(str(self.s.get("global_intensity", "8")) + " / 20")
        if hasattr(self, "_home_color_choice"):
            keys = list(FILTERS.keys())
            fk = self.s.get("global_filter", keys[0])
            if fk in keys:
                self._home_color_choice.SetSelection(keys.index(fk))
        if hasattr(self, "_side_state"):
            active = bool(self.s.get("global_on", True))
            self._side_state.SetLabel("●  Screen filter active" if active else "○  Screen filter paused")
            self._side_state.SetForegroundColour(self.PINK if active else self.SUB)




class ThemePreviewDialog(wx.Dialog):
    def __init__(self, parent, name):
        th = THEMES[name]
        super().__init__(parent, title=name + " · preview", size=(410, 315))
        self.name = name
        self.SetBackgroundColour(th["bg"])
        s = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label="DuskBloom Screen  🌷")
        title.SetForegroundColour(th["pink"])
        title.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        s.Add(title, 0, wx.LEFT | wx.TOP, 20)

        sub = wx.StaticText(self, label="a little preview before you commit.")
        sub.SetForegroundColour(th["sub"])
        s.Add(sub, 0, wx.LEFT | wx.TOP, 20)

        card = wx.Panel(self)
        card.SetBackgroundColour(th["card"])
        cs = wx.BoxSizer(wx.VERTICAL)
        ct = wx.StaticText(card, label="♡  Your comfort setup")
        ct.SetForegroundColour(th["pink"])
        ct.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        cs.Add(ct, 0, wx.ALL, 12)
        st = wx.StaticText(card, label="Reading · Dusty Rose · Level 8")
        st.SetForegroundColour(th["text"])
        cs.Add(st, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        row = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Reading", "Night", "Cozy"]:
            b = wx.Button(card, label=label, size=(90, 30))
            b.SetBackgroundColour(th["accent"] if label == "Reading" else th["card"])
            b.SetForegroundColour(th["text"])
            row.Add(b, 0, wx.RIGHT, 6)
        cs.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        card.SetSizer(cs)
        s.Add(card, 1, wx.ALL | wx.EXPAND, 20)

        br = wx.BoxSizer(wx.HORIZONTAL)
        cancel = wx.Button(self, wx.ID_CANCEL, label="Keep current")
        applyb = wx.Button(self, wx.ID_OK, label="♡ Use " + name)
        applyb.SetBackgroundColour(th["accent"]); applyb.SetForegroundColour(th["text"])
        br.Add(cancel, 0, wx.RIGHT, 8); br.Add(applyb, 0)
        s.Add(br, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 20)
        self.SetSizer(s)
        self.SetPosition((140, 140))


# ── Main app ───────────────────────────────────────────────────────────────────
class FilterApp(wx.App):

    def _startup_mark(self, text):
        try:
            d = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "DuskBloom", "DuskBloomScreen")
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "startup.txt"), "a", encoding="utf-8") as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "  " + text + "\n")
        except Exception:
            pass

    def OnInit(self):
        self._startup_mark("START v" + APP_VERSION)
        self.s = load_settings()
        self._startup_mark("settings loaded")
        if self.s.get("theme_name") not in THEMES:
            self.s["theme_name"] = "Cozy Pink"
            save_settings(self.s)
        self.panels = []
        self.mon_info = get_monitors()
        self.tray = None
        self._go = True
        self._idle_last_pos = None
        self._idle_secs = 0
        self._emergency_on = False
        self._pre_emergency = None

        self._startup_mark("monitors found: " + str(len(self.mon_info)))
        for x, y, w, h in self.mon_info:
            self.panels.append(Panel(x, y, w, h))
        self._startup_mark("overlays created")

        for i in range(len(self.panels)):
            k = str(i)
            if k not in self.s["per_monitor"]:
                self.s["per_monitor"][k] = {
                    "filter": self.s["global_filter"],
                    "intensity": self.s["global_intensity"],
                    "on": self.s["global_on"],
                }

        self.mini_popup = MiniPopup()
        self._startup_mark("mini popup created")
        self.settings_win = SettingsWindow(self)
        self._startup_mark("settings window created")
        self.mini_controller = MiniController(self)
        self._startup_mark("mini controller created")

        self._register_hotkeys()
        self._peek_active = False
        threading.Thread(target=self._peek_loop, daemon=True).start()
        threading.Thread(target=self._push_loop, daemon=True).start()
        threading.Thread(target=self._idle_loop, daemon=True).start()
        threading.Thread(target=self._run_tray, daemon=True).start()

        wx.CallLater(500, self._fade_in_startup)

        self._usage_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_usage_tick, self._usage_timer)
        self._usage_timer.Start(60000)

        dp = self.s.get("default_profile")
        if dp and dp in self.s.get("profiles", {}):
            wx.CallLater(1200, self._load_profile, dp)

        # Center integration is intentionally delayed until the working
        # overlay + settings UI are fully initialized.
        wx.CallLater(1500, self._safe_start_duskbloom_bridge)
        self._startup_mark("READY")
        return True

    def _effective_alpha(self, fk, lv):
        alpha = get_alpha(fk, lv)
        if self.s.get("white_point_killer", False) and fk in ("warm_white", "pink", "pink_blackout", "bluelight", "amber"):
            alpha = min(252, alpha + int(self.s.get("white_point_killer_boost", 3)) * 6)
        elif self.s.get("white_point_killer", False):
            alpha = min(252, alpha + int(self.s.get("white_point_killer_boost", 3)) * 3)
        return alpha

    def _apply_mode(self, name):
        cfg = MODES.get(name)
        if not cfg:
            return
        fk, lv, wpk = cfg
        self.s["mode_name"] = name
        self.s["white_point_killer"] = bool(wpk)
        self._set_all_state_atomic(fk, lv)
        self._show_status("Mode: " + name)

    def _match_all_monitors(self):
        self.s["use_per_monitor"] = True
        for i in range(len(self.panels)):
            self.s["per_monitor"][str(i)] = {
                "filter": self.s["global_filter"],
                "intensity": self.s["global_intensity"],
                "on": self.s["global_on"],
            }
        self._apply_all()
        self._show_status("Home settings applied to all screens")

    def _darken_side_monitors(self):
        self.s["use_per_monitor"] = True
        for i in range(len(self.panels)):
            if i == 1:
                self.s["per_monitor"][str(i)] = {
                    "filter": self.s["global_filter"],
                    "intensity": self.s["global_intensity"],
                    "on": True,
                }
            else:
                self.s["per_monitor"][str(i)] = {
                    "filter": "obsidian", "intensity": "14", "on": True,
                }
        self._apply_all()
        self._show_status("Side screens darkened")

    def _show_mini_controller(self):
        self.mini_controller.show_safe()

    def _peek_start(self):
        if getattr(self, "_peek_active", False):
            return
        self._peek_active = True
        for p in self.panels:
            p.hide()

    def _peek_end(self):
        if not getattr(self, "_peek_active", False):
            return
        self._peek_active = False
        self._apply_all()

    def _peek_loop(self):
        # Hold Ctrl+Shift+P to reveal the unfiltered screens.
        last = False
        while self._go:
            down = bool(u32.GetAsyncKeyState(0x11) & 0x8000) and \
                   bool(u32.GetAsyncKeyState(0x10) & 0x8000) and \
                   bool(u32.GetAsyncKeyState(0x50) & 0x8000)
            if down and not last:
                wx.CallAfter(self._peek_start)
            elif last and not down:
                wx.CallAfter(self._peek_end)
            last = down
            time.sleep(0.08)

    def _safe_start_duskbloom_bridge(self):
        try:
            self._mellow_bridge_start()
        except BaseException:
            # DuskBloom Center integration must never take Screen down.
            pass

    def _mellow_bridge_start(self):
        # DuskBloom-native bridge path. Existing Mellow bridge files are copied
        # forward once when useful, so the rename does not throw away state.
        os.makedirs(MELLOW_BRIDGE_DIR, exist_ok=True)
        try:
            if os.path.isdir(LEGACY_MELLOW_BRIDGE_DIR):
                for legacy_name in ("state.json",):
                    oldp = os.path.join(LEGACY_MELLOW_BRIDGE_DIR, legacy_name)
                    newp = os.path.join(MELLOW_BRIDGE_DIR, legacy_name)
                    if os.path.exists(oldp) and not os.path.exists(newp):
                        shutil.copy2(oldp, newp)
        except BaseException:
            # Branding/Center migration is optional and must never block startup.
            pass
        _atomic_json_write(MELLOW_MANIFEST_FILE, {
            "app": "DuskBloom Screen",
            "version": APP_VERSION,
            "protocol": 1,
            "state_file": MELLOW_STATE_FILE,
            "command_file": MELLOW_COMMAND_FILE,
            "commands": [
                "set_filter", "set_intensity", "set_mode", "apply_preset",
                "set_enabled", "pause", "match_all", "darken_sides",
                "set_monitor_filter", "set_monitor_intensity", "set_monitor_enabled", "set_menu_theme"
            ]
        })
        self._mellow_last_command_id = None
        self._mellow_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._mellow_bridge_tick, self._mellow_timer)
        self._mellow_timer.Start(2000)
        self._mellow_publish_state()

    def _mellow_publish_state(self):
        monitors = []
        for i in range(len(self.panels)):
            ms = self.s["per_monitor"].get(str(i), {})
            monitors.append({
                "index": i,
                "enabled": ms.get("on", self.s.get("global_on", True)),
                "filter": ms.get("filter", self.s.get("global_filter", "pink")),
                "intensity": int(ms.get("intensity", self.s.get("global_intensity", "8")))
            })
        _atomic_json_write(MELLOW_STATE_FILE, {
            "app": "DuskBloom Screen",
            "version": APP_VERSION,
            "running": True,
            "updated": time.time(),
            "enabled": bool(self.s.get("global_on", True)),
            "filter": self.s.get("global_filter", "pink"),
            "filter_name": FILTERS.get(self.s.get("global_filter", "pink"), FILTERS["pink"])["name"],
            "filter_rgb": list(get_color(self.s.get("global_filter", "pink"))),
            "intensity": int(self.s.get("global_intensity", "8")),
            "mode": self.s.get("mode_name", "Everyday"),
            "white_point_killer": bool(self.s.get("white_point_killer", False)),
            "per_monitor": bool(self.s.get("use_per_monitor", False)),
            "paused_until": self.s.get("paused_until", 0),
            "monitors": monitors
        })

    def _mellow_bridge_tick(self, evt=None):
        self._mellow_publish_state()
        if not os.path.exists(MELLOW_COMMAND_FILE):
            return
        try:
            with open(MELLOW_COMMAND_FILE, "r", encoding="utf-8") as f:
                msg = json.load(f)
            cid = msg.get("id")
            if cid is not None and cid == self._mellow_last_command_id:
                return
            self._mellow_last_command_id = cid
            cmd = msg.get("command", "")
            val = msg.get("value")
            idx = int(msg.get("monitor", 0))

            if cmd == "set_filter" and val in FILTERS:
                self._set_filter_all(val)
            elif cmd == "set_intensity":
                self._set_intensity_all(str(max(1, min(20, int(val)))))
            elif cmd == "set_mode" and val in MODES:
                self._apply_mode(val)
            elif cmd == "apply_preset" and val in PRESETS:
                self._apply_preset(val)
            elif cmd == "set_menu_theme" and val in THEMES:
                self.s["theme_name"] = val
                save_settings(self.s)
                if self.settings_win and self.settings_win.IsShown():
                    self.settings_win._apply_theme_live(val)
            elif cmd == "set_enabled":
                self._set_global_on(bool(val))
            elif cmd == "pause":
                self._pause_for_minutes(max(1, int(val or 10)))
            elif cmd == "match_all":
                self._match_all_monitors()
            elif cmd == "darken_sides":
                self._darken_side_monitors()
            elif cmd == "set_monitor_filter" and val in FILTERS and 0 <= idx < len(self.panels):
                self._set_monitor_filter(idx, val)
            elif cmd == "set_monitor_intensity" and 0 <= idx < len(self.panels):
                self._set_monitor_intensity(idx, max(1, min(20, int(val))))
            elif cmd == "set_monitor_enabled" and 0 <= idx < len(self.panels):
                self._set_monitor_on(idx, bool(val))
        except Exception:
            pass

    def _register_hotkeys(self):
        hk = self.s.get("hotkeys", DEFAULT_SETTINGS["hotkeys"])
        actions = ["toggle", "emergency", "intensity_up", "intensity_down", "cycle_filter"]
        for i, name in enumerate(actions, start=1):
            h = hk.get(name, DEFAULT_SETTINGS["hotkeys"].get(name, {}))
            try:
                u32.RegisterHotKey(None, i, h["mod"], h["vk"])
            except Exception:
                pass
        threading.Thread(target=self._hk_loop, daemon=True).start()

    def _unregister_hotkeys(self):
        for i in range(1, 6):
            try:
                u32.UnregisterHotKey(None, i)
            except Exception:
                pass

    def _hk_loop(self):
        msg = ctypes.wintypes.MSG()
        while True:
            r = u32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if r == 0 or r == -1:
                break
            if msg.message == 0x0312:
                hid = msg.wParam
                if hid == 1: wx.CallAfter(self._toggle_all)
                elif hid == 2: wx.CallAfter(self._emergency)
                elif hid == 3: wx.CallAfter(self._intensity_up)
                elif hid == 4: wx.CallAfter(self._intensity_down)
                elif hid == 5: wx.CallAfter(self._cycle_filter)

    def _push_loop(self):
        _flush_counter = 0
        while self._go:
            if self.s.get("paused_until", 0) and time.time() >= self.s.get("paused_until", 0):
                wx.CallAfter(self._resume_now)
            for p in self.panels:
                p.push()
            _flush_counter += 1
            if _flush_counter >= 60 and self.tray:
                _flush_toasts(self.tray)
                _flush_counter = 0
            time.sleep(0.75)

    def _idle_loop(self):
        while self._go:
            time.sleep(5)
            pt = ctypes.wintypes.POINT()
            u32.GetCursorPos(ctypes.byref(pt))
            cur = (pt.x, pt.y)
            if cur == self._idle_last_pos:
                self._idle_secs += 5
            else:
                if self._idle_secs >= self.s.get("idle_threshold", 300):
                    wx.CallAfter(self._unapply_idle_boost)
                self._idle_secs = 0
            self._idle_last_pos = cur
            if self._idle_secs >= self.s.get("idle_threshold", 300):
                wx.CallAfter(self._apply_idle_boost)

    def _on_usage_tick(self, e):
        today = time.strftime("%Y-%m-%d")
        if self.s.get("usage_today_date") != today:
            self.s["usage_today_date"] = today
            self.s["usage_today_secs"] = 0
        if self.s.get("global_on") or self.s.get("use_per_monitor"):
            self.s["usage_today_secs"] = int(self.s.get("usage_today_secs", 0)) + 60
            save_settings(self.s)
            if self.settings_win:
                self.settings_win._sync_from_settings()

    def _apply_idle_boost(self):
        if self._emergency_on:
            return
        boost = self.s.get("idle_boost", 5)
        for i, p in enumerate(self.panels):
            mon = self.s["per_monitor"].get(str(i), {})
            if self.s.get("use_per_monitor"):
                fk = mon.get("filter", self.s["global_filter"])
                lv = int(mon.get("intensity", self.s["global_intensity"]))
                on = mon.get("on", True)
            else:
                fk = self.s["global_filter"]
                lv = int(self.s["global_intensity"])
                on = self.s["global_on"]
            if on:
                boosted = min(20, lv + boost)
                p.set_target(get_color(fk), self._effective_alpha(fk, str(boosted)))
                p.show_now()
        self._start_transition()

    def _unapply_idle_boost(self):
        self._apply_all()

    def _fade_in_startup(self):
        if not self.s.get("global_on", True) and not self.s.get("use_per_monitor", False):
            return
        for i, p in enumerate(self.panels):
            ms = self.s["per_monitor"].get(str(i), {})
            if self.s.get("use_per_monitor"):
                on = ms.get("on", True)
                fk = ms.get("filter", self.s["global_filter"])
                lv = ms.get("intensity", self.s["global_intensity"])
            else:
                on = self.s["global_on"]
                fk = self.s["global_filter"]
                lv = self.s["global_intensity"]
            if on:
                p._cur_alpha = 0.0
                p._target_alpha = self._effective_alpha(fk, lv)
                p.set_target(get_color(fk), self._effective_alpha(fk, lv))
                p.show_now()
        speed = self.s.get("transition_speed", 0.25) * 3
        def do_fade(evt=None):
            results = [p.step_transition(speed) for p in self.panels if p.IsShown()]
            still = any(results)
            if not still:
                self._fade_timer.Stop()
        self._fade_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, do_fade, self._fade_timer)
        self._fade_timer.Start(16)

    def _apply_all(self):
        if getattr(self, "_peek_active", False):
            return
        if self.s.get("paused_until", 0) > time.time():
            for p in self.panels:
                p.hide()
            save_settings(self.s)
            if self.tray:
                self.tray.update_menu()
            return
        for i, p in enumerate(self.panels):
            ms = self.s["per_monitor"].get(str(i), {})
            if self.s.get("use_per_monitor"):
                on = ms.get("on", True)
                fk = ms.get("filter", self.s["global_filter"])
                lv = ms.get("intensity", self.s["global_intensity"])
            else:
                on = self.s["global_on"]
                fk = self.s["global_filter"]
                lv = self.s["global_intensity"]
            if on:
                final_alpha = self._effective_alpha(fk, lv)
                p.set_target(get_color(fk), final_alpha)
                p.show_now()
                # Apply the requested result now. This avoids the transition
                # timer becoming a single point of failure for normal controls.
                p._cur_alpha = float(final_alpha)
                p.SetTransparent(int(final_alpha))
                p.Refresh()
                p.Update()
                p.push()
            else:
                p.hide()
        save_settings(self.s)
        if self.settings_win:
            self.settings_win._sync_from_settings()
        if self.tray:
            self.tray.update_menu()
        if hasattr(self, "_mellow_timer"):
            self._mellow_publish_state()

    def _start_transition(self):
        if hasattr(self, "_trans_timer") and self._trans_timer.IsRunning():
            return
        speed = self.s.get("transition_speed", 0.25)
        def step(evt=None):
            results = [p.step_transition(speed) for p in self.panels if p.IsShown()]
            still = any(results)
            if not still:
                self._trans_timer.Stop()
        self._trans_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, step, self._trans_timer)
        self._trans_timer.Start(16)

    def _set_all_state_atomic(self, fk, lv):
        """Change color + intensity as one visual transaction.

        Presets used to render once after the color change and again after the
        intensity change. On bright displays that intermediate frame looked
        like a white/bright flash. This updates all state first and paints once.
        """
        lv = str(max(1, min(20, int(lv))))
        self.s["global_filter"] = fk
        self.s["global_intensity"] = lv
        for i in range(len(self.panels)):
            mon = self.s["per_monitor"].setdefault(str(i), {})
            mon["filter"] = fk
            mon["intensity"] = lv
            mon.setdefault("on", self.s.get("global_on", True))
        self._apply_all()

    def _set_global_on(self, enabled):
        self.s["global_on"] = bool(enabled)
        # Home is the all-screen controller, including when per-monitor mode is active.
        for i in range(len(self.panels)):
            mon = self.s["per_monitor"].setdefault(str(i), {})
            mon["on"] = self.s["global_on"]
            mon.setdefault("filter", self.s["global_filter"])
            mon.setdefault("intensity", self.s["global_intensity"])
        self._apply_all()
        self._show_status()

    def _toggle_all(self):
        self._set_global_on(not self.s["global_on"])

    def _set_monitor_on(self, idx, enabled):
        ms = self.s["per_monitor"].setdefault(str(idx), {})
        ms["on"] = bool(enabled)
        self.s["use_per_monitor"] = True
        self._apply_all()
        self._show_status(f"Monitor {idx + 1}: {'ON' if enabled else 'OFF'}")

    def _set_monitor_filter(self, idx, fk):
        ms = self.s["per_monitor"].setdefault(str(idx), {})
        ms["filter"] = fk
        self.s["use_per_monitor"] = True
        self._apply_all()
        self._show_status(f"Monitor {idx + 1}: {FILTERS[fk]['name']}")

    def _set_monitor_intensity(self, idx, lv):
        ms = self.s["per_monitor"].setdefault(str(idx), {})
        ms["intensity"] = str(lv)
        self.s["use_per_monitor"] = True
        self._apply_all()
        self._show_status(f"Monitor {idx + 1}: Lv{lv}")

    def _emergency(self):
        if not self._emergency_on:
            self._emergency_on = True
            self.s.setdefault("diary_entries", []).append({
                "date": time.strftime("%Y-%m-%d %H:%M"),
                "severity": 10,
                "note": "Emergency mode activated",
                "type": "emergency",
            })
            save_settings(self.s)
            self._pre_emergency = {
                "filter": self.s["global_filter"],
                "intensity": self.s["global_intensity"],
                "on": self.s["global_on"],
                "use_per_monitor": self.s["use_per_monitor"],
                "per_monitor": json.loads(json.dumps(self.s["per_monitor"])),
                "white_point_killer": self.s.get("white_point_killer", False),
            }
            self.s["global_filter"] = "obsidian"
            self.s["global_intensity"] = "20"
            self.s["global_on"] = True
            self.s["use_per_monitor"] = False
            self.s["white_point_killer"] = True
            self._apply_all()
            self._show_status("🆘 Emergency Mode")
            mins = self.s.get("emergency_restore_mins", 10)
            wx.CallLater(int(mins * 60 * 1000), self._restore_emergency)
        else:
            self._restore_emergency()

    def _restore_emergency(self):
        if not self._emergency_on:
            return
        self._emergency_on = False
        if self._pre_emergency:
            self.s["global_filter"] = self._pre_emergency["filter"]
            self.s["global_intensity"] = self._pre_emergency["intensity"]
            self.s["global_on"] = self._pre_emergency["on"]
            self.s["use_per_monitor"] = self._pre_emergency.get("use_per_monitor", False)
            self.s["per_monitor"] = self._pre_emergency.get("per_monitor", self.s["per_monitor"])
            self.s["white_point_killer"] = self._pre_emergency.get("white_point_killer", self.s.get("white_point_killer", False))
        self._apply_all()
        self._show_status("Emergency restored")
        save_settings(self.s)

    def _set_filter_all(self, fk):
        self.s["global_filter"] = fk
        # Home controls are intentionally ALL-SCREENS controls.
        for i in range(len(self.panels)):
            mon = self.s["per_monitor"].setdefault(str(i), {})
            mon["filter"] = fk
            mon.setdefault("intensity", self.s["global_intensity"])
            mon.setdefault("on", self.s["global_on"])
        if self.s["global_on"] or self.s.get("use_per_monitor"):
            self._apply_all()
        self._show_status()
        save_settings(self.s)

    def _set_intensity_all(self, lv):
        self.s["global_intensity"] = lv
        # Home controls are intentionally ALL-SCREENS controls.
        for i in range(len(self.panels)):
            mon = self.s["per_monitor"].setdefault(str(i), {})
            mon["intensity"] = lv
            mon.setdefault("filter", self.s["global_filter"])
            mon.setdefault("on", self.s["global_on"])
        if self.s["global_on"] or self.s.get("use_per_monitor"):
            self._apply_all()
        self._show_status()
        save_settings(self.s)

    def _intensity_up(self):
        self._set_intensity_all(str(min(20, int(self.s["global_intensity"]) + 1)))

    def _intensity_down(self):
        self._set_intensity_all(str(max(1, int(self.s["global_intensity"]) - 1)))

    def _cycle_filter(self):
        keys = list(FILTERS.keys())
        self._set_filter_all(keys[(keys.index(self.s["global_filter"]) + 1) % len(keys)])

    def _load_profile(self, name):
        p = self.s["profiles"].get(name)
        if p:
            self._set_filter_all(p["filter"])
            self._set_intensity_all(p["intensity"])
            self._show_status(f"Profile: {name}")

    def _save_profile(self, name):
        self.s["profiles"][name] = {"filter": self.s["global_filter"], "intensity": self.s["global_intensity"]}
        save_settings(self.s)
        if self.tray:
            self.tray.update_menu()

    def _apply_preset(self, name):
        preset = PRESETS.get(name, {})
        if not preset:
            return
        if "pause" in preset:
            self._pause_for_minutes(int(preset["pause"]))
            return
        self.s["white_point_killer"] = bool(preset.get("white_point_killer", self.s.get("white_point_killer", False)))
        self._set_all_state_atomic(preset["filter"], preset["intensity"])
        self._show_status(f"Preset: {name}")

    def _pause_for_minutes(self, minutes):
        self.s["paused_until"] = time.time() + (minutes * 60)
        for p in self.panels:
            p.hide()
        save_settings(self.s)
        self._show_status(f"Paused for {minutes} min")
        if self.tray:
            self.tray.update_menu()

    def _resume_now(self):
        self.s["paused_until"] = 0
        self._apply_all()
        self._show_status("Filter resumed")
        if self.tray:
            self.tray.update_menu()

    def _show_status(self, msg=None):
        if msg is None:
            fk = self.s["global_filter"]
            lv = self.s["global_intensity"]
            mode = "PER-MONITOR" if self.s.get("use_per_monitor") else ("ON" if self.s["global_on"] else "OFF")
            extra = " · White Killer" if self.s.get("white_point_killer") else ""
            em = " 🆘" if self._emergency_on else ""
            msg = f"{FILTERS[fk]['name']}  Lv{lv}  {mode}{extra}{em}"
        _toast("DuskBloom Screen", msg)

    def _open_settings(self):
        self.settings_win._sync_from_settings()
        self.settings_win.Show()
        self.settings_win.Raise()
        wx.CallLater(120, self.settings_win._apply_glass)

    def _run_tray(self):
        self.tray = pystray.Icon("mf")
        self.tray.icon = mkicon()
        self.tray.title = "DuskBloom Screen"
        self.tray.menu = self._make_menu()

        def _on_click(icon, button, pressed):
            import pystray as _pystray
            if pressed and button == _pystray.mouse.Button.left:
                wx.CallAfter(self.mini_popup.show_near_tray, self.s)
        self.tray._on_click = _on_click
        self.tray.run()

    def _make_menu(self):
        def pause_toggle(i, it):
            if self.s.get("paused_until", 0) > time.time():
                wx.CallAfter(self._resume_now)
            else:
                wx.CallAfter(self._pause_for_minutes, 5)

        pause_label = lambda i: "Resume" if self.s.get("paused_until", 0) > time.time() else "Pause 5 min"

        return pystray.Menu(
            pystray.MenuItem("DuskBloom Screen 🌷", None, enabled=False),
            pystray.MenuItem(lambda i: f"{FILTERS[self.s['global_filter']]['name']} · Lv {self.s['global_intensity']}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Toggle Filter", lambda i, it: wx.CallAfter(self._toggle_all), default=True),
            pystray.MenuItem("Emergency Mode", lambda i, it: wx.CallAfter(self._emergency)),
            pystray.MenuItem(pause_label, pause_toggle),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Migraine Preset", lambda i, it: wx.CallAfter(self._apply_preset, "Migraine")),
            pystray.MenuItem("Reading Preset", lambda i, it: wx.CallAfter(self._apply_preset, "Reading")),
            pystray.MenuItem("Night Preset", lambda i, it: wx.CallAfter(self._apply_preset, "Night")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Mini Mode", lambda i, it: wx.CallAfter(self._show_mini_controller)),
            pystray.MenuItem("Open DuskBloom Screen…", lambda i, it: wx.CallAfter(self._open_settings)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit_app),
        )

    def _quit_app(self, i=None, it=None):
        self._go = False
        self._unregister_hotkeys()
        self.s["startup"] = get_startup()
        save_settings(self.s)
        wx.CallAfter(self.ExitMainLoop)
        if self.tray:
            self.tray.stop()

if __name__ == "__main__":
    try:
        app = FilterApp()
        app.MainLoop()
    except Exception:
        import traceback
        err = traceback.format_exc()
        try:
            log_dir = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "DuskBloom", "DuskBloomScreen")
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "crash.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(err)
            ctypes.windll.user32.MessageBoxW(
                0,
                "DuskBloom Screen could not start.\n\nA crash report was saved to:\n" + log_path,
                "DuskBloom Screen",
                0x10
            )
        except Exception:
            pass
