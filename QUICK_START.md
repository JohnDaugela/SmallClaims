# GAMMA Auto Presenter - Quick Start Guide

## For Non-Developers

### What You Need
1. Your GAMMA presentation URL
2. Your script (text file you read from)
3. Your voiceover recording (WAV or MP3 file)

### One-Time Setup (5 minutes)

**Step 1: Install Python packages**
```bash
pip install pyautogui pillow pytesseract openai-whisper pygame torch numpy
```

**Step 2: Install Tesseract OCR**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- During installation, CHECK "Add to PATH"
- Restart your computer

### Running the System

**Option A: Complete Automation (Easiest)**
1. Double-click `gamma_auto_presenter_full.py`
2. Follow the prompts
3. Wait for analysis (may take 5-10 minutes total)
4. Run your automated presentation!

**Option B: Test the Basic Version First**
1. Double-click `GAMMA_Auto_Presenter.py`
2. This just clicks through at regular intervals
3. Good for testing before running full analysis

### What Each File Does

| File | Purpose |
|------|---------|
| `GAMMA_Auto_Presenter.py` | Simple version - just clicks every 3 seconds |
| `gamma_auto_presenter_full.py` | **Main file** - Complete automated system |
| `gamma_analyzer.py` | Analyzes GAMMA slides (auto-run by main file) |
| `audio_transcriber.py` | Transcribes audio (auto-run by main file) |
| `content_matcher.py` | Matches slides to audio (auto-run by main file) |
| `automated_presenter.py` | Runs the presentation (auto-run by main file) |

### Expected Timeline

1. **Setup** (one-time): 5-10 minutes
2. **GAMMA Analysis**: 30 seconds per presentation
3. **Audio Transcription**: 1-5 minutes depending on length
4. **Content Matching**: 10 seconds
5. **Running Presentation**: Same as audio duration

### Folder to Save Everything

Save all files to:
```
F:\Dropbox\JohnDarcy (1)\2025\Small Claims Academy\Lessons_Generated\0_RUN_AUTOMATION\Claude
```

### Getting Help

If something doesn't work:
1. Check that Tesseract is installed and in PATH
2. Make sure all pip packages installed successfully
3. Try the simple `GAMMA_Auto_Presenter.py` first
4. Check error messages for missing dependencies

### What the Output Looks Like

After running, you'll have a folder structure like:
```
gamma_presentation_output/
├── gamma_analysis/           (Screenshots and slide data)
├── audio_analysis/           (Transcription with timestamps)
└── presentation_timeline.json (Final timing for automation)
```

You can review these files to see what the system detected!

## Next Steps

Once you've run the full system once:
- You can reuse it for different presentations
- Just run `gamma_auto_presenter_full.py` again with new files
- System automatically detects slide counts and timings
- No manual configuration needed!

## Pro Tip

Before running the full analysis:
1. Manually click through your GAMMA presentation once
2. Count the slides (e.g., 17 slides)
3. This helps you verify the system found everything correctly
