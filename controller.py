# controller.py — Maps gestures to OS actions (pyautogui + pynput)

import pyautogui
import time
from pynput.keyboard import Controller as KeyboardController, Key
from config import (
    SCROLL_SENSITIVITY,
    MOUSE_SMOOTHING,
    MOUSE_SPEED_MULTIPLIER,
    AUTO_SCROLL_AMOUNT,
)
import screeninfo

pyautogui.FAILSAFE = False
keyboard = KeyboardController()

try:
    monitor = screeninfo.get_monitors()[0]
    SCREEN_W, SCREEN_H = monitor.width, monitor.height
except Exception:
    SCREEN_W, SCREEN_H = 1920, 1080


class Controller:
    def __init__(self):
        self.mode = "MANHWA"
        self._mouse_smooth_x = SCREEN_W // 2
        self._mouse_smooth_y = SCREEN_H // 2

    def set_mode(self, mode):
        self.mode = mode

    def act(self, gesture, extra):
        if gesture == "FIST":
            return  # pause handled in main.py

        # ── gestures that work in BOTH modes ─────────────────────────────────

        if gesture == "FIST_DESKTOP":
            self._win_d()
            return

        # 3 fingers → Win+Tab (task view)
        if gesture == "WIN_TAB":
            self._win_tab()
            return

        # 4 fingers → Alt+Tab (window switch)
        if gesture == "ALT_TAB":
            self._alt_tab()
            return

        # 5 fingers / palm → Show Desktop (Win+D)
        if gesture == "SHOW_DESKTOP":
            self._win_d()
            return

        # Scroll works same in both modes
        if gesture == "SCROLL_UP":
            pyautogui.scroll(SCROLL_SENSITIVITY)
            return
        if gesture == "SCROLL_DOWN":
            pyautogui.scroll(-SCROLL_SENSITIVITY)
            return
        if gesture == "SCROLL_HOLD_UP":
            pyautogui.scroll(AUTO_SCROLL_AMOUNT)
            return
        if gesture == "SCROLL_HOLD_DOWN":
            pyautogui.scroll(-AUTO_SCROLL_AMOUNT)
            return

        # Point (1 finger) → cursor move in both modes
        if gesture == "POINT":
            target = extra.get("target")
            if target:
                self._move_mouse_smooth(target)
            return

        # ── mode-specific gestures ────────────────────────────────────────────
        if self.mode == "MANHWA":
            self._act_manhwa(gesture, extra)
        else:
            self._act_desktop(gesture, extra)

    # ── MANHWA MODE ───────────────────────────────────────────────────────────
    def _act_manhwa(self, gesture, extra):
        if gesture == "SWIPE_RIGHT":       # 2-finger swipe right → next page
            self._tap(Key.right)
        elif gesture == "SWIPE_LEFT":      # 2-finger swipe left → prev page
            self._tap(Key.left)
        elif gesture == "SWIPE_UP":        # 2-finger fast swipe up → Page Up
            self._tap(Key.page_up)
        elif gesture == "SWIPE_DOWN":      # 2-finger fast swipe down → Page Down
            self._tap(Key.page_down)
        elif gesture == "PINCH":           # pinch → click (e.g. Next Chapter button)
            pyautogui.click()

    # ── DESKTOP MODE ──────────────────────────────────────────────────────────
    def _act_desktop(self, gesture, extra):
        if gesture == "PINCH":
            pyautogui.click()
        elif gesture == "SWIPE_RIGHT":
            self._tap(Key.right)
        elif gesture == "SWIPE_LEFT":
            self._tap(Key.left)

    # ── KEYBOARD HELPERS ──────────────────────────────────────────────────────
    def _tap(self, key):
        keyboard.press(key)
        keyboard.release(key)

    def _win_d(self):
        """Win+D → show/hide desktop"""
        with keyboard.pressed(Key.cmd):
            keyboard.press('d')
            keyboard.release('d')

    def _win_tab(self):
        """Win+Tab → task view"""
        with keyboard.pressed(Key.cmd):
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)

    def _alt_tab(self):
        """Alt+Tab → switch window"""
        with keyboard.pressed(Key.alt):
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)

    # ── MOUSE ─────────────────────────────────────────────────────────────────
    def _move_mouse_smooth(self, target_norm):
        tx = int(target_norm[0] * SCREEN_W * MOUSE_SPEED_MULTIPLIER)
        ty = int(target_norm[1] * SCREEN_H * MOUSE_SPEED_MULTIPLIER)
        tx = max(0, min(SCREEN_W - 1, tx))
        ty = max(0, min(SCREEN_H - 1, ty))

        self._mouse_smooth_x = int(
            MOUSE_SMOOTHING * tx + (1 - MOUSE_SMOOTHING) * self._mouse_smooth_x
        )
        self._mouse_smooth_y = int(
            MOUSE_SMOOTHING * ty + (1 - MOUSE_SMOOTHING) * self._mouse_smooth_y
        )
        pyautogui.moveTo(self._mouse_smooth_x, self._mouse_smooth_y, _pause=False)
