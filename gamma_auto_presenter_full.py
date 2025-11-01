#!/usr/bin/env python3
"""
GAMMA Auto Presenter - Complete Workflow
Fully automated presentation system that synchronizes GAMMA slides with voiceover audio
"""

import os
import sys
import json

def print_header(title):
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70 + "\n")

def check_dependencies():
    """Check if all required packages are installed"""
    missing = []

    try:
        import pyautogui
    except ImportError:
        missing.append("pyautogui")

    try:
        import PIL
    except ImportError:
        missing.append("pillow")

    try:
        import pytesseract
    except ImportError:
        missing.append("pytesseract")

    try:
        import whisper
    except ImportError:
        missing.append("openai-whisper")

    try:
        import pygame
    except ImportError:
        missing.append("pygame")

    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nPlease install with:")
        print(f"   pip install {' '.join(missing)}")
        print("\n⚠️  Note: pytesseract also requires Tesseract OCR to be installed:")
        print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

    return True

def main():
    print_header("GAMMA AUTO PRESENTER - Complete System")

    print("This tool will create a fully automated GAMMA presentation")
    print("synchronized with your voiceover audio.\n")

    print("📋 What you need:")
    print("   1. GAMMA presentation URL")
    print("   2. Voiceover script (text file)")
    print("   3. Voiceover audio (WAV/MP3 file)\n")

    print("🔄 The process:")
    print("   Step 1: Analyze GAMMA presentation (capture slide content)")
    print("   Step 2: Transcribe audio (get word-level timestamps)")
    print("   Step 3: Match content (slides → script → audio)")
    print("   Step 4: Run automated presentation!\n")

    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return

    # Get user inputs
    print_header("STEP 0: Configuration")

    gamma_url = input("Enter GAMMA presentation URL: ").strip()
    if not gamma_url:
        gamma_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"
        print(f"   Using default: {gamma_url}")

    script_file = input("Enter path to script file (.txt): ").strip()
    if not script_file or not os.path.exists(script_file):
        print(f"   ❌ Script file not found: {script_file}")
        input("\nPress Enter to exit...")
        return

    audio_file = input("Enter path to audio file (.wav/.mp3): ").strip()
    if not audio_file or not os.path.exists(audio_file):
        print(f"   ❌ Audio file not found: {audio_file}")
        input("\nPress Enter to exit...")
        return

    # Create output directory
    output_dir = "gamma_presentation_output"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n✅ Configuration complete")
    print(f"   Output directory: {output_dir}\n")

    # Step 1: Analyze GAMMA
    print_header("STEP 1: Analyze GAMMA Presentation")
    print("We'll now analyze your GAMMA presentation to capture slide content.\n")
    input("Press Enter to start GAMMA analysis...")

    from gamma_analyzer import GammaAnalyzer
    analyzer = GammaAnalyzer(gamma_url, output_dir=os.path.join(output_dir, "gamma_analysis"))
    analyzer.analyze_presentation()
    gamma_analysis_file = analyzer.save_analysis()

    # Step 2: Transcribe audio
    print_header("STEP 2: Transcribe Audio")
    print("We'll now transcribe your audio file with word-level timestamps.\n")
    print("⚠️  This may take several minutes depending on audio length...\n")
    input("Press Enter to start transcription...")

    from audio_transcriber import AudioTranscriber
    transcriber = AudioTranscriber(audio_file, output_dir=os.path.join(output_dir, "audio_analysis"))
    transcriber.transcribe(model_size="base")
    transcription_file = transcriber.save_transcription()

    # Step 3: Match content
    print_header("STEP 3: Match Content")
    print("We'll now match GAMMA slides with your script and audio.\n")
    input("Press Enter to start matching...")

    from content_matcher import ContentMatcher
    matcher = ContentMatcher(gamma_analysis_file, script_file, transcription_file)
    matcher.load_data()
    matcher.generate_timeline()
    timeline_file = os.path.join(output_dir, "presentation_timeline.json")
    matcher.save_timeline(timeline_file)

    # Step 4: Run presentation
    print_header("STEP 4: Run Automated Presentation")
    print("Everything is ready! We can now run your automated presentation.\n")
    print("When you're ready:")
    print("   1. Open your GAMMA presentation in a browser")
    print("   2. Make sure the browser window is visible\n")

    choice = input("Run automated presentation now? (y/n): ").strip().lower()

    if choice == 'y':
        from automated_presenter import AutomatedPresenter
        presenter = AutomatedPresenter(timeline_file, audio_file)
        presenter.load_timeline()
        presenter.initialize_audio()
        presenter.run_presentation()
    else:
        print(f"\n✅ Setup complete!")
        print(f"\nTo run the presentation later, use:")
        print(f"   python automated_presenter.py {timeline_file} {audio_file}")

    print_header("COMPLETE")
    print("🎉 Your automated presentation system is ready!")
    print(f"\n📁 All files saved in: {output_dir}/")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")
