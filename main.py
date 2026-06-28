

import cv2
import time
from gesture_detector import GestureDetector
from gesture_classifier import GestureClassifier
from controller import Controller
from overlay import ModeOverlay


def main():
    print("Starting GhostHand... Press 'q' in camera window to quit.")
    print(f"Startup grace: {2.0}s — keep hand open/neutral until overlay shows mode.")
    print("\n=== GESTURES ===")
    print("MANHWA MODE:")
    print("  ✌️  Swipe R/L        → Next/Prev page (←/→)")
    print("  ✌️  Swipe Up/Down   → Page Up / Page Down")
    print("  🖐️ Scroll Up/Down   → Continuous scroll (hold)")
    print("  ☝️  Point + hold    → Move mouse")
    print("  🤟  3 fingers swipe → Ctrl+Tab / Ctrl+Shift+Tab")
    print("  🖖  4 fingers up    → Win+Tab (Task View)")
    print("  🖖  4 fingers down  → Win+Down (Minimize)")
    print("DESKTOP MODE:")
    print("  🤏 Pinch            → Left click")
    print("  🖐️ Scroll           → Continuous scroll")
    print("  🤟/🖖 Same as above → Tab switch, Task View")
    print("BOTH:")
    print("  ✊ Fist             → Pause input")
    print("  ✊ Fist hold 0.8s   → Win+D (Show Desktop)")
    print("  ✌️ Peace hold 1s    → Toggle mode\n")

    detector = GestureDetector()
    classifier = GestureClassifier()
    controller = Controller()
    overlay = ModeOverlay()

    fps_time = time.time()
    frame_count = 0
    paused = False

    try:
        while True:
            success, frame, landmarks = detector.get_frame()
            if not success:
                break

            gesture, extra = "NONE", {}

            # Always classify to detect unpause
            if landmarks is not None:
                gesture, extra = classifier.classify(landmarks)

            # FIST = pause toggle
            if gesture == "FIST":
                if not paused:
                    paused = True
                    print("[PAUSED] Input paused — open hand to resume")
            else:
                if paused:
                    paused = False
                    print("[RESUMED] Input active")

            # Execute if not paused
            if not paused:
                controller.act(gesture, extra)

                # Peace = mode toggle
                if gesture == "PEACE":
                    new_mode = "DESKTOP" if controller.mode == "MANHWA" else "MANHWA"
                    controller.set_mode(new_mode)
                    overlay.set_mode(new_mode)
                    print(f"[MODE] Switched to {new_mode}")

            # Overlay
            overlay.set_mode(controller.mode)
            overlay.update()

            # FPS
            frame_count += 1
            if time.time() - fps_time >= 1.0:
                fps = frame_count / (time.time() - fps_time)
                frame_count = 0
                fps_time = time.time()
            else:
                fps = 0

            # Draw
            cv2.putText(frame, f"Mode: {controller.mode}  FPS: {fps:.1f}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if paused:
                cv2.putText(frame, "PAUSED (FIST) — OPEN HAND TO RESUME",
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow("GhostHand", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting down...")
        detector.release()
        overlay.close()


if __name__ == "__main__":
    main()
