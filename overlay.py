# overlay.py — Tkinter always-on-top floating mode indicator

import tkinter as tk
from config import (
    OVERLAY_WIDTH,
    OVERLAY_HEIGHT,
    OVERLAY_MARGIN,
    OVERLAY_BG_COLOR,
    OVERLAY_FG_COLOR,
    OVERLAY_FONT,
    OVERLAY_ALPHA,
)


class ModeOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)           # no title bar
        self.root.attributes("-topmost", True)     # always on top
        self.root.attributes("-alpha", OVERLAY_ALPHA)
        self.root.configure(bg=OVERLAY_BG_COLOR)

        # Position top-right
        screen_w = self.root.winfo_screenwidth()
        x = screen_w - OVERLAY_WIDTH - OVERLAY_MARGIN
        y = OVERLAY_MARGIN
        self.root.geometry(f"{OVERLAY_WIDTH}x{OVERLAY_HEIGHT}+{x}+{y}")

        self.label = tk.Label(
            self.root,
            text="MANHWA MODE",
            font=OVERLAY_FONT,
            bg=OVERLAY_BG_COLOR,
            fg=OVERLAY_FG_COLOR,
        )
        self.label.pack(expand=True, fill=tk.BOTH)

        # Rounded corners hack (Windows 11 supports it via DWM)
        try:
            from ctypes import windll
            HWND = windll.user32.GetParent(self.root.winfo_id())
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            windll.dwmapi.DwmSetWindowAttribute(
                HWND, DWMWA_WINDOW_CORNER_PREFERENCE,
                tk.byref(tk.c_int(DWMWCP_ROUND)), tk.sizeof(tk.c_int)
            )
        except Exception:
            pass  # rounded corners optional

        self.root.update_idletasks()

    def set_mode(self, mode):
        text = f"{mode} MODE"
        color = OVERLAY_FG_COLOR
        if mode == "DESKTOP":
            color = "#f5e0dc"  # Catppuccin rosewater
        self.label.config(text=text, fg=color)

    def update(self):
        self.root.update_idletasks()
        self.root.update()

    def close(self):
        self.root.destroy()
