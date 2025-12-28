#!/usr/bin/env python3
"""
Meeting Recorder - Menu Bar App
A Mac menu bar app that records meetings and transcribes them locally.
"""

import rumps
import threading
import time
from enum import Enum
from config import ensure_directories, get_transcripts_dir


class AppState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"


class MeetingRecorderApp(rumps.App):
    """Main menu bar application."""

    # Icon characters for different states
    ICON_IDLE = "●"
    ICON_RECORDING = "◉"
    ICON_PROCESSING = "◐"

    def __init__(self):
        super().__init__(self.ICON_IDLE, quit_button=None)

        self.state = AppState.IDLE
        self.recording_start_time = None
        self.recording_meeting_name = None
        self._timer_thread = None
        self._stop_timer = False

        # Build the menu
        self._build_menu()

        # Ensure directories exist
        ensure_directories()

    def _build_menu(self):
        """Build the menu items."""
        self.menu.clear()

        if self.state == AppState.IDLE:
            self._build_idle_menu()
        elif self.state == AppState.RECORDING:
            self._build_recording_menu()
        elif self.state == AppState.PROCESSING:
            self._build_processing_menu()

    def _build_idle_menu(self):
        """Build menu for idle state."""
        # Next meeting placeholder
        self.next_meeting_item = rumps.MenuItem("Next: No upcoming meetings")
        self.next_meeting_item.set_callback(None)
        self.menu.add(self.next_meeting_item)

        self.menu.add(rumps.separator)

        # Actions
        self.start_recording_item = rumps.MenuItem(
            "Start Recording Manually",
            callback=self.start_recording
        )
        self.menu.add(self.start_recording_item)

        self.menu.add(rumps.separator)

        self.open_transcripts_item = rumps.MenuItem(
            "Open Transcripts Folder",
            callback=self.open_transcripts
        )
        self.menu.add(self.open_transcripts_item)

        self.menu.add(rumps.separator)

        self.quit_item = rumps.MenuItem("Quit", callback=self.quit_app)
        self.menu.add(self.quit_item)

    def _build_recording_menu(self):
        """Build menu for recording state."""
        self.stop_item = rumps.MenuItem(
            "Stop Recording",
            callback=self.stop_recording
        )
        self.menu.add(self.stop_item)

        self.cancel_item = rumps.MenuItem(
            "Cancel (discard audio)",
            callback=self.cancel_recording
        )
        self.menu.add(self.cancel_item)

    def _build_processing_menu(self):
        """Build menu for processing state."""
        processing_item = rumps.MenuItem("Transcribing... please wait")
        processing_item.set_callback(None)
        self.menu.add(processing_item)

    def _update_title(self):
        """Update the menu bar title based on state."""
        if self.state == AppState.IDLE:
            self.title = self.ICON_IDLE
        elif self.state == AppState.RECORDING:
            elapsed = self._get_elapsed_time()
            meeting_name = self.recording_meeting_name or "Manual Recording"
            # Truncate long meeting names
            if len(meeting_name) > 20:
                meeting_name = meeting_name[:17] + "..."
            self.title = f"{self.ICON_RECORDING} {meeting_name} ({elapsed})"
        elif self.state == AppState.PROCESSING:
            self.title = f"{self.ICON_PROCESSING} Transcribing..."

    def _get_elapsed_time(self) -> str:
        """Get elapsed recording time as MM:SS string."""
        if not self.recording_start_time:
            return "00:00"
        elapsed = int(time.time() - self.recording_start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _start_timer(self):
        """Start the timer update thread."""
        self._stop_timer = False

        def update_timer():
            while not self._stop_timer:
                if self.state == AppState.RECORDING:
                    self._update_title()
                time.sleep(1)

        self._timer_thread = threading.Thread(target=update_timer, daemon=True)
        self._timer_thread.start()

    def _stop_timer_thread(self):
        """Stop the timer update thread."""
        self._stop_timer = True
        if self._timer_thread:
            self._timer_thread.join(timeout=2)
            self._timer_thread = None

    def _set_state(self, new_state: AppState):
        """Change app state and update UI."""
        self.state = new_state
        self._build_menu()
        self._update_title()

    # --- Menu Actions ---

    def start_recording(self, sender=None, meeting_name=None):
        """Start a new recording."""
        if self.state != AppState.IDLE:
            return

        self.recording_meeting_name = meeting_name
        self.recording_start_time = time.time()

        self._set_state(AppState.RECORDING)
        self._start_timer()

        print(f"Recording started: {self.recording_meeting_name or 'Manual Recording'}")

        # TODO: Actually start audio recording (Chunk 2)

    def stop_recording(self, sender=None):
        """Stop recording and begin transcription."""
        if self.state != AppState.RECORDING:
            return

        self._stop_timer_thread()

        elapsed = self._get_elapsed_time()
        print(f"Recording stopped after {elapsed}")

        # Simulate processing
        self._set_state(AppState.PROCESSING)

        # TODO: Actually stop recording and transcribe (Chunks 2 & 3)
        # For now, simulate with a short delay
        def simulate_processing():
            time.sleep(2)  # Simulate transcription
            self._set_state(AppState.IDLE)
            self.recording_start_time = None
            self.recording_meeting_name = None
            print("Transcription complete (simulated)")

        thread = threading.Thread(target=simulate_processing, daemon=True)
        thread.start()

    def cancel_recording(self, sender=None):
        """Cancel recording and discard audio."""
        if self.state != AppState.RECORDING:
            return

        self._stop_timer_thread()

        print("Recording cancelled - audio discarded")

        # TODO: Delete audio file (Chunk 2)

        self.recording_start_time = None
        self.recording_meeting_name = None
        self._set_state(AppState.IDLE)

    def open_transcripts(self, sender=None):
        """Open the transcripts folder in Finder."""
        import subprocess
        transcripts_dir = get_transcripts_dir()
        transcripts_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["open", str(transcripts_dir)])

    def quit_app(self, sender=None):
        """Quit the application."""
        self._stop_timer_thread()
        rumps.quit_application()


def main():
    """Entry point."""
    print("Starting Meeting Recorder...")
    print("Look for the ● icon in your menu bar")
    app = MeetingRecorderApp()
    app.run()


if __name__ == "__main__":
    main()
