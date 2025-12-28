# Instructions for Claude Code

Copy and paste this into Claude Code running on your Mac:

---

## Setup & Test Chunk 1

I'm building a Meeting Recorder app. The code is in a GitHub repo. Please:

1. Clone the repo and checkout the feature branch:
   ```
   git clone https://github.com/johnbr0phy/yapyap.git
   cd yapyap
   git checkout claude/review-plan-markdown-kfRsq
   ```

2. Install dependencies:
   ```
   cd meeting-recorder
   pip3 install -r requirements.txt
   ```

3. Run the app:
   ```
   python3 app.py
   ```

4. Help me test:
   - Verify the ● icon appears in the menu bar
   - Click through the menu options
   - Test start/stop recording
   - Watch the timer count up
   - Test cancel recording
   - Test "Open Transcripts Folder"

5. If there are any errors, fix them.

---

## Project Context

- **Build spec:** `meeting-recorder-build-spec.md` - full requirements
- **Build plan:** `PLAN.md` - chunked implementation plan
- **Current progress:** Chunk 1 complete (menu bar shell)
- **Next:** Chunk 2 (audio recording with BlackHole + mic)

When Chunk 1 testing is complete, let me know and we'll proceed to Chunk 2.
