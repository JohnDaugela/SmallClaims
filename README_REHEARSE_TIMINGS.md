# GAMMA Rehearse Timings - User Guide

A PowerPoint-style "Rehearse Timings" feature for GAMMA presentations!

## What It Does

Record the timing of your spacebar presses while listening to your voiceover, then play back the presentation automatically with perfect timing.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python gamma_rehearse_timings.py
```

## How to Use

### Tab 1: Record Timings

**Setup:**
1. Click "Load Script (.txt)" - load your voiceover script text
2. Click "Load Audio (.wav/.mp3)" - load your audio file (from OmniVoice TTS)
3. Click "Transcribe Audio" - this takes ~1 minute, gets word-level timestamps
4. Wait for "Transcription complete!" message

**Recording:**
1. Open GAMMA presentation in fullscreen on your other monitor
2. In the app, click "▶ Start Recording"
3. Audio plays, script highlights word-by-word (karaoke style)
4. **Press SPACEBAR** every time you want to advance a slide
5. Watch the timeline - red markers show your spacebar presses
6. Click "⏹ Stop" when done

**Tips:**
- The script highlights the current word as audio plays
- You'll see a counter showing how many times you've pressed spacebar
- Timeline shows red markers for each press

### Tab 2: Review & Edit

**Adjust Timing:**
1. You'll see a visual timeline with all your spacebar markers
2. **Click and drag** any marker left/right to adjust timing by a few seconds
3. Click a marker to see:
   - Spacebar number (#1, #2, etc.)
   - Exact timestamp (MM:SS.mm)
   - Preview of words that come AFTER this spacebar press

**Preview Text:**
- The bottom text box shows "Words After This Spacebar Press"
- This helps you verify timing makes sense
- Shows ~30 words after each marker (even mid-sentence)

**Save/Load:**
- Click "💾 Save Timeline" to save your timing as JSON
- Click "📂 Load Timeline" to load a saved timeline
- Timelines are reusable - record once, play many times!

**Delete Markers:**
- Click a marker to select it
- Click "Delete Marker" to remove it
- Click "Refresh Timeline" to redraw

### Tab 3: Playback

**Automated Presentation:**
1. Open GAMMA in presentation mode on your other monitor
2. Click in the GAMMA window to give it focus
3. Set countdown (default 5 seconds)
4. Click "▶ Start Playback"
5. App will:
   - Count down (5... 4... 3... 2... 1...)
   - Start playing audio
   - Automatically press spacebar at your recorded times

**Status Display:**
- Shows countdown
- Shows when each spacebar press happens
- Shows timestamp for each press
- Shows "✅ PLAYBACK COMPLETE!" when done

## Two-Monitor Setup

**Recommended layout:**
- **Monitor 1:** GAMMA presentation (fullscreen, spotlight mode)
- **Monitor 2:** Rehearse Timings app

This way you can:
- See script highlighting while recording
- Adjust timeline while seeing slide previews
- Monitor playback status during automated presentation

## File Formats

**Script:** Plain text file (.txt)
- Your voiceover script
- Can be any text format

**Audio:** WAV or MP3 (.wav, .mp3)
- Generated from OmniVoice TTS
- Any audio with your voiceover

**Timeline:** JSON (.json)
- Saves your spacebar timestamps
- Includes audio file path and duration
- Reusable across sessions

Example timeline JSON:
```json
{
  "audio_file": "voiceover.wav",
  "audio_duration": 165.4,
  "spacebar_timestamps": [
    0.0,
    5.23,
    12.87,
    18.45
  ],
  "total_presses": 4
}
```

## Keyboard Shortcuts

**During Recording:**
- `SPACEBAR` - Mark slide change
- (Use mouse for Pause/Stop buttons)

**During Review:**
- Click and drag markers to adjust
- (All controls via mouse/GUI)

## Troubleshooting

**"Transcription failed"**
- Make sure Whisper is installed: `pip install openai-whisper`
- Make sure you loaded a valid audio file
- First transcription downloads the model (~200MB) - be patient

**"Playback doesn't press spacebar"**
- Make sure GAMMA window has focus (click in it before starting)
- Make sure you loaded a timeline (Tab 2)
- Check that spacebar timestamps exist

**"Script doesn't highlight words"**
- Make sure you transcribed the audio first
- Highlighting is approximate - based on word timestamps
- Works best with clear audio and matching script

**"Can't drag timeline markers"**
- Make sure you're in Tab 2 (Review & Edit)
- Click directly on the red circles
- Drag left/right to adjust

## Workflow Example

1. Write script in text editor → `script.txt`
2. Generate audio with OmniVoice TTS → `voiceover.wav`
3. Open `gamma_rehearse_timings.py`
4. Load script, load audio, transcribe
5. Open GAMMA in fullscreen on second monitor
6. Record: Press spacebar at slide changes while audio plays
7. Review: Drag markers to fine-tune timing
8. Save timeline → `presentation1_timing.json`
9. Playback: Automated presentation with perfect timing!
10. Reuse: Load same timeline for future runs

## Advanced Tips

**Multiple Takes:**
- Save different timeline versions: `take1.json`, `take2.json`, etc.
- Load and compare to find best timing

**Fine-Tuning:**
- Drag markers in small increments (~0.5-1 second adjustments)
- Use the preview text to verify timing makes sense
- Listen to audio at that timestamp to double-check

**Reusability:**
- Once you have a good timeline, save it
- Use for rehearsals, live presentations, recordings
- No need to re-record if audio doesn't change

**Screen Recording:**
- (Optional) Use OBS or other screen recorder during playback
- Captures automated presentation as video
- Great for sharing or uploading

## Support

For issues or questions, check the main repo or session link:
https://claude.ai/code/session_011CUgmrLHx2KBi1rEGdKMXX
