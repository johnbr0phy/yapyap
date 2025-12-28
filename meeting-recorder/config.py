"""
Meeting Recorder - Configuration
"""

import os
from pathlib import Path

# Base directory (where the app lives)
APP_DIR = Path(__file__).parent.resolve()

# User data directory
DATA_DIR = Path.home() / "meeting-recorder"

# Configuration
CONFIG = {
    "audio": {
        "system_device": "BlackHole 2ch",
        "mic_device": "default",
        "sample_rate": 16000,
    },
    "whisper": {
        "model": "small",
        "language": "en",  # or None for auto-detect
    },
    "calendar": {
        "poll_interval_minutes": 5,
        "auto_record": True,
    },
    "paths": {
        "recordings": DATA_DIR / "recordings",
        "transcripts": DATA_DIR / "transcripts",
        "logs": DATA_DIR / "logs",
    },
}


def ensure_directories():
    """Create necessary directories if they don't exist."""
    for key in ["recordings", "transcripts", "logs"]:
        path = CONFIG["paths"][key]
        path.mkdir(parents=True, exist_ok=True)


def get_recordings_dir() -> Path:
    return CONFIG["paths"]["recordings"]


def get_transcripts_dir() -> Path:
    return CONFIG["paths"]["transcripts"]


def get_logs_dir() -> Path:
    return CONFIG["paths"]["logs"]
