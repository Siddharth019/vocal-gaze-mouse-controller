"""Optional background voice-command support."""

from __future__ import annotations

import threading
from typing import Callable, Optional


class VoiceController:
    COMMANDS = {
        "click": "click",
        "left click": "click",
        "double click": "double_click",
        "right click": "right_click",
        "scroll up": "scroll_up",
        "scroll down": "scroll_down",
        "pause": "pause",
        "resume": "resume",
        "exit": "exit",
        "quit": "exit",
    }

    def __init__(self, callback: Callable[[str], None]) -> None:
        self.callback = callback
        self.recognizer = None
        self.microphone = None
        self.stop_listening: Optional[Callable[[bool], None]] = None

    def start(self) -> bool:
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.recognizer.pause_threshold = 0.7
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            self.stop_listening = self.recognizer.listen_in_background(
                self.microphone, self._handle_audio, phrase_time_limit=4
            )
            return True
        except Exception as exc:
            print(f"Voice control unavailable: {exc}")
            return False

    def _handle_audio(self, recognizer, audio) -> None:
        try:
            text = recognizer.recognize_google(audio).lower().strip()
        except Exception:
            return

        command = self.COMMANDS.get(text)
        if command:
            self.callback(command)

    def stop(self) -> None:
        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)
            self.stop_listening = None
