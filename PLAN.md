# Meeting Recorder - Build Plan

## Chunk 1: Menu Bar App Shell
**Goal:** A clickable menu bar app with visual states

**Deliverables:**
- `app.py` - Menu bar app using `rumps`
- `config.py` - Basic configuration
- `requirements.txt` - Dependencies

**Features:**
- App appears in menu bar with icon
- Click shows menu with placeholder items:
  - "Next: No upcoming meetings"
  - "Start Recording Manually"
  - "Open Transcripts Folder"
  - "Quit"
- Icon changes between states (idle ● / recording ◉ / processing ◐)
- Timer display when "recording" (simulated)

**You Can Test:**
- Run `python app.py`
- See app in menu bar
- Click through menu items
- Trigger fake recording state, watch icon/timer change
- Quit from menu

---

## Chunk 2: Audio Recording
**Goal:** Actually capture audio from mic and BlackHole

**Deliverables:**
- `recorder.py` - Audio capture module

**Features:**
- List available audio devices
- Capture from BlackHole (system audio)
- Capture from default mic
- Mix into single WAV file (16kHz)
- Start/stop recording from menu bar
- Show recording duration in real-time
- Save to `recordings/` folder

**You Can Test:**
- Start recording from menu
- Play music/YouTube - verify system audio captured
- Speak into mic - verify voice captured
- Stop recording, find WAV file
- Play WAV file to confirm both sources recorded
- Cancel recording, verify file deleted

**Prerequisites:**
- BlackHole 2ch installed
- Multi-Output Device configured in Audio MIDI Setup

---

## Chunk 3: Local Transcription
**Goal:** Transcribe recordings with Whisper

**Deliverables:**
- `transcriber.py` - Whisper transcription module

**Features:**
- Download/load `small` Whisper model on first use
- Transcribe WAV files locally
- Show "Transcribing..." state in menu bar
- Generate timestamped transcript
- Save to `transcripts/` folder
- Clean up raw audio after success

**You Can Test:**
- Record a 1-2 minute clip with talking
- Stop recording, watch transcription begin
- Menu bar shows processing state
- Transcript file appears with timestamps
- Verify transcript accuracy

**Output Format:**
```
Recording: 2024-12-28_manual_recording.txt
Date: 2024-12-28 3:45 PM
Duration: 2 minutes

---

[00:00] Hello, this is a test recording.
[00:05] I'm checking if the transcription works.
...
```

---

## Chunk 4: Google Calendar Integration
**Goal:** Connect to Google Calendar, show upcoming meetings

**Deliverables:**
- `calendar_sync.py` - OAuth + calendar polling
- Google Cloud project setup instructions

**Features:**
- OAuth flow (opens browser for login)
- Store refresh token in macOS Keychain
- Poll calendar every 5 minutes
- Detect meetings with video links (Meet, Zoom, Teams)
- Show next meeting in menu bar
- Cache today's meetings locally

**You Can Test:**
- Run app, trigger OAuth flow
- Authorize with your Google account
- See your real upcoming meetings in menu
- "Next: Meeting Name (2:30 PM)" shows correctly
- Restart app - still authenticated (no re-login)

**Menu Updates:**
```
[●] Meeting Recorder
    ├── Next: Q4 Planning (2:30 PM)
    ├── Later: 1:1 with Sarah (4:00 PM)
    ├── ──────────────────
    ├── Start Recording Manually
    ...
```

---

## Chunk 5: Auto-Recording + Meeting Metadata
**Goal:** Auto-start recording when meetings begin, enrich transcripts

**Deliverables:**
- Meeting scheduler logic in `app.py`
- Enhanced transcript formatting

**Features:**
- Auto-start recording at meeting start time
- Notification: "Recording: [Meeting Name]"
- Pull attendees, description from calendar event
- Include meeting metadata in transcript header
- Stop recording manually (meetings run over)
- Cancel option (discards if you skip meeting)

**You Can Test:**
- Create a test meeting in Google Calendar (starting in 1 min)
- Add a Meet/Zoom link to it
- Watch app auto-start recording
- See notification appear
- Stop recording, verify transcript has:
  - Meeting title
  - Attendees list
  - Date/time
  - Full transcription

**Transcript Format:**
```
Meeting: Q4 Planning Sync
Date: 2024-12-28 2:30 PM
Duration: 47 minutes
Attendees: John, Sarah Chen, Mike Torres

---

[00:00] Let's start with the API update.
...
```

---

## Chunk 6: Notifications + Polish
**Goal:** Native macOS notifications, better UX

**Deliverables:**
- `notifier.py` - Notification system
- Error handling improvements

**Features:**
- Recording started notification
- Transcript ready notification (click to open file)
- Error notifications (BlackHole missing, auth expired)
- Disk space warnings
- Graceful handling of sleep/wake
- Transcription retry on failure

**You Can Test:**
- Start recording → see notification
- Complete transcription → see "Transcript ready" notification
- Click notification → opens transcript
- Unplug BlackHole → see helpful error notification
- Fill disk → see warning before it's too late

---

## Chunk 7: Auto-Start + Setup Wizard
**Goal:** App runs on login, easy first-time setup

**Deliverables:**
- `setup.py` - First-run wizard
- `launch/com.meetingrecorder.plist` - LaunchAgent

**Features:**
- Setup wizard walks through:
  1. Check BlackHole installed
  2. Guide Multi-Output Device creation
  3. Google OAuth
  4. Download Whisper model (progress bar)
  5. Test recording (5 seconds)
  6. Install LaunchAgent
- App auto-starts on Mac login
- App stays running (restarts if crashed)

**You Can Test:**
- Delete config, run app → wizard appears
- Walk through each setup step
- Reboot Mac → app auto-starts
- Force-quit app → auto-restarts
- `launchctl list | grep meetingrecorder` shows it running

---

## Summary

| Chunk | What You Get | Time Est. |
|-------|--------------|-----------|
| 1 | Clickable menu bar app | - |
| 2 | Working audio recording | - |
| 3 | Local transcription | - |
| 4 | Google Calendar in menu | - |
| 5 | Auto-record meetings | - |
| 6 | Notifications + polish | - |
| 7 | Auto-start + setup wizard | - |

---

## Ready to Start?

When you give the thumbs up, I'll begin with **Chunk 1: Menu Bar App Shell**.
