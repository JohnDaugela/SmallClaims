# GAMMA Auto Presenter - Complete Automated System

This system creates fully automated GAMMA.app presentations synchronized with voiceover audio. No manual timing needed - the system analyzes everything automatically!

## What It Does

Given:
- Your GAMMA presentation URL
- Your voiceover script (text)
- Your voiceover audio file

The system will:
1. **Analyze GAMMA** - Automatically discover slide structure and content
2. **Transcribe Audio** - Get precise word-level timestamps using AI
3. **Match Content** - Intelligently match slides → script → audio timing
4. **Execute** - Run the presentation with perfect synchronization!

## System Requirements

### Software
- **Python 3.8+**
- **Tesseract OCR** (for reading slide content)
  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - Add to PATH during installation

### Python Packages
```bash
pip install -r requirements.txt
```

Required packages:
- `pyautogui` - Keyboard/mouse automation
- `pillow` - Image processing
- `pytesseract` - OCR for slide text extraction
- `openai-whisper` - AI speech-to-text
- `pygame` - Audio playback
- `torch` - Machine learning backend for Whisper
- `numpy` - Numerical computing

## Complete Workflow

### Option 1: All-in-One Script (Recommended)

Run the complete workflow in one go:

```bash
python gamma_auto_presenter_full.py
```

This will guide you through:
1. Entering your GAMMA URL
2. Selecting your script file
3. Selecting your audio file
4. Analyzing the presentation
5. Transcribing the audio
6. Matching everything together
7. Running the automated presentation

### Option 2: Step-by-Step (Advanced)

#### Step 1: Analyze GAMMA Presentation

```bash
python gamma_analyzer.py
```

This will:
- Open your GAMMA presentation (you do this manually)
- Automatically click through and capture each slide
- Extract text from slides using OCR
- Detect when the presentation ends (no more changes)
- Save analysis to `gamma_analysis/presentation_analysis.json`

**Output:**
- `gamma_analysis/presentation_analysis.json` - Slide data
- `gamma_analysis/slide_01.png`, `slide_02.png`, etc. - Screenshots

#### Step 2: Transcribe Audio

```bash
python audio_transcriber.py your_voiceover.wav
```

This will:
- Load your audio file
- Use Whisper AI to transcribe with word-level timestamps
- Save transcription data

**Output:**
- `audio_analysis/transcription.json` - Full data with timestamps
- `audio_analysis/transcription.txt` - Plain text
- `audio_analysis/transcription_timestamped.txt` - Readable timestamped version

#### Step 3: Match Content

```bash
python content_matcher.py gamma_analysis/presentation_analysis.json script.txt audio_analysis/transcription.json
```

This will:
- Load GAMMA slide content
- Load your script
- Load audio transcription
- Use fuzzy matching to find where each slide's content appears in your script
- Find when those words are spoken in the audio
- Generate precise timeline for spacebar presses

**Output:**
- `presentation_timeline.json` - Complete timeline with all timings

#### Step 4: Run Automated Presentation

```bash
python automated_presenter.py presentation_timeline.json your_voiceover.wav
```

This will:
- Load the timeline
- Wait for you to open and focus on GAMMA browser
- Enter presentation mode (Ctrl+Shift+Enter)
- Enter spotlight mode (S)
- Play audio and automatically press spacebar at exact timestamps

## File Structure

After running the complete workflow, you'll have:

```
gamma_presentation_output/
├── gamma_analysis/
│   ├── presentation_analysis.json    # Slide structure data
│   ├── slide_01.png                  # Screenshot of slide 1
│   ├── slide_02.png                  # Screenshot of slide 2
│   └── ...
├── audio_analysis/
│   ├── transcription.json            # Word-level timestamps
│   ├── transcription.txt             # Plain text transcription
│   └── transcription_timestamped.txt # Human-readable timestamps
└── presentation_timeline.json         # Final timeline for execution
```

## How It Works

### 1. GAMMA Analysis
- Opens presentation in browser
- Takes screenshot, presses spacebar, takes another screenshot
- Compares images - if no change, we've reached the end
- Extracts text from each slide using OCR
- Handles variable presentation lengths automatically

### 2. Audio Transcription
- Uses OpenAI's Whisper model for speech-to-text
- Gets word-level timestamps (accurate to ~0.1 seconds)
- Works with WAV, MP3, and other audio formats

### 3. Content Matching
- Extracts key phrases from each slide
- Fuzzy matches slide text to script
- Finds when those words are spoken in audio
- Handles variations in wording/punctuation
- Generates timeline: "At 12.3 seconds, press spacebar for slide 2"

### 4. Execution
- Plays audio file
- Monitors playback time
- Presses spacebar at precise moments
- Fully unattended operation

## Tips for Best Results

### Script File
- Should be the actual text you read during recording
- Doesn't need to be word-perfect, but close
- Plain text file (.txt)

### Audio File
- WAV or MP3 format
- Clear speech (minimal background noise)
- Consistent volume

### GAMMA Presentation
- Use spotlight mode for best visual effect
- Test manually first to know the slide count
- Make sure slide content has readable text

### Matching Quality
- The system shows similarity scores for matches
- 1.0 = perfect match, 0.6+ = acceptable
- Low scores may indicate script doesn't match audio/slides
- Review `presentation_timeline.json` to verify matches

## Troubleshooting

### "Tesseract not found"
- Install Tesseract OCR
- Add to PATH
- Restart terminal/command prompt

### "Cannot match slide to script"
- Check that script matches what's actually on slides
- Try simplifying slide text
- Manually verify slide screenshots in output folder

### "Audio transcription failed"
- Check audio file format (WAV/MP3)
- Ensure file isn't corrupted
- Try a smaller audio file first (under 5 minutes)

### "Spacebar presses don't align"
- Review timeline in `presentation_timeline.json`
- Check that matched text makes sense
- Script might not match audio recording

### "Presentation doesn't advance"
- Ensure GAMMA browser window is focused
- Check that presentation mode is active
- Verify keyboard shortcuts work manually

## Example Usage

```bash
# Complete workflow
python gamma_auto_presenter_full.py

# Or step by step:
python gamma_analyzer.py
python audio_transcriber.py voiceover.wav
python content_matcher.py gamma_analysis/presentation_analysis.json script.txt audio_analysis/transcription.json
python automated_presenter.py presentation_timeline.json voiceover.wav
```

## Reusing With Different Presentations

The system works with ANY GAMMA presentation:
- Different slide counts (automatically detected)
- Different content
- Different audio lengths
- Different scripts

Just run the workflow again with new files!

## Performance

- **GAMMA Analysis**: ~10-30 seconds (depends on slide count)
- **Audio Transcription**: ~1-5 minutes (depends on audio length)
- **Content Matching**: ~5-10 seconds
- **Execution**: Real-time (same as audio duration)

## License

Free to use for your presentations!
