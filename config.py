"""Runtime configuration for Vocal Gaze Mouse Controller."""

CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Cursor mapping margins. Smaller values use more of the camera frame.
GAZE_X_MIN = 0.08
GAZE_X_MAX = 0.92
GAZE_Y_MIN = 0.10
GAZE_Y_MAX = 0.90

# Cursor smoothing: higher = faster response, lower = smoother.
SMOOTHING = 0.28

# Blink detection threshold and minimum frames to avoid accidental clicks.
BLINK_THRESHOLD = 0.19
BLINK_MIN_FRAMES = 2
BLINK_COOLDOWN_SECONDS = 0.8

# Voice recognition settings.
VOICE_ENABLED = True
VOICE_PHRASE_TIME_LIMIT = 4
VOICE_PAUSE_THRESHOLD = 0.7
