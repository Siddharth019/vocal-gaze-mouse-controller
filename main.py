"""Vocal Gaze Mouse Controller entry point."""

from __future__ import annotations

import time

import cv2
import pyautogui

import config
from gaze_tracker import GazeTracker
from voice_control import VoiceController


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def remap(value: float, low: float, high: float) -> float:
    return clamp((value - low) / max(high - low, 1e-6), 0.0, 1.0)


def main() -> None:
    pyautogui.PAUSE = 0.02
    screen_w, screen_h = pyautogui.size()
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check camera permissions and connection.")

    tracker = GazeTracker(config.BLINK_THRESHOLD)
    voice = VoiceController(lambda command: handle_command(command))
    state = {"paused": False, "running": True}
    last_blink = 0.0
    previous_blink = False
    cursor_x, cursor_y = pyautogui.position()

    def command_handler(command: str) -> None:
        if command == "click":
            pyautogui.click()
        elif command == "double_click":
            pyautogui.doubleClick(interval=0.08)
        elif command == "right_click":
            pyautogui.rightClick()
        elif command == "scroll_up":
            pyautogui.scroll(5)
        elif command == "scroll_down":
            pyautogui.scroll(-5)
        elif command == "pause":
            state["paused"] = True
        elif command == "resume":
            state["paused"] = False
        elif command == "exit":
            state["running"] = False

    # Keep the callback target accessible without exposing application state globally.
    handle_command = command_handler
    voice.callback = command_handler
    if config.VOICE_ENABLED:
        voice.start()

    try:
        while state["running"]:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            result = tracker.process(frame)

            if result and not state["paused"]:
                target_x = remap(result.x, config.GAZE_X_MIN, config.GAZE_X_MAX) * screen_w
                target_y = remap(result.y, config.GAZE_Y_MIN, config.GAZE_Y_MAX) * screen_h
                cursor_x += (target_x - cursor_x) * config.SMOOTHING
                cursor_y += (target_y - cursor_y) * config.SMOOTHING
                pyautogui.moveTo(int(cursor_x), int(cursor_y), duration=0)

                now = time.monotonic()
                if result.blink and not previous_blink and now - last_blink > config.BLINK_COOLDOWN_SECONDS:
                    pyautogui.click()
                    last_blink = now
                previous_blink = result.blink

            status = "PAUSED" if state["paused"] else "ACTIVE"
            cv2.putText(frame, f"Gaze Mouse: {status}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, "P: pause/resume | Q: quit", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow("Vocal Gaze Mouse Controller", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                state["running"] = False
            elif key == ord("p"):
                state["paused"] = not state["paused"]
    finally:
        voice.stop()
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
