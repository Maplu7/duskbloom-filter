#!/usr/bin/env python3
"""
Migraine Filter for Windows
Whole-screen migraine-friendly overlay with:
- Adaptive brightness
- Flash protection
- Smooth auto fade
- Reading / Media / Night modes
- Sleep/wake recovery
- Startup safety
- Global keyboard shortcuts
- Start with Windows
- Temporary Reveal
- Monitor Memory
- 23 muted color filters
- Gaming Safe Mode (static overlay; no screen capture)

Requires:
    pip install pillow pystray keyboard mss pywin32
"""

import ctypes
import ctypes.wintypes
import json
import os
import sys
import time
import threading
from pathlib import Path
import tkinter as tk

try:
    import mss
    import keyboard
    import pystray
    from PIL import Image, ImageDraw
    import win32api
    import win32con
    import win32gui
except ImportError as e:
    raise SystemExit(
        "Missing dependency. Run:\n"
        "pip install pillow pystray keyboard mss pywin32\n\n"
        f"Details: {e}"
    )

APP_NAME = "Migraine Filter"
SETTINGS_DIR = Path(os.getenv("APPDATA", Path.home())) / "MigraineFilter"
SETTINGS_PATH = SETTINGS_DIR / "settings.json"
STARTUP_DIR = Path(os.getenv("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup"
STARTUP_CMD = STARTUP_DIR / "MigraineFilter.cmd"

FILTERS = {
    "pink_blackout": {"name": "Pink Blackout", "rgb": (214, 126, 156)},
    "pink": {"name": "Pink", "rgb": (235, 154, 184)},
    "dark_pink": {"name": "Dark Pink", "rgb": (155, 75, 108)},
    "rose_dim": {"name": "Rose Dim", "rgb": (190, 112, 135)},
    "purple": {"name": "Lavender", "rgb": (143, 116, 166)},
    "amber": {"name": "Amber", "rgb": (214, 153, 73)},
    "green": {"name": "Forest Green", "rgb": (70, 105, 76)},
    "warm_white": {"name": "Warm White", "rgb": (255, 224, 180)},
    "deep_red": {"name": "Deep Red", "rgb": (105, 28, 36)},
    "bluelight": {"name": "Blue Light", "rgb": (78, 111, 148)},
    "dark": {"name": "Dark Dimmer", "rgb": (20, 20, 20)},
    "midnight": {"name": "Midnight", "rgb": (14, 12, 22)},
    "obsidian": {"name": "Obsidian", "rgb": (8, 8, 12)},
    "dusty_rose": {"name": "Dusty Rose", "rgb": (166, 108, 126)},
    "peach": {"name": "Peach", "rgb": (222, 157, 126)},
    "sepia": {"name": "Sepia", "rgb": (150, 121, 86)},
    "sage": {"name": "Sage", "rgb": (116, 139, 112)},
    "soft_cyan": {"name": "Soft Cyan", "rgb": (112, 151, 153)},
    "mauve": {"name": "Mauve", "rgb": (130, 96, 125)},
    "smoke": {"name": "Smoke", "rgb": (92, 96, 103)},
    "cocoa": {"name": "Cocoa", "rgb": (76, 55, 50)},
    "navy": {"name": "Navy", "rgb": (35, 48, 75)},
    "burgundy": {"name": "Burgundy", "rgb": (82, 34, 48)},
}

MODES = {
    "Normal": {"filter": "pink_blackout", "intensity": 7, "compression": 1},
    "Reading": {"filter": "warm_white", "intensity": 8, "compression": 2},
    "Media": {"filter": "dark", "intensity": 5, "compression": 1},
    "Night": {"filter": "midnight", "intensity": 12, "compression": 2},
}

DEFAULTS = {
    "enabled": True,
    "mode": "Normal",
    "filter": "pink_blackout",
    "intensity": 7,
    "adaptive_brightness": True,
    "adaptive_sensitivity": 0.65,
    "flash_protection": True,
    "flash_strength": "Normal",
    "brightness_compression": 1,
    "auto_fade": True,
    "fade_speed": 0.10,
    "launch_at_login": False,
    "startup_safety": True,
    "temporary_reveal": False,
    "monitor_memory": True,
    "monitor_profiles": {},
    "gaming_safe_mode": False,
}

def load_settings():
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            for k, v in DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULTS)

def save_settings(s):
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(s, indent=2), encoding="utf-8")

def set_startup(enabled):
    STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    if enabled:
        script = Path(__file__).resolve()
        STARTUP_CMD.write_text(
            f'@echo off\nstart "" "{sys.executable}" "{script}"\n',
            encoding="utf-8",
        )
    else:
        try:
            STARTUP_CMD.unlink()
        except FileNotFoundError:
            pass

def monitor_rects():
    mons = []
    def cb(hmon, hdc, rect_ptr, data):
        r = rect_ptr.contents
        mons.append((r.left, r.top, r.right-r.left, r.bottom-r.top))
        return 1
    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
        ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double
    )
    ctypes.windll.user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(cb), 0)
    return mons

def monitor_info():
    """Return stable-ish monitor IDs and rectangles."""
    items = []
    def cb(hmon, hdc, rect_ptr, data):
        r = rect_ptr.contents
        info = ctypes.wintypes.MONITORINFOEXW()
        info.cbSize = ctypes.sizeof(info)
        try:
            ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))
            name = str(info.szDevice)
        except Exception:
            name = ""
        rect = (r.left, r.top, r.right-r.left, r.bottom-r.top)
        sid = name or f"screen-{rect[0]}-{rect[1]}-{rect[2]}x{rect[3]}"
        items.append((sid, rect))
        return 1
    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double
    )
    ctypes.windll.user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(cb), 0)
    return items


class Overlay:
    def __init__(self, root, rect):
        self.win = tk.Toplevel(root)
        x, y, w, h = rect
        self.win.overrideredirect(True)
        self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.0)
        self.win.configure(bg="#000000")
        self.win.update_idletasks()

        hwnd = self.win.winfo_id()
        exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        exstyle |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle)

        self.alpha = 0.0
        self.target = 0.0

    def set_color(self, rgb):
        self.win.configure(bg="#%02x%02x%02x" % rgb)

    def set_target(self, alpha):
        self.target = max(0.0, min(0.94, alpha))

    def tick(self, smooth=True, speed=.10):
        if smooth:
            self.alpha += (self.target - self.alpha) * max(.02, min(.5, speed))
            if abs(self.target - self.alpha) < .002:
                self.alpha = self.target
        else:
            self.alpha = self.target
        self.win.attributes("-alpha", self.alpha)
        self.win.lift()

class App:
    def __init__(self):
        self.settings = load_settings()
        self.root = tk.Tk()
        self.root.withdraw()
        self.overlays = []
        self.last_luma = None
        self.flash_until = 0
        self.last_sample = 0
        self.last_monitor_check = 0
        self.start_time = time.time()
        self.last_tick = time.time()
        self.monitor_items = []

        # Startup safety: begin with a mild overlay, then restore saved state.
        self.startup_safe_until = time.time() + 2.5 if self.settings["startup_safety"] else 0

        self.rebuild_overlays()
        self.setup_hotkeys()
        self.setup_tray()
        self.root.after(30, self.tick)

    def rebuild_overlays(self):
        for o in self.overlays:
            try: o.win.destroy()
            except Exception: pass
        self.monitor_items = monitor_info()
        self.overlays = [Overlay(self.root, rect) for _, rect in self.monitor_items]

    def sample_luminance(self):
        try:
            with mss.mss() as sct:
                mon = sct.monitors[0]
                shot = sct.grab(mon)
                img = Image.frombytes("RGB", shot.size, shot.rgb).resize((32, 18))
                px = list(img.getdata())
                return sum((0.2126*r + 0.7152*g + 0.0722*b) for r,g,b in px) / (255*len(px))
        except Exception:
            return 0.5

    def base_alpha(self):
        level = max(1, min(20, int(self.settings["intensity"])))
        # useful 1..20 curve, capped below total blackout
        return 0.025 + ((level - 1) / 19.0) ** 1.35 * 0.76

    def effective_alpha(self, luma):
        if not self.settings["enabled"] or self.settings.get("temporary_reveal", False):
            return 0.0

        alpha = self.base_alpha()

        if self.settings.get("gaming_safe_mode", False):
            # Static overlay only: no screen capture/adaptive/flash analysis.
            return min(.92, min(alpha, .18) if time.time() < self.startup_safe_until else alpha)

        comp = int(self.settings.get("brightness_compression", 1))
        if comp:
            alpha += max(0, luma - 0.50) * (0.10 if comp == 1 else 0.18)

        if self.settings.get("adaptive_brightness"):
            sens = float(self.settings.get("adaptive_sensitivity", .65))
            alpha += max(0, luma - 0.38) * 0.30 * sens

        if time.time() < self.flash_until:
            extra = {"Gentle": .08, "Normal": .15, "Strong": .24}.get(
                self.settings.get("flash_strength"), .15
            )
            alpha += extra

        if time.time() < self.startup_safe_until:
            alpha = min(alpha, .18)

        return min(.92, alpha)

    def apply_mode(self, name):
        p = MODES[name]
        self.settings.update({
            "mode": name,
            "filter": p["filter"],
            "intensity": p["intensity"],
            "brightness_compression": p["compression"],
            "enabled": True,
        })
        save_settings(self.settings)

    def toggle(self):
        self.settings["enabled"] = not self.settings["enabled"]
        save_settings(self.settings)

    def toggle_reveal(self):
        self.settings["temporary_reveal"] = not self.settings.get("temporary_reveal", False)
        save_settings(self.settings)

    def toggle_gaming_safe(self):
        self.settings["gaming_safe_mode"] = not self.settings.get("gaming_safe_mode", False)
        self.last_luma = None
        self.flash_until = 0
        save_settings(self.settings)

    def remember_monitors(self):
        profiles = self.settings.setdefault("monitor_profiles", {})
        for sid, _rect in getattr(self, "monitor_items", monitor_info()):
            profiles[sid] = {
                "filter": self.settings["filter"],
                "intensity": int(self.settings["intensity"]),
                "enabled": True,
            }
        self.settings["monitor_memory"] = True
        save_settings(self.settings)

    def clear_monitor_memory(self):
        self.settings["monitor_profiles"] = {}
        save_settings(self.settings)

    def choose_filter(self, key):
        if key in FILTERS:
            self.settings["filter"] = key
            self.settings["enabled"] = True
            save_settings(self.settings)

    def setup_hotkeys(self):
        keyboard.add_hotkey("ctrl+shift+m", self.toggle)
        keyboard.add_hotkey("ctrl+shift+r", lambda: self.apply_mode("Reading"))
        keyboard.add_hotkey("ctrl+shift+d", lambda: self.apply_mode("Media"))
        keyboard.add_hotkey("ctrl+shift+n", lambda: self.apply_mode("Night"))
        keyboard.add_hotkey("ctrl+shift+up", lambda: self.change_intensity(1))
        keyboard.add_hotkey("ctrl+shift+down", lambda: self.change_intensity(-1))
        keyboard.add_hotkey("ctrl+shift+g", self.toggle_gaming_safe)
        keyboard.add_hotkey("ctrl+shift+p", self.toggle_reveal)

    def change_intensity(self, d):
        self.settings["intensity"] = max(1, min(20, int(self.settings["intensity"]) + d))
        save_settings(self.settings)

    def setup_tray(self):
        icon = Image.new("RGBA", (64,64), (0,0,0,0))
        d = ImageDraw.Draw(icon)
        d.ellipse((10,10,54,54), fill=(214,126,156,255))
        d.ellipse((26,14,54,48), fill=(30,24,34,255))

        def item(label, fn, checked=None):
            return pystray.MenuItem(label, lambda *_: fn(), checked=checked)

        filter_items = [
            item(FILTERS[k]["name"], lambda key=k: self.choose_filter(key),
                 lambda _i, key=k: self.settings.get("filter") == key)
            for k in FILTERS
        ]

        self.tray = pystray.Icon(
            "MigraineFilter", icon, APP_NAME,
            menu=pystray.Menu(
                item("Toggle Filter", self.toggle,
                     lambda _: self.settings.get("enabled", True)),
                item("Temporary Reveal", self.toggle_reveal,
                     lambda _: self.settings.get("temporary_reveal", False)),
                item("Gaming Safe Mode", self.toggle_gaming_safe,
                     lambda _: self.settings.get("gaming_safe_mode", False)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Filters", pystray.Menu(*filter_items)),
                pystray.MenuItem("Quick Modes", pystray.Menu(
                    item("Reading", lambda: self.apply_mode("Reading")),
                    item("Media", lambda: self.apply_mode("Media")),
                    item("Night", lambda: self.apply_mode("Night")),
                    item("Normal", lambda: self.apply_mode("Normal")),
                )),
                pystray.Menu.SEPARATOR,
                item("Adaptive Brightness", self.toggle_adaptive,
                     lambda _: self.settings["adaptive_brightness"]),
                item("Flash Protection", self.toggle_flash,
                     lambda _: self.settings["flash_protection"]),
                item("Remember Current Monitors", self.remember_monitors),
                item("Clear Monitor Memory", self.clear_monitor_memory),
                item("Launch with Windows", self.toggle_startup,
                     lambda _: self.settings["launch_at_login"]),
                pystray.Menu.SEPARATOR,
                item("Quit", self.quit),
            )
        )
        threading.Thread(target=self.tray.run, daemon=True).start()

    def toggle_adaptive(self):
        self.settings["adaptive_brightness"] = not self.settings["adaptive_brightness"]
        save_settings(self.settings)

    def toggle_flash(self):
        self.settings["flash_protection"] = not self.settings["flash_protection"]
        save_settings(self.settings)

    def toggle_startup(self):
        self.settings["launch_at_login"] = not self.settings["launch_at_login"]
        set_startup(self.settings["launch_at_login"])
        save_settings(self.settings)

    def quit(self):
        keyboard.unhook_all_hotkeys()
        try: self.tray.stop()
        except Exception: pass
        self.root.after(0, self.root.destroy)

    def tick(self):
        now = time.time()

        # Sleep/wake protection: a large scheduler gap means Windows slept/locked/stalled.
        gap = now - self.last_tick
        self.last_tick = now
        if gap > 4.0:
            self.startup_safe_until = now + 1.5
            self.rebuild_overlays()

        if now - self.last_monitor_check > 3:
            self.last_monitor_check = now
            if len(self.overlays) != len(monitor_info()):
                self.startup_safe_until = now + 1.5
                self.rebuild_overlays()

        if self.settings.get("gaming_safe_mode", False):
            # No MSS capture at all while gaming-safe is active.
            self.last_luma = None
            self.flash_until = 0
            luma = .5
        elif now - self.last_sample > .18:
            self.last_sample = now
            luma = self.sample_luminance()
            if self.last_luma is not None and self.settings.get("flash_protection"):
                delta = luma - self.last_luma
                if delta > .20 or (luma > .78 and delta > .10):
                    self.flash_until = now + 1.4
            self.last_luma = luma
        else:
            luma = self.last_luma if self.last_luma is not None else .5

        default_rgb = FILTERS.get(self.settings["filter"], FILTERS["dark"])["rgb"]
        default_target = self.effective_alpha(luma)

        for idx, o in enumerate(self.overlays):
            rgb = default_rgb
            target = default_target
            # Monitor Memory: a recognized monitor can restore its own filter/intensity.
            if self.settings.get("monitor_memory", True) and idx < len(self.monitor_items):
                sid = self.monitor_items[idx][0]
                p = self.settings.get("monitor_profiles", {}).get(sid)
                if p:
                    rgb = FILTERS.get(p.get("filter"), FILTERS["dark"])["rgb"]
                    old_intensity = self.settings["intensity"]
                    old_enabled = self.settings["enabled"]
                    try:
                        self.settings["intensity"] = int(p.get("intensity", old_intensity))
                        self.settings["enabled"] = bool(p.get("enabled", True))
                        target = self.effective_alpha(luma)
                    finally:
                        self.settings["intensity"] = old_intensity
                        self.settings["enabled"] = old_enabled
            o.set_color(rgb)
            o.set_target(target)
            o.tick(self.settings.get("auto_fade", True), self.settings.get("fade_speed", .10))

        self.root.after(30, self.tick)

if __name__ == "__main__":
    App().root.mainloop()
