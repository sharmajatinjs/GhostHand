# gesture_classifier.py — Classify gestures from 21 MediaPipe landmarks

import math
import time
import numpy as np
from config import (
    PINCH_THRESHOLD,
    FIST_THRESHOLD,
    FIST_STABLE_FRAMES,
    FIST_HOLD_DESKTOP,
    PEACE_ANGLE_MIN,
    PEACE_ANGLE_MAX,
    SWIPE_MIN_DISTANCE,
    SWIPE_MAX_TIME,
    SWIPE_COOLDOWN,
    TWO_FINGER_SWIPE_VERTICAL,
    SCROLL_DEADZONE,
    POINT_HOLD_TIME,
    TOGGLE_HOLD_TIME,
    STARTUP_GRACE_SECONDS,
)

# ── Gesture constants ─────────────────────────────────────────────────────────
NONE             = "NONE"
PINCH            = "PINCH"
FIST             = "FIST"
FIST_DESKTOP     = "FIST_DESKTOP"
PEACE            = "PEACE"
POINT            = "POINT"

# 2-finger gestures
SWIPE_LEFT       = "SWIPE_LEFT"
SWIPE_RIGHT      = "SWIPE_RIGHT"
SWIPE_UP         = "SWIPE_UP"
SWIPE_DOWN       = "SWIPE_DOWN"
SCROLL_UP        = "SCROLL_UP"
SCROLL_DOWN      = "SCROLL_DOWN"
SCROLL_HOLD_UP   = "SCROLL_HOLD_UP"
SCROLL_HOLD_DOWN = "SCROLL_HOLD_DOWN"

# 3-finger → Win+Tab (task view)
WIN_TAB          = "WIN_TAB"

# 4-finger → Alt+Tab (window switch)
ALT_TAB          = "ALT_TAB"

# 5-finger / full palm → Show desktop
SHOW_DESKTOP     = "SHOW_DESKTOP"

# Cooldown for one-shot multi-finger gestures (seconds)
_MULTIFINEGER_COOLDOWN = 0.9


def _dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def _angle(p1, p2, p3):
    v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
    v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    cos = np.clip(np.dot(v1, v2) / (norm1 * norm2), -1.0, 1.0)
    return math.degrees(math.acos(cos))


def _count_extended(landmarks):
    """Return (count, list_of_bool) for 5 fingers: thumb, index, middle, ring, pinky"""
    wrist = landmarks[0]
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]
    extended = []
    for tip, pip in zip(tips, pips):
        extended.append(_dist(landmarks[tip], wrist) > _dist(landmarks[pip], wrist))
    return sum(extended), extended


class GestureClassifier:
    def __init__(self):
        # Swipe tracking (2-finger)
        self._swipe_start_pos  = None
        self._swipe_start_time = 0
        self._last_swipe_time  = 0

        # Point hold (1-finger)
        self._point_start_time = 0
        self._point_triggered  = False

        # Peace toggle
        self._peace_start_time = 0

        # Fist stability + hold
        self._fist_frame_count      = 0
        self._fist_hold_start       = 0
        self._fist_desktop_triggered = False

        # Continuous scroll state (2-finger vertical hold)
        self._scroll_hold_start  = 0
        self._scroll_hold_dir    = 0
        self._last_auto_scroll   = 0
        self._prev_wrist_y_2f    = None   # for 2-finger vertical scroll

        # One-shot cooldowns for 3/4/5-finger gestures
        self._last_win_tab    = 0
        self._last_alt_tab    = 0
        self._last_show_desk  = 0

        # Startup grace
        self._start_time = time.time()

    def classify(self, landmarks):
        now = time.time()

        if now - self._start_time < STARTUP_GRACE_SECONDS:
            return NONE, {}

        if landmarks is None:
            self._reset_tracking()
            return NONE, {}

        wrist      = landmarks[0]
        thumb_tip  = landmarks[4]
        index_tip  = landmarks[8]
        index_mcp  = landmarks[5]
        middle_tip = landmarks[12]
        ring_tip   = landmarks[16]
        ring_pip   = landmarks[14]
        pinky_tip  = landmarks[20]
        pinky_pip  = landmarks[18]

        ext_count, extended = _count_extended(landmarks)
        thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext = extended

        # ── PRIORITY: highest finger count wins ───────────────────────────────
        # Checked from highest to lowest so 4-finger never accidentally fires 2-finger logic

        # ── 5 FINGERS / FULL PALM → Show Desktop ─────────────────────────────
        if ext_count == 5:
            if now - self._last_show_desk > _MULTIFINEGER_COOLDOWN:
                self._last_show_desk = now
                self._reset_tracking()
                return SHOW_DESKTOP, {}
            return NONE, {}

        # ── 4 FINGERS → Alt+Tab (window switch) ──────────────────────────────
        if index_ext and middle_ext and ring_ext and pinky_ext:
            if now - self._last_alt_tab > _MULTIFINEGER_COOLDOWN:
                self._last_alt_tab = now
                self._reset_tracking()
                return ALT_TAB, {}
            return NONE, {}

        # ── 3 FINGERS → Win+Tab (task view) ──────────────────────────────────
        if index_ext and middle_ext and ring_ext and not pinky_ext:
            if now - self._last_win_tab > _MULTIFINEGER_COOLDOWN:
                self._last_win_tab = now
                self._reset_tracking()
                return WIN_TAB, {}
            return NONE, {}

        # ── PINCH (0 fingers, thumb+index close) ─────────────────────────────
        pinch_dist = _dist(thumb_tip, index_tip)
        if pinch_dist < PINCH_THRESHOLD:
            self._reset_tracking()
            return PINCH, {}

        # ── FIST (0 fingers) + hold for desktop ──────────────────────────────
        fingertip_dists = [_dist(landmarks[i], wrist) for i in [4, 8, 12, 16, 20]]
        avg_dist = sum(fingertip_dists) / len(fingertip_dists)

        if avg_dist < FIST_THRESHOLD:
            self._fist_frame_count += 1
            if self._fist_frame_count >= FIST_STABLE_FRAMES:
                if self._fist_hold_start == 0:
                    self._fist_hold_start = now
                elif (not self._fist_desktop_triggered and
                      now - self._fist_hold_start >= FIST_HOLD_DESKTOP):
                    self._fist_desktop_triggered = True
                    self._reset_tracking()
                    return FIST_DESKTOP, {}
                return FIST, {}
        else:
            self._fist_frame_count       = 0
            self._fist_hold_start        = 0
            self._fist_desktop_triggered = False

        # ── PEACE SIGN → toggle mode ──────────────────────────────────────────
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            angle = _angle(index_tip, index_mcp, middle_tip)
            if PEACE_ANGLE_MIN < angle < PEACE_ANGLE_MAX:
                if self._peace_start_time == 0:
                    self._peace_start_time = now
                elif now - self._peace_start_time >= TOGGLE_HOLD_TIME:
                    self._peace_start_time = 0
                    self._reset_tracking()
                    return PEACE, {}
                return NONE, {}
        self._peace_start_time = 0

        # ── 1 FINGER (index only) → Point / move cursor ───────────────────────
        if index_ext and not middle_ext and not ring_ext and not pinky_ext:
            if self._point_start_time == 0:
                self._point_start_time = now
            elif not self._point_triggered and (now - self._point_start_time >= POINT_HOLD_TIME):
                self._point_triggered = True
            if self._point_triggered:
                return POINT, {"target": (index_tip[0], index_tip[1])}
            return NONE, {}
        else:
            self._point_start_time = 0
            self._point_triggered  = False

        # ── 2 FINGERS (index + middle) → Swipe L/R or Scroll U/D ─────────────
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            wrist_x = wrist[0]
            wrist_y = wrist[1]

            # Horizontal swipe → next/prev page
            if self._swipe_start_pos is None:
                self._swipe_start_pos  = (wrist_x, wrist_y)
                self._swipe_start_time = now
                self._prev_wrist_y_2f  = wrist_y
            else:
                dx = wrist_x - self._swipe_start_pos[0]
                dy = wrist_y - self._swipe_start_pos[1]
                dt = now - self._swipe_start_time

                if dt > SWIPE_MAX_TIME:
                    self._swipe_start_pos  = (wrist_x, wrist_y)
                    self._swipe_start_time = now
                elif abs(dx) >= SWIPE_MIN_DISTANCE and abs(dx) > abs(dy) * 1.5:
                    if now - self._last_swipe_time >= SWIPE_COOLDOWN:
                        self._last_swipe_time = now
                        self._swipe_start_pos = None
                        return (SWIPE_RIGHT if dx > 0 else SWIPE_LEFT), {}
                elif abs(dy) >= TWO_FINGER_SWIPE_VERTICAL and abs(dy) > abs(dx) * 1.5:
                    if now - self._last_swipe_time >= SWIPE_COOLDOWN:
                        self._last_swipe_time = now
                        self._swipe_start_pos = None
                        return (SWIPE_UP if dy < 0 else SWIPE_DOWN), {}

            # Slow 2-finger vertical movement → continuous scroll
            if self._prev_wrist_y_2f is not None:
                slow_dy = self._prev_wrist_y_2f - wrist_y   # positive = hand up
                self._prev_wrist_y_2f = wrist_y
                if abs(slow_dy) > SCROLL_DEADZONE:
                    dir_now = 1 if slow_dy > 0 else -1
                    if self._scroll_hold_dir == dir_now and self._scroll_hold_start > 0:
                        if now - self._last_auto_scroll >= 0.05:
                            self._last_auto_scroll = now
                            return (SCROLL_HOLD_UP if dir_now > 0 else SCROLL_HOLD_DOWN), {}
                    else:
                        self._scroll_hold_start = now
                        self._scroll_hold_dir   = dir_now
                        self._last_auto_scroll  = now
                        return (SCROLL_UP if dir_now > 0 else SCROLL_DOWN), {}
                else:
                    self._scroll_hold_start = 0
                    self._scroll_hold_dir   = 0
        else:
            self._swipe_start_pos    = None
            self._prev_wrist_y_2f   = None
            self._scroll_hold_start = 0
            self._scroll_hold_dir   = 0

        return NONE, {}

    def _reset_tracking(self):
        self._swipe_start_pos        = None
        self._swipe_start_time       = 0
        self._point_start_time       = 0
        self._point_triggered        = False
        self._peace_start_time       = 0
        self._fist_frame_count       = 0
        self._fist_hold_start        = 0
        self._fist_desktop_triggered = False
        self._scroll_hold_start      = 0
        self._scroll_hold_dir        = 0
        self._last_auto_scroll       = 0
        self._prev_wrist_y_2f        = None
