# Vocal Gaze Mouse Controller

A hands-free desktop mouse controller that combines **eye-gaze tracking, blink gestures, and voice commands**. It uses a webcam to estimate gaze direction and moves the system cursor with smoothing; a deliberate blink can click, while optional voice commands provide additional controls.

## Features

- 👁️ Webcam-based gaze tracking with MediaPipe Face Mesh
- 🖱️ Smooth gaze-to-cursor movement
- 😉 Blink-to-left-click with debounce protection
- 🎙️ Voice commands: click, double click, right click, scroll, pause, resume, exit
- ⏸️ Keyboard pause/resume and safe quit controls
- ⚙️ Central configuration for sensitivity and smoothing
- 🧩 Modular Python structure

## Project Structure

```text
vocal-gaze-mouse-controller/
├── main.py
├── gaze_tracker.py
├── voice_control.py
├── config.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or 3.11 recommended
- Working webcam
- Windows, macOS, or Linux
- Microphone for voice commands
- macOS may require Camera, Microphone, and Accessibility permissions

## Installation

```bash
git clone https://github.com/Siddharth019/vocal-gaze-mouse-controller.git
cd vocal-gaze-mouse-controller
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Look at the webcam and move your eyes to control the cursor. A short deliberate blink triggers a left click. Voice recognition starts automatically when a microphone is available.

### Keyboard controls

| Key | Action |
|---|---|
| `P` | Pause/resume gaze control |
| `Q` | Quit safely |

### Voice commands

Examples:

- `click`
- `double click`
- `right click`
- `scroll up`
- `scroll down`
- `pause`
- `resume`
- `exit`

Voice recognition uses the SpeechRecognition Google recognizer and therefore requires an internet connection while processing speech.

## How It Works

1. MediaPipe detects facial and iris landmarks from the webcam frame.
2. Iris position is normalized relative to each eye.
3. The normalized gaze position is mapped to the screen resolution.
4. Exponential smoothing reduces cursor jitter.
5. Eye aspect-ratio-style measurements detect deliberate blinks.
6. A background speech-recognition listener converts supported phrases into mouse actions.

## Safety

This software controls the real system cursor. Test it in a low-risk environment first. Use `P` to pause control and `Q` to exit. Avoid running it while important unsaved work is open.

## Limitations

Gaze estimation is camera- and lighting-dependent and is not intended as a medical or accessibility-certified eye-tracking system. Accuracy can vary with camera placement, glasses, lighting, and face position.

## License

MIT License. See `LICENSE`.

## Author

**Siddharth Kumar**  
GitHub: [Siddharth019](https://github.com/Siddharth019)
