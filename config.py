# config.py — All tunable constants in one place

# ─── MediaPipe ───
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.75
MIN_TRACKING_CONFIDENCE = 0.7
MODEL_COMPLEXITY = 1

# ─── Camera ───
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 30

# ─── Gesture Thresholds ───
PINCH_THRESHOLD = 0.045
FIST_THRESHOLD = 0.055
FIST_STABLE_FRAMES = 3
FIST_HOLD_DESKTOP = 0.8          # NEW: hold fist this long → Win+D
PEACE_ANGLE_MIN = 35
PEACE_ANGLE_MAX = 85
POINT_ANGLE_THRESHOLD = 25

# Swipe detection
SWIPE_MIN_DISTANCE = 0.12
SWIPE_MAX_TIME = 0.6
SWIPE_COOLDOWN = 0.8
TWO_FINGER_SWIPE_VERTICAL = 0.08  # NEW: vertical swipe threshold for Page Up/Down

# Scroll
SCROLL_SENSITIVITY = 120
SCROLL_DEADZONE = 0.02
AUTO_SCROLL_INTERVAL = 0.05       # NEW: seconds between auto-scroll ticks
AUTO_SCROLL_AMOUNT = 60           # NEW: scroll units per tick

# Point + hold → mouse move
POINT_HOLD_TIME = 0.35
MOUSE_SMOOTHING = 0.35
MOUSE_SPEED_MULTIPLIER = 1.8

# Peace sign toggle
TOGGLE_HOLD_TIME = 1.0

# Startup grace
STARTUP_GRACE_SECONDS = 2.0

# ─── Keybinds (pynput) ───
KEY_NEXT_PAGE = 'right'
KEY_PREV_PAGE = 'left'

# ─── Overlay ───
OVERLAY_WIDTH = 220
OVERLAY_HEIGHT = 50
OVERLAY_MARGIN = 20
OVERLAY_BG_COLOR = '#1e1e2e'
OVERLAY_FG_COLOR = '#cdd6f4'
OVERLAY_FONT = ('Segoe UI', 14, 'bold')
OVERLAY_ALPHA = 0.92
