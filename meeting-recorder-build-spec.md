# Meeting Recorder – Build Spec

## Overview

A Mac menu bar app that records meetings, transcribes them locally with Whisper, and saves transcripts enriched with Google Calendar metadata. Runs automatically on login.

**Privacy model:** Audio never leaves the machine. Only text transcripts sync later (Phase 2+).

---

## User Experience

### Always Running
- App starts automatically when Mac boots
- Lives in menu bar as small icon
- Watches Google Calendar in background

### Before Meeting
- App detects meetings with video links (Meet, Zoom, etc.)
- When meeting start time arrives: recording begins automatically
- Notification: "Recording: [Meeting Name]"
- If you skip a meeting: click menu bar → Stop Recording (discards)

### During Meeting
- Menu bar icon shows recording state + duration
- System audio (what you hear) + mic (what you say) captured
- Keeps recording until you click Stop (meetings run over)
- Auto-stop only if silence detected for 5+ minutes (optional)

### After Meeting
- Whisper transcribes locally
- Transcript saved with meeting metadata
- Notification: "Transcript ready"

---

## Technical Requirements

### Prerequisites (user installs once)

**BlackHole 2ch**
- Virtual audio driver for capturing system audio
- Install from: https://existential.audio/blackhole/
- User creates Multi-Output Device in Audio MIDI Setup (MacBook Speakers + BlackHole)
- User sets system output to Multi-Output Device

**Whisper model**
- Download on first run or bundle with app
- Use `small` model (balance of speed/accuracy)
- ~500MB disk space

**Google OAuth**
- App needs OAuth credentials for Calendar API
- User authenticates on first run

---

## App Structure

```
meeting-recorder/
├── app.py                  # Entry point, menu bar app
├── calendar_sync.py        # Google Calendar OAuth + polling
├── recorder.py             # Audio capture (BlackHole + mic)
├── transcriber.py          # Whisper transcription
├── notifier.py             # macOS notifications
├── config.py               # Settings, paths, credentials
├── requirements.txt
├── setup.py                # First-run setup wizard
├── recordings/             # Raw audio files (temp)
├── transcripts/            # Final transcripts
└── launch/
    └── com.meetingrecorder.plist  # LaunchAgent for auto-start
```

---

## Component Specs

### 1. Menu Bar App (app.py)

Use `rumps` library for menu bar integration.

**Menu states:**

Idle:
```
[●] Meeting Recorder
    ├── Next: Q4 Planning (2:30 PM)
    ├── ──────────────────
    ├── Start Recording Manually
    ├── Open Transcripts Folder
    ├── Settings
    └── Quit
```

Recording:
```
[◉] Recording: Q4 Planning (12:34)
    ├── Stop Recording
    └── Cancel (discard audio)
```

Processing:
```
[◐] Transcribing...
    └── (no actions available)
```

**Icon states:**
- `●` = idle (black/white depending on system theme)
- `◉` = recording (red)
- `◐` = processing (animated or pulsing)

---

### 2. Google Calendar Sync (calendar_sync.py)

**OAuth flow:**
- First run: open browser for Google auth
- Store refresh token in macOS Keychain
- Token auto-refreshes

**Polling:**
- Check calendar every 5 minutes
- On wake from sleep: immediate check
- Cache today's meetings locally

**Meeting detection:**
- Has video link (Meet, Zoom, Teams, Webex)
- User is attendee (not declined)
- Starts within next 8 hours

**Data to extract per meeting:**
```python
{
    "id": "abc123",
    "title": "Q4 Planning Sync",
    "start": "2024-12-28T14:30:00",
    "end": "2024-12-28T15:30:00",
    "attendees": [
        {"name": "John", "email": "john@company.com"},
        {"name": "Sarah Chen", "email": "sarah@company.com"},
        {"name": "Mike Torres", "email": "mike@company.com"}
    ],
    "video_link": "https://meet.google.com/xyz",
    "description": "Agenda: Q4 goals, budget review..."
}
```

---

### 3. Audio Recorder (recorder.py)

**Capture sources:**
- BlackHole 2ch (system audio)
- Default input device (mic)
- Mix into single stereo file

**Libraries:**
- `sounddevice` for audio capture
- `soundfile` for WAV export

**Recording format:**
- WAV, 16kHz sample rate (Whisper optimal)
- Stereo (left = system audio, right = mic) OR mono mix
- Filename: `recordings/{meeting_id}_{timestamp}.wav`

**Functions:**
```python
def list_audio_devices() -> list
def start_recording(meeting_id: str) -> None
def stop_recording() -> str  # returns filepath
def cancel_recording() -> None  # deletes file
def get_duration() -> int  # seconds elapsed
```

---

### 4. Transcriber (transcriber.py)

**Library:** `faster-whisper` (faster than openai-whisper, runs on CPU)

**Model:** `small` (good accuracy, reasonable speed)
- ~2-3x realtime on M1/M2 Mac
- 30 min meeting ≈ 10-15 min transcription

**Functions:**
```python
def transcribe(audio_path: str) -> list[dict]
# Returns: [{"start": 0.0, "end": 2.5, "text": "Let's start..."}, ...]

def format_transcript(segments: list, meeting_metadata: dict) -> str
# Returns formatted transcript string
```

**Output format:**
```
Meeting: Q4 Planning Sync
Date: 2024-12-28 2:30 PM
Duration: 47 minutes
Attendees: John, Sarah Chen, Mike Torres

---

[00:00] Let's start with the API update.
[00:08] We hit a blocker with authentication.
[00:15] I can take a look at that tomorrow.
[00:22] Great. Can you have it done by Thursday?
[00:25] Yeah, should be fine.
[00:31] Perfect. Next item—the customer feedback from last week.
...
```

---

### 5. Notifications (notifier.py)

Use `pync` or `osascript` for native macOS notifications.

**Notification types:**

Recording started (automatic):
```
Title: "Recording: Q4 Planning Sync"
Body: "Auto-recording in progress"
```

Transcript ready:
```
Title: "Transcript ready"
Body: "Q4 Planning Sync (47 min)"
Action: Open transcript file
```

---

### 6. Auto-Start (LaunchAgent)

File: `~/Library/LaunchAgents/com.meetingrecorder.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.meetingrecorder</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/USER/meeting-recorder/app.py</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/USER/meeting-recorder/logs/stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/USER/meeting-recorder/logs/stderr.log</string>
</dict>
</plist>
```

Install with:
```bash
launchctl load ~/Library/LaunchAgents/com.meetingrecorder.plist
```

---

### 7. First-Run Setup (setup.py)

Wizard that runs on first launch:

1. **Check BlackHole installed**
   - List audio devices, look for "BlackHole"
   - If missing: show instructions + link to download

2. **Check Multi-Output Device**
   - Guide user through Audio MIDI Setup
   - Verify system output is Multi-Output Device

3. **Google OAuth**
   - Open browser for authentication
   - Store tokens in Keychain

4. **Download Whisper model**
   - Show progress bar
   - ~500MB download

5. **Test recording**
   - 5-second test recording
   - Verify audio captured from both sources

6. **Install LaunchAgent**
   - Copy plist to ~/Library/LaunchAgents/
   - Load with launchctl

---

## Configuration (config.py)

```python
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
        "auto_record": True,  # No prompts, just record
    },
    "paths": {
        "recordings": "~/meeting-recorder/recordings",
        "transcripts": "~/meeting-recorder/transcripts",
        "logs": "~/meeting-recorder/logs",
    },
}
```

---

## Dependencies (requirements.txt)

```
rumps>=0.4.0           # Menu bar app
sounddevice>=0.4.6     # Audio capture
soundfile>=0.12.1      # WAV export
faster-whisper>=0.10.0 # Transcription
google-api-python-client>=2.100.0  # Calendar API
google-auth-oauthlib>=1.1.0        # OAuth
keyring>=24.0.0        # Credential storage
pync>=2.0.3            # macOS notifications
```

---

## File Outputs

### Transcript location
`~/meeting-recorder/transcripts/{date}_{meeting_title}.txt`

Example: `2024-12-28_Q4_Planning_Sync.txt`

### Transcript format
```
Meeting: Q4 Planning Sync
Date: 2024-12-28 2:30 PM
Duration: 47 minutes
Attendees: John, Sarah Chen, Mike Torres

---

[00:00] Let's start with the API update.
[00:08] We hit a blocker with authentication.
[00:15] I can take a look at that tomorrow.
...
```

### Raw audio (optional retention)
`~/meeting-recorder/recordings/{meeting_id}_{timestamp}.wav`

Default: delete after successful transcription
Config option to retain for X days

---

## Error Handling

**BlackHole not detected:**
- Show notification with setup instructions
- Disable recording until resolved

**Google auth expired:**
- Show notification "Re-authenticate with Google"
- Click opens browser for re-auth

**Transcription fails:**
- Keep raw audio file
- Show notification "Transcription failed - audio saved"
- Retry option in menu

**Disk space low:**
- Warn when <1GB free
- Block recording when <500MB free

---

## Testing Checklist

- [ ] App appears in menu bar on launch
- [ ] App auto-starts on Mac login
- [ ] Google Calendar connects and shows upcoming meetings
- [ ] Recording auto-starts when meeting time begins
- [ ] Notification shows "Recording: [Meeting Name]"
- [ ] Recording captures system audio (test with YouTube)
- [ ] Recording captures mic audio
- [ ] Stop recording triggers transcription
- [ ] Transcript includes meeting metadata from calendar
- [ ] Transcript timestamps are accurate
- [ ] "Open Transcripts Folder" works
- [ ] Cancel recording deletes audio file
- [ ] App recovers gracefully from sleep/wake
- [ ] App handles no internet (calendar cached)

---

## Future Phases (not in scope now)

- Phase 2: Cloud sync of transcripts
- Phase 3: Extraction engine (tasks, decisions, blockers)
- Phase 4: Query interface
- Phase 5: Auto-actions (summaries, reminders)
- Phase 6: Speaker diarization + voice profiles

---

## Build Order

1. Basic menu bar app with states (no functionality)
2. Audio recording (manual start/stop)
3. Whisper transcription integration
4. Google Calendar OAuth + polling
5. Pre-meeting notifications
6. Meeting metadata in transcripts
7. LaunchAgent auto-start
8. First-run setup wizard
9. Polish + error handling
