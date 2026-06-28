# gesture_detector.py — MediaPipe hand tracking, returns 21 landmarks per frame

import cv2
import mediapipe as mp
import numpy as np
from config import (
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MODEL_COMPLEXITY,
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)


class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            model_complexity=MODEL_COMPLEXITY,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles

        self.cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # DSHOW = faster on Windows
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # reduce latency

        if not self.cap.isOpened():
            raise RuntimeError("Cannot open webcam. Check CAMERA_INDEX in config.py")

    def get_frame(self):
        """Returns (success, frame_bgr, landmarks_list) where landmarks_list is
        list of 21 (x, y, z) tuples normalized 0–1, or None if no hand."""
        success, frame = self.cap.read()
        if not success:
            return False, None, None

        frame = cv2.flip(frame, 1)  # mirror for natural interaction
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True

        landmarks = None
        if results.multi_hand_landmarks:
            # Only use first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

            # Draw landmarks (optional, for debugging)
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_styles.get_default_hand_landmarks_style(),
                self.mp_styles.get_default_hand_connections_style(),
            )

        return True, frame, landmarks

    def release(self):
        self.cap.release()
        self.hands.close()
        cv2.destroyAllWindows()
