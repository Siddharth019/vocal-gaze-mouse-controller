"""Face, iris and blink tracking helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Optional, Tuple

import cv2
import mediapipe as mp


@dataclass
class GazeResult:
    x: float
    y: float
    blink: bool


class GazeTracker:
    """Estimate normalized gaze position and blink state from a webcam frame."""

    LEFT_IRIS = (468, 469, 470, 471, 472)
    RIGHT_IRIS = (473, 474, 475, 476, 477)
    LEFT_EYE_H = (33, 133)
    RIGHT_EYE_H = (362, 263)
    LEFT_EYE_V = (159, 145)
    RIGHT_EYE_V = (386, 374)

    def __init__(self, blink_threshold: float = 0.19) -> None:
        self.blink_threshold = blink_threshold
        self.mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._blink_frames = 0

    @staticmethod
    def _point(landmarks, index: int, width: int, height: int) -> Tuple[float, float]:
        p = landmarks[index]
        return p.x * width, p.y * height

    @classmethod
    def _iris_center(cls, landmarks, indices, width, height):
        points = [cls._point(landmarks, i, width, height) for i in indices]
        return (
            sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points),
        )

    @staticmethod
    def _ratio(landmarks, horizontal, vertical, width, height) -> float:
        h1 = GazeTracker._point(landmarks, horizontal[0], width, height)
        h2 = GazeTracker._point(landmarks, horizontal[1], width, height)
        v1 = GazeTracker._point(landmarks, vertical[0], width, height)
        v2 = GazeTracker._point(landmarks, vertical[1], width, height)
        horizontal_distance = hypot(h2[0] - h1[0], h2[1] - h1[1])
        vertical_distance = hypot(v2[0] - v1[0], v2[1] - v1[1])
        return vertical_distance / max(horizontal_distance, 1e-6)

    def process(self, frame) -> Optional[GazeResult]:
        height, width = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mesh.process(rgb)
        if not result.multi_face_landmarks:
            return None

        landmarks = result.multi_face_landmarks[0].landmark
        left_iris = self._iris_center(landmarks, self.LEFT_IRIS, width, height)
        right_iris = self._iris_center(landmarks, self.RIGHT_IRIS, width, height)

        left_c1 = self._point(landmarks, self.LEFT_EYE_H[0], width, height)
        left_c2 = self._point(landmarks, self.LEFT_EYE_H[1], width, height)
        right_c1 = self._point(landmarks, self.RIGHT_EYE_H[0], width, height)
        right_c2 = self._point(landmarks, self.RIGHT_EYE_H[1], width, height)

        left_min_x, left_max_x = sorted((left_c1[0], left_c2[0]))
        right_min_x, right_max_x = sorted((right_c1[0], right_c2[0]))
        left_x = (left_iris[0] - left_min_x) / max(left_max_x - left_min_x, 1e-6)
        right_x = (right_iris[0] - right_min_x) / max(right_max_x - right_min_x, 1e-6)

        left_top = self._point(landmarks, self.LEFT_EYE_V[0], width, height)
        left_bottom = self._point(landmarks, self.LEFT_EYE_V[1], width, height)
        right_top = self._point(landmarks, self.RIGHT_EYE_V[0], width, height)
        right_bottom = self._point(landmarks, self.RIGHT_EYE_V[1], width, height)
        left_y = (left_iris[1] - min(left_top[1], left_bottom[1])) / max(abs(left_bottom[1] - left_top[1]), 1e-6)
        right_y = (right_iris[1] - min(right_top[1], right_bottom[1])) / max(abs(right_bottom[1] - right_top[1]), 1e-6)

        blink_ratio = (
            self._ratio(landmarks, self.LEFT_EYE_H, self.LEFT_EYE_V, width, height)
            + self._ratio(landmarks, self.RIGHT_EYE_H, self.RIGHT_EYE_V, width, height)
        ) / 2
        is_closed = blink_ratio < self.blink_threshold
        if is_closed:
            self._blink_frames += 1
        else:
            self._blink_frames = 0

        return GazeResult(
            x=(left_x + right_x) / 2,
            y=(left_y + right_y) / 2,
            blink=self._blink_frames >= 2,
        )

    def close(self) -> None:
        self.mesh.close()
